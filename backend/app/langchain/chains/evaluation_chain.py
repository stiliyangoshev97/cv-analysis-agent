"""
CV Evaluation Chain

LangChain chain for evaluating CVs against criteria with structured output.
Uses Claude to analyze CV text and return Pydantic-validated scores.
"""

from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from pydantic import BaseModel, Field

from app.langchain.config import get_llm


class CriterionScore(BaseModel):
    """Score for a single evaluation criterion.
    
    Attributes:
        name: Name of the criterion (e.g., "Technical Skills").
        score: Points awarded (0 to max_score).
        max_score: Maximum possible points.
        reasoning: Explanation for the score.
        evidence: Specific quotes/evidence from the CV.
    """
    name: str = Field(description="Name of the criterion being evaluated")
    score: int = Field(description="Points awarded for this criterion", ge=0)
    max_score: int = Field(description="Maximum possible points", ge=0)
    reasoning: str = Field(description="Detailed explanation for the score")
    evidence: list[str] = Field(
        default_factory=list,
        description="Specific quotes or evidence from the CV supporting this score"
    )


class CVEvaluationResult(BaseModel):
    """Complete CV evaluation result.
    
    Attributes:
        criteria_scores: List of scores for each criterion.
        total_score: Sum of all criterion scores.
        max_total_score: Maximum possible total score.
        percentage: Score as percentage (0-100).
        passed: Whether the CV meets passing threshold.
        summary: Brief overall assessment.
        strengths: Key strengths identified.
        weaknesses: Areas for improvement.
        recommendation: Final hiring recommendation.
    """
    criteria_scores: list[CriterionScore] = Field(
        description="Scores for each evaluation criterion"
    )
    total_score: int = Field(description="Sum of all criterion scores", ge=0)
    max_total_score: int = Field(description="Maximum possible total score", ge=0)
    percentage: float = Field(description="Score as percentage (0-100)", ge=0, le=100)
    passed: bool = Field(description="Whether the CV meets the passing threshold")
    summary: str = Field(description="Brief overall assessment of the candidate")
    strengths: list[str] = Field(
        default_factory=list,
        description="Key strengths identified in the CV"
    )
    weaknesses: list[str] = Field(
        default_factory=list,
        description="Areas for improvement or missing qualifications"
    )
    recommendation: str = Field(
        description="Final hiring recommendation (Strong Yes / Yes / Maybe / No / Strong No)"
    )


# System prompt for CV evaluation
EVALUATION_SYSTEM_PROMPT = """You are an expert CV/resume evaluator for a hiring team.

Your task is to objectively evaluate a candidate's CV against specific criteria.
Be thorough, fair, and provide evidence-based scoring.

**Evaluation Guidelines:**
1. Read the entire CV carefully before scoring
2. Score each criterion independently based on evidence in the CV
3. Provide specific quotes or examples as evidence
4. Be consistent - similar qualifications should receive similar scores
5. Consider both explicit statements and reasonable inferences
6. When information is missing, note it as a weakness

**Scoring Philosophy:**
- 0-20% of max: No evidence of this skill/experience
- 21-40% of max: Minimal evidence, far below requirements
- 41-60% of max: Some evidence, partially meets requirements
- 61-80% of max: Good evidence, meets requirements
- 81-100% of max: Strong evidence, exceeds requirements

{format_instructions}"""

EVALUATION_HUMAN_PROMPT = """## Evaluation Template: {template_name}
{template_description}

## Passing Criteria
- Passing Score: {passing_score}%
- Minimum Criteria to Meet: {minimum_criteria_met}

## Criteria to Evaluate

{criteria_description}

---

## Candidate CV

{cv_text}

---

Please evaluate this CV against each criterion and provide a comprehensive assessment."""


class EvaluationChain:
    """
    Chain for evaluating CVs against criteria.
    
    Uses Claude to analyze CV text and produce structured evaluation results
    that match the Pydantic schema for database storage.
    
    Example:
        ```python
        chain = EvaluationChain()
        
        criteria = [
            {"name": "Technical Skills", "max_points": 30, "description": "..."},
            {"name": "Experience", "max_points": 25, "description": "..."},
        ]
        
        result = await chain.evaluate(
            cv_text=cv_content,
            template_name="AI-First Fintech",
            template_description="Screening for fintech startup",
            criteria=criteria,
            passing_score=60,
            minimum_criteria_met=3,
        )
        
        print(f"Score: {result.percentage}%")
        print(f"Passed: {result.passed}")
        for score in result.criteria_scores:
            print(f"  {score.name}: {score.score}/{score.max_score}")
        ```
    """
    
    def __init__(
        self,
        llm: ChatAnthropic | None = None,
        temperature: float = 0.0,
    ):
        """
        Initialize the evaluation chain.
        
        Args:
            llm: Optional pre-configured LLM instance.
            temperature: Temperature for generation (0.0 for consistent scoring).
        """
        self.llm = llm or get_llm(temperature=temperature)
        self.parser = PydanticOutputParser(pydantic_object=CVEvaluationResult)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", EVALUATION_SYSTEM_PROMPT),
            ("human", EVALUATION_HUMAN_PROMPT),
        ])
        
        # Build the chain
        self.chain: RunnableSequence = self.prompt | self.llm | self.parser
    
    def _format_criteria(self, criteria: list[dict[str, Any]]) -> str:
        """Format criteria list into prompt text."""
        lines = []
        for i, criterion in enumerate(criteria, 1):
            name = criterion.get("name", f"Criterion {i}")
            max_points = criterion.get("max_points", 10)
            description = criterion.get("description", "")
            is_required = criterion.get("is_required", False)
            
            required_tag = " [REQUIRED]" if is_required else ""
            lines.append(f"### {i}. {name}{required_tag}")
            lines.append(f"**Max Points:** {max_points}")
            if description:
                lines.append(f"**Description:** {description}")
            lines.append("")
        
        return "\n".join(lines)
    
    async def evaluate(
        self,
        cv_text: str,
        template_name: str,
        template_description: str,
        criteria: list[dict[str, Any]],
        passing_score: int = 60,
        minimum_criteria_met: int = 0,
    ) -> CVEvaluationResult:
        """
        Evaluate a CV against criteria.
        
        Args:
            cv_text: Full text content of the CV.
            template_name: Name of the evaluation template.
            template_description: Description of what we're screening for.
            criteria: List of criterion dicts with name, max_points, description.
            passing_score: Minimum percentage to pass.
            minimum_criteria_met: Minimum number of criteria to meet.
        
        Returns:
            CVEvaluationResult with scores, summary, and recommendation.
        
        Raises:
            ValueError: If cv_text is empty.
            ValidationError: If LLM output doesn't match schema.
        """
        if not cv_text or not cv_text.strip():
            raise ValueError("CV text cannot be empty")
        
        if not criteria:
            raise ValueError("At least one criterion is required")
        
        criteria_description = self._format_criteria(criteria)
        
        result = await self.chain.ainvoke({
            "template_name": template_name,
            "template_description": template_description or "General CV screening",
            "criteria_description": criteria_description,
            "passing_score": passing_score,
            "minimum_criteria_met": minimum_criteria_met,
            "cv_text": cv_text,
            "format_instructions": self.parser.get_format_instructions(),
        })
        
        return result
    
    async def evaluate_with_template(
        self,
        cv_text: str,
        template: Any,  # EvaluationTemplate from database
        criteria_list: list[Any],  # List of TemplateCriterion from database
    ) -> CVEvaluationResult:
        """
        Evaluate a CV using a database template and criteria.
        
        Convenience method that extracts needed fields from database models.
        
        Args:
            cv_text: Full text content of the CV.
            template: EvaluationTemplate database model.
            criteria_list: List of TemplateCriterion database models.
        
        Returns:
            CVEvaluationResult with scores, summary, and recommendation.
        """
        criteria = [
            {
                "name": c.name,
                "max_points": c.max_points,
                "description": c.description,
                "is_required": c.is_required,
            }
            for c in criteria_list
        ]
        
        return await self.evaluate(
            cv_text=cv_text,
            template_name=template.name,
            template_description=template.description or "",
            criteria=criteria,
            passing_score=template.passing_score,
            minimum_criteria_met=template.minimum_criteria_met,
        )


# Singleton instance for convenience
_evaluation_chain: EvaluationChain | None = None


def get_evaluation_chain() -> EvaluationChain:
    """Get or create the evaluation chain singleton."""
    global _evaluation_chain
    if _evaluation_chain is None:
        _evaluation_chain = EvaluationChain()
    return _evaluation_chain
