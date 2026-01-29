"""
Pydantic schemas for request/response models.
Defines the structured data contracts for the API.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class PassFailStatus(str, Enum):
    """Enum for pass/fail evaluation status."""
    PASS = "pass"
    FAIL = "fail"


class EvaluationCriteria(BaseModel):
    """Individual evaluation criterion result."""
    
    name: str = Field(..., description="Name of the criterion being evaluated")
    passed: bool = Field(..., description="Whether the criterion was met")
    details: str = Field(..., description="Explanation of the evaluation")


class CVEvaluationRequest(BaseModel):
    """Request model for CV evaluation (used internally)."""
    
    cv_text: str = Field(..., description="Extracted text content from the CV")
    filename: str = Field(..., description="Original filename of the uploaded CV")


class CVEvaluationResponse(BaseModel):
    """
    Structured response from the CV evaluation.
    This is the main output displayed on the frontend scorecard.
    """
    
    status: PassFailStatus = Field(
        ..., 
        description="Overall pass/fail status of the CV screening"
    )
    match_score: int = Field(
        ..., 
        ge=0, 
        le=100, 
        description="Overall match score from 0-100"
    )
    reasoning: str = Field(
        ..., 
        description="Detailed paragraph explaining the evaluation decision"
    )
    criteria: list[EvaluationCriteria] = Field(
        ..., 
        description="List of individual criteria evaluations"
    )
    candidate_name: Optional[str] = Field(
        None, 
        description="Extracted candidate name if found"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "pass",
                "match_score": 85,
                "reasoning": "The candidate demonstrates strong qualifications with a Bachelor's degree in Computer Science, 3 years of experience in fintech at a cryptocurrency exchange, and proficient TypeScript/Python skills.",
                "criteria": [
                    {
                        "name": "Education",
                        "passed": True,
                        "details": "Bachelor's degree in Computer Science from MIT"
                    },
                    {
                        "name": "Fintech Experience",
                        "passed": True,
                        "details": "3 years at Coinbase working on trading systems"
                    },
                    {
                        "name": "Technical Skills",
                        "passed": True,
                        "details": "Proficient in TypeScript, Python, and React"
                    }
                ],
                "candidate_name": "John Doe"
            }
        }


class UploadResponse(BaseModel):
    """Response model for file upload endpoint."""
    
    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Status message")
    evaluation: Optional[CVEvaluationResponse] = Field(
        None, 
        description="CV evaluation results if successful"
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
