"""Pydantic schemas for CV evaluation request/response models.

This module defines the data contracts for the CV screening API.
All schemas include validation rules and OpenAPI documentation.

Classes:
    PassFailStatus: Enum for evaluation status.
    EvaluationCriteria: Individual criterion result.
    CVEvaluationRequest: Internal evaluation request.
    CVEvaluationResponse: Main evaluation response.
    UploadResponse: File upload response wrapper.
    ErrorResponse: Standard error response.
    CVSummary: Summary of a CV for list views.
    CVListResponse: Response for CV listing endpoint.
    EvaluationDetail: Detailed evaluation information.
    CVDetailResponse: Response for single CV detail endpoint.

Example:
    Creating an evaluation response::
    
        response = CVEvaluationResponse(
            status=PassFailStatus.PASS,
            match_score=85,
            reasoning="Strong candidate...",
            criteria=[...],
            candidate_name="John Doe"
        )
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class PassFailStatus(str, Enum):
    """Enumeration for pass/fail evaluation status.
    
    Attributes:
        PASS: Candidate meets the hiring criteria.
        FAIL: Candidate does not meet the hiring criteria.
    """
    PASS = "pass"
    FAIL = "fail"


class EvaluationCriteria(BaseModel):
    """Individual evaluation criterion result.
    
    Represents the evaluation result for a single hiring criterion
    (e.g., Education, Fintech Experience, Technical Skills).
    
    Attributes:
        name: Name of the criterion being evaluated.
        passed: Whether the criterion was met.
        details: Explanation of the evaluation decision.
    
    Example:
        >>> criterion = EvaluationCriteria(
        ...     name="Education",
        ...     passed=True,
        ...     details="Bachelor's degree in Computer Science"
        ... )
    """
    name: str = Field(..., description="Name of the criterion being evaluated")
    passed: bool = Field(..., description="Whether the criterion was met")
    details: str = Field(..., description="Explanation of the evaluation")


class CVEvaluationRequest(BaseModel):
    """Request model for CV evaluation (internal use).
    
    Used to pass extracted CV data to the evaluation service.
    
    Attributes:
        cv_text: Extracted text content from the CV PDF.
        filename: Original filename of the uploaded CV.
    """
    cv_text: str = Field(..., description="Extracted text content from the CV")
    filename: str = Field(..., description="Original filename of the uploaded CV")


class CVEvaluationResponse(BaseModel):
    """Structured response from the CV evaluation.
    
    This is the main output displayed on the frontend scorecard.
    Contains overall status, score, reasoning, and individual criteria.
    
    Attributes:
        status: Overall pass/fail status of the CV screening.
        match_score: Overall match score from 0-100.
        reasoning: Detailed explanation of the evaluation decision.
        criteria: List of individual criteria evaluations.
        candidate_name: Extracted candidate name if found.
    
    Example:
        >>> response = CVEvaluationResponse(
        ...     status=PassFailStatus.PASS,
        ...     match_score=85,
        ...     reasoning="Strong qualifications...",
        ...     criteria=[criterion1, criterion2, criterion3],
        ...     candidate_name="Jane Smith"
        ... )
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
        """Pydantic configuration."""
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
    """Response model for file upload endpoint.
    
    Wraps the evaluation response with success status and message.
    
    Attributes:
        success: Whether the upload and evaluation was successful.
        message: Status message describing the result.
        evaluation: CV evaluation results if successful.
    
    Example:
        >>> response = UploadResponse(
        ...     success=True,
        ...     message="CV evaluated successfully",
        ...     evaluation=evaluation_response
        ... )
    """
    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Status message")
    evaluation: Optional[CVEvaluationResponse] = Field(
        None, 
        description="CV evaluation results if successful"
    )


class ErrorResponse(BaseModel):
    """Standard error response model.
    
    Used for consistent error responses across CV endpoints.
    
    Attributes:
        success: Always False for error responses.
        error: Error message.
        detail: Optional detailed error information.
    """
    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


class CVSummary(BaseModel):
    """Summary of a CV for list views.
    
    Attributes:
        id: CV UUID.
        filename: Original uploaded filename.
        candidate_name: Extracted candidate name if available.
        status: Processing status.
        uploaded_at: Upload timestamp.
        score: Latest evaluation score if available.
        evaluation_status: Pass/fail status if evaluated.
    """
    id: str = Field(..., description="CV UUID")
    filename: str = Field(..., description="Original uploaded filename")
    candidate_name: Optional[str] = Field(None, description="Extracted candidate name")
    status: str = Field(..., description="Processing status")
    uploaded_at: str = Field(..., description="Upload timestamp ISO format")
    score: Optional[int] = Field(None, description="Latest evaluation score")
    evaluation_status: Optional[str] = Field(None, description="Pass/fail status")


class CVListResponse(BaseModel):
    """Response for CV listing endpoint.
    
    Attributes:
        cvs: List of CV summaries.
        total: Total number of CVs.
        limit: Maximum returned per page.
        offset: Number of CVs skipped.
    """
    cvs: list[CVSummary] = Field(..., description="List of CV summaries")
    total: int = Field(..., description="Total number of CVs")
    limit: int = Field(..., description="Page size")
    offset: int = Field(..., description="Items skipped")


class EvaluationDetail(BaseModel):
    """Detailed evaluation information.
    
    Attributes:
        id: Evaluation UUID.
        score: Evaluation score (0-100).
        status: Pass or fail.
        reasoning: AI-generated explanation.
        criteria_results: Per-criterion scores and evidence.
        evaluated_at: Evaluation timestamp.
    """
    id: str = Field(..., description="Evaluation UUID")
    score: int = Field(..., description="Evaluation score")
    status: str = Field(..., description="Pass or fail")
    reasoning: Optional[str] = Field(None, description="AI explanation")
    criteria_results: Optional[dict] = Field(None, description="Per-criterion results")
    evaluated_at: str = Field(..., description="Evaluation timestamp ISO format")


class CVDetailResponse(BaseModel):
    """Response for single CV detail endpoint.
    
    Attributes:
        id: CV UUID.
        filename: Original uploaded filename.
        candidate_name: Extracted candidate name if available.
        status: Processing status.
        uploaded_at: Upload timestamp.
        original_text: Full extracted CV text.
        evaluation: Latest evaluation details if available.
    """
    id: str = Field(..., description="CV UUID")
    filename: str = Field(..., description="Original uploaded filename")
    candidate_name: Optional[str] = Field(None, description="Extracted candidate name")
    status: str = Field(..., description="Processing status")
    uploaded_at: str = Field(..., description="Upload timestamp ISO format")
    original_text: str = Field(..., description="Full extracted CV text")
    evaluation: Optional[EvaluationDetail] = Field(None, description="Latest evaluation")
