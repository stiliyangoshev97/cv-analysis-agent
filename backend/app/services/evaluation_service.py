"""
CV Evaluation Service.
Handles the AI-powered evaluation of CV content using Claude.
"""

import json
import logging
from typing import Optional
from anthropic import Anthropic
from ..config import get_settings
from ..models.schemas import CVEvaluationResponse, EvaluationCriteria, PassFailStatus

logger = logging.getLogger(__name__)

# System prompt for CV evaluation
CV_EVALUATION_SYSTEM_PROMPT = """You are an expert HR screening agent for XBO.com, a fintech company. 
Your task is to evaluate CV/resume content and provide a structured assessment.

You MUST evaluate candidates based on these THREE criteria:

1. **Education**: Does the candidate have at least a High School Diploma (or equivalent/higher)?
   - Look for: High School, GED, Associate's, Bachelor's, Master's, PhD, or equivalent certifications
   
2. **Fintech Fit**: Does the candidate have relevant experience in Finance, Banking, Cryptocurrency, or Fintech?
   - Look for: Experience at financial institutions, crypto exchanges, trading platforms, payment companies
   - Also consider: Blockchain experience, DeFi, traditional finance roles
   
3. **Technical Skills**: Does the candidate have proficiency in TypeScript OR Python?
   - Look for: Direct mentions of TypeScript, Python, JavaScript (close to TypeScript), or related frameworks
   - Consider: React, Node.js, FastAPI, Django, Flask as indicators of these skills

SCORING GUIDELINES:
- Each criterion is worth roughly 33 points
- Bonus points for exceptional qualifications
- Score 0-100 overall

PASS/FAIL LOGIC:
- PASS: Score >= 60 AND at least 2 out of 3 criteria are met
- FAIL: Score < 60 OR fewer than 2 criteria met

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
        }
    ],
    "candidate_name": "<extracted name or null if not found>"
}

Be fair but thorough. If information is missing or unclear, note it in your evaluation."""


class EvaluationService:
    """Service for evaluating CV content using Claude AI."""
    
    def __init__(self):
        """Initialize the evaluation service with Anthropic client."""
        self.settings = get_settings()
        self.client = Anthropic(api_key=self.settings.anthropic_api_key)
        
    def evaluate_cv(self, cv_text: str, filename: str) -> CVEvaluationResponse:
        """
        Evaluate CV content using Claude AI.
        
        Args:
            cv_text: Extracted text content from the CV
            filename: Original filename for context
            
        Returns:
            Structured evaluation response
            
        Raises:
            ValueError: If evaluation fails
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
        """
        Parse the Claude response text to extract JSON.
        Handles cases where JSON might be wrapped in markdown code blocks.
        
        Args:
            response_text: Raw response from Claude
            
        Returns:
            Parsed JSON as dictionary
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
        """
        Check if the Anthropic API is accessible.
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Simple API check - just verify the key format
            return bool(self.settings.anthropic_api_key and 
                       len(self.settings.anthropic_api_key) > 10)
        except Exception:
            return False
