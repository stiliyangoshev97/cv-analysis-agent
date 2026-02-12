"""CV Evaluation Service using Claude AI.

This module provides AI-powered CV/resume evaluation using Anthropic's
Claude model. It analyzes CV content against predefined criteria and
returns a structured assessment with pass/fail status and detailed scoring.

The evaluation assesses candidates based on:
    - Education level (High School Diploma minimum)
    - Fintech/Finance industry experience
    - Technical skills (TypeScript/Python proficiency)
    - Soft skills (fast learner, stress handling, team player)
    - AI-Native Development (AI tools, RAG, MCP, agents)

Classes:
    EvaluationService: Main service class for CV evaluation.

Example:
    Evaluating a CV::
    
        service = EvaluationService()
        result = service.evaluate_cv(
            cv_text="John Doe\\nSoftware Engineer at Coinbase...",
            filename="john_doe_cv.pdf"
        )
        print(f"Status: {result.status}, Score: {result.match_score}")

Note:
    Requires ANTHROPIC_API_KEY environment variable to be set.
    Uses Claude Sonnet 4 model by default (configurable via CLAUDE_MODEL).
"""

import json
import logging
from anthropic import Anthropic

from ....config import get_settings
from ..cv_schemas import CVEvaluationResponse, EvaluationCriteria, PassFailStatus

logger = logging.getLogger(__name__)

# System prompt for CV evaluation
CV_EVALUATION_SYSTEM_PROMPT = """You are an expert HR screening agent for a modern AI-first fintech company. 
Your task is to evaluate CV/resume content and provide a structured assessment.

You MUST evaluate candidates based on these FIVE criteria:

1. **Education**: Does the candidate have at least a High School Diploma (or equivalent/higher)?
   - Look for: High School, GED, Associate's, Bachelor's, Master's, PhD, or equivalent certifications
   - Also consider: Bootcamps, online courses, self-taught with portfolio evidence
   
2. **Fintech Fit**: Does the candidate have relevant experience in Finance, Banking, Cryptocurrency, or Fintech?
   - Look for: Experience at financial institutions, crypto exchanges, trading platforms, payment companies
   - Also consider: Blockchain experience, DeFi, traditional finance roles, fintech startups
   
3. **Technical Skills**: Does the candidate have proficiency in TypeScript OR Python?
   - Look for: Direct mentions of TypeScript, Python, JavaScript (close to TypeScript), or related frameworks
   - Consider: React, Node.js, FastAPI, Django, Flask, Next.js as indicators of these skills

4. **Soft Skills & Adaptability**: Does the candidate demonstrate key soft skills for modern tech environments?
   - Fast Learner: Evidence of quickly picking up new technologies, frameworks, or domains
   - Work Under Pressure: Experience with deadlines, high-stakes projects, startup environments, on-call rotations
   - Team Player: Collaboration, cross-functional work, mentoring, pair programming, code reviews
   - Adaptability: Career pivots, learning new stacks, working across different domains
   
5. **AI-Native Development**: Does the candidate embrace AI-assisted development and modern AI tools?
   - AI Coding Tools: Uses Claude Code, GitHub Copilot, Cursor, Windsurf, Cody, or similar AI assistants
   - Vibe Coding: Comfortable with AI pair programming, prompt engineering for code generation
   - RAG Systems: Understanding of Retrieval-Augmented Generation, vector databases, embeddings
   - MCP (Model Context Protocol): Familiarity with tool-use, function calling, agent protocols
   - AI Agent Development: Experience building or working with AI agents, LangChain, LlamaIndex
   - LLM Integration: Working with OpenAI, Anthropic, or other LLM APIs in production

SCORING GUIDELINES:
- Education: 15 points max
- Fintech Fit: 20 points max
- Technical Skills: 25 points max
- Soft Skills & Adaptability: 20 points max
- AI-Native Development: 20 points max
- Bonus points for exceptional qualifications in any category
- Score 0-100 overall

PASS/FAIL LOGIC:
- PASS: Score >= 60 AND at least 3 out of 5 criteria are met (must include Technical Skills)
- FAIL: Score < 60 OR fewer than 3 criteria met OR Technical Skills not met

IMPORTANT FOR AI-NATIVE CRITERIA:
- This is a modern requirement - many excellent candidates may not explicitly list AI tools
- Look for indirect evidence: mentions of productivity tools, modern workflows, recent projects
- If a candidate shows strong technical skills + adaptability, they likely can adopt AI tools
- Weight this criterion appropriately - it's a bonus for candidates who explicitly mention it

You MUST respond with ONLY valid JSON in this exact format:
{
    "status": "pass" or "fail",
    "match_score": <number 0-100>,
    "reasoning": "<detailed paragraph explaining your evaluation>",
    "criteria": [
        {
            "name": "Education",
            "passed": true/false,
            "details": "<specific details found or reason for failure>"
        },
        {
            "name": "Fintech Experience",
            "passed": true/false,
            "details": "<specific details found or reason for failure>"
        },
        {
            "name": "Technical Skills",
            "passed": true/false,
            "details": "<specific skills found or reason for failure>"
        },
        {
            "name": "Soft Skills & Adaptability",
            "passed": true/false,
            "details": "<evidence of fast learning, stress handling, teamwork>"
        },
        {
            "name": "AI-Native Development",
            "passed": true/false,
            "details": "<AI tools, RAG, MCP, agents experience or potential>"
        }
    ],
    "candidate_name": "<extracted name or null if not found>"
}

Be fair but thorough. If information is missing or unclear, note it in your evaluation.
For AI-Native Development, be generous if the candidate shows strong technical aptitude and modern practices."""


class EvaluationService:
    """Service for evaluating CV content using Claude AI.
    
    Provides AI-powered CV analysis with structured output including
    pass/fail status, numeric score, and detailed criteria breakdown.
    
    Attributes:
        settings: Application settings containing API keys and model config.
        client: Anthropic API client instance.
    
    Example:
        >>> service = EvaluationService()
        >>> result = service.evaluate_cv(cv_text, "resume.pdf")
        >>> if result.status == "pass":
        ...     print(f"Candidate passed with {result.match_score}%")
    
    Note:
        The evaluation prompt is tailored for fintech company requirements.
        Modify CV_EVALUATION_SYSTEM_PROMPT to customize criteria.
    """
    
    def __init__(self) -> None:
        """Initialize the evaluation service with Anthropic client.
        
        Loads settings from environment and creates the API client.
        
        Raises:
            ValueError: If ANTHROPIC_API_KEY is not configured.
        """
        self.settings = get_settings()
        self.client = Anthropic(api_key=self.settings.anthropic_api_key)
        
    def evaluate_cv(self, cv_text: str, filename: str) -> CVEvaluationResponse:
        """Evaluate CV content using Claude AI.
        
        Sends the CV text to Claude with a structured prompt and parses
        the JSON response into a CVEvaluationResponse model.
        
        Args:
            cv_text: Extracted text content from the CV/resume PDF.
            filename: Original filename for logging and context.
        
        Returns:
            CVEvaluationResponse containing:
                - status: "pass" or "fail"
                - match_score: 0-100 numeric score
                - reasoning: Detailed explanation
                - criteria: List of evaluated criteria with pass/fail
                - candidate_name: Extracted name (if found)
        
        Raises:
            ValueError: If evaluation fails due to:
                - API error
                - Invalid JSON response from Claude
                - Missing required fields in response
        
        Example:
            >>> service = EvaluationService()
            >>> result = service.evaluate_cv(
            ...     cv_text="Jane Smith\\nSenior Python Developer...",
            ...     filename="jane_smith_cv.pdf"
            ... )
            >>> print(result.match_score)  # 85
            >>> print(result.criteria[0].name)  # "Education"
        """
        try:
            # Prepare the user message
            user_message = f"""Please evaluate the following CV/Resume:

Filename: {filename}

--- CV CONTENT START ---
{cv_text}
--- CV CONTENT END ---

Provide your structured evaluation as JSON."""

            logger.info(f"Sending CV for evaluation: {filename}")
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.settings.claude_model,
                max_tokens=2048,
                system=CV_EVALUATION_SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Extract the response text
            response_text = response.content[0].text
            logger.debug(f"Raw Claude response: {response_text}")
            
            # Parse the JSON response
            evaluation_data = self._parse_evaluation_response(response_text)
            
            # Construct the response model
            return CVEvaluationResponse(
                status=PassFailStatus(evaluation_data["status"]),
                match_score=evaluation_data["match_score"],
                reasoning=evaluation_data["reasoning"],
                criteria=[
                    EvaluationCriteria(**criterion) 
                    for criterion in evaluation_data["criteria"]
                ],
                candidate_name=evaluation_data.get("candidate_name")
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            raise ValueError("AI returned invalid response format")
        except KeyError as e:
            logger.error(f"Missing required field in AI response: {e}")
            raise ValueError(f"AI response missing required field: {e}")
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            raise ValueError(f"Failed to evaluate CV: {e}")
    
    def _parse_evaluation_response(self, response_text: str) -> dict:
        """Parse Claude response text to extract JSON.
        
        Handles cases where JSON might be wrapped in markdown code blocks
        (```json ... ```) which Claude sometimes includes.
        
        Args:
            response_text: Raw text response from Claude API.
        
        Returns:
            Parsed JSON as a dictionary with evaluation data.
        
        Raises:
            json.JSONDecodeError: If response is not valid JSON.
        
        Example:
            >>> text = '```json\\n{"status": "pass"}\\n```'
            >>> result = service._parse_evaluation_response(text)
            >>> result["status"]
            'pass'
        """
        # Clean up the response - remove markdown code blocks if present
        text = response_text.strip()
        
        # Remove ```json and ``` markers if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
            
        if text.endswith("```"):
            text = text[:-3]
            
        text = text.strip()
        
        # Parse JSON
        return json.loads(text)
    
    def health_check(self) -> bool:
        """Check if the Anthropic API is accessible.
        
        Performs a basic validation that the API key is configured.
        Does not make an actual API call to avoid costs.
        
        Returns:
            True if API key appears valid, False otherwise.
        
        Example:
            >>> service = EvaluationService()
            >>> if service.health_check():
            ...     print("API ready")
        
        Note:
            This only validates key format, not actual API access.
            A real health check would require a test API call.
        """
        try:
            # Simple API check - just verify the key format
            return bool(self.settings.anthropic_api_key and 
                       len(self.settings.anthropic_api_key) > 10)
        except Exception:
            return False
