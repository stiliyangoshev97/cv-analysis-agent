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
    SimilarCVResponse: A CV found in similarity search.
    SimilarCVsResponse: Response for finding similar CVs.
    CVRankingResponse: Response for CV percentile ranking.
    CVComparisonItemResponse: A single CV in a comparison.
    CVCompareRequest: Request to compare multiple CVs.
    CVCompareResponse: Response for CV comparison.
    CVSearchRequest: Request for semantic CV search.
    CVSearchResponse: Response for semantic CV search.

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


# =============================================================================
# Similarity Search Schemas
# =============================================================================

class SimilarCVResponse(BaseModel):
    """A CV found in similarity search.
    
    Attributes:
        cv_id: UUID of the similar CV.
        filename: Original filename.
        candidate_name: Candidate name if available.
        similarity_score: Cosine similarity (0-1, higher = more similar).
        evaluation_score: Evaluation score if available.
        status: Pass/fail status if evaluated.
    
    Example:
        >>> for cv in response.similar_cvs:
        ...     print(f"{cv.candidate_name}: {cv.similarity_score:.1%} similar")
    """
    cv_id: str = Field(..., description="CV UUID")
    filename: str = Field(..., description="Original filename")
    candidate_name: Optional[str] = Field(None, description="Candidate name")
    similarity_score: float = Field(..., ge=0, le=1, description="Similarity score 0-1")
    evaluation_score: Optional[int] = Field(None, ge=0, le=100, description="Evaluation score")
    status: Optional[str] = Field(None, description="Pass/fail status")


class SimilarCVsResponse(BaseModel):
    """Response for finding similar CVs.
    
    Attributes:
        source_cv_id: The CV used as the similarity source.
        similar_cvs: List of similar CVs found.
        total: Number of similar CVs found.
    """
    source_cv_id: str = Field(..., description="Source CV UUID")
    similar_cvs: list[SimilarCVResponse] = Field(..., description="Similar CVs")
    total: int = Field(..., description="Number of results")


class CVRankingResponse(BaseModel):
    """Response for CV percentile ranking.
    
    Attributes:
        cv_id: UUID of the ranked CV.
        percentile: Percentile rank (0-100, higher = better than more).
        rank: Absolute rank (1 = best).
        total_cvs: Total CVs in comparison.
        evaluation_score: This CV's score.
        average_score: Average score across all CVs.
        highest_score: Highest score in dataset.
        label: Human-readable ranking label.
    
    Example:
        >>> print(f"Ranked #{response.rank} of {response.total_cvs}")
        >>> print(f"Better than {response.percentile:.0f}% of candidates")
    """
    cv_id: str = Field(..., description="CV UUID")
    percentile: float = Field(..., ge=0, le=100, description="Percentile rank")
    rank: int = Field(..., ge=1, description="Absolute rank")
    total_cvs: int = Field(..., ge=1, description="Total CVs compared")
    evaluation_score: int = Field(..., ge=0, le=100, description="CV score")
    average_score: float = Field(..., ge=0, le=100, description="Average score")
    highest_score: int = Field(..., ge=0, le=100, description="Highest score")
    label: str = Field(..., description="Human-readable label like 'Top 10%'")


class CVComparisonItemResponse(BaseModel):
    """A single CV in a comparison.
    
    Attributes:
        cv_id: CV UUID.
        filename: Original filename.
        candidate_name: Candidate name if available.
        evaluation_score: Evaluation score if available.
        status: Pass/fail status.
        similarity_to_first: Similarity to the first CV in comparison.
    """
    cv_id: str = Field(..., description="CV UUID")
    filename: str = Field(..., description="Original filename")
    candidate_name: Optional[str] = Field(None, description="Candidate name")
    evaluation_score: Optional[int] = Field(None, description="Evaluation score")
    status: Optional[str] = Field(None, description="Pass/fail status")
    similarity_to_first: float = Field(..., description="Similarity to first CV")


class CVCompareRequest(BaseModel):
    """Request to compare multiple CVs.
    
    Attributes:
        cv_ids: List of CV UUIDs to compare (2-10).
    
    Example:
        >>> request = CVCompareRequest(cv_ids=["uuid1", "uuid2", "uuid3"])
    """
    cv_ids: list[str] = Field(
        ...,
        min_length=2,
        max_length=10,
        description="CV UUIDs to compare (2-10)",
    )


class CVCompareResponse(BaseModel):
    """Response for CV comparison.
    
    Attributes:
        cvs: List of compared CVs with details.
        similarity_matrix: NxN pairwise similarity matrix.
        best_match_id: UUID of highest-scoring CV.
        most_similar_pair: Most similar pair of CVs.
    """
    cvs: list[CVComparisonItemResponse] = Field(..., description="Compared CVs")
    similarity_matrix: list[list[float]] = Field(..., description="Pairwise similarities")
    best_match_id: Optional[str] = Field(None, description="Best candidate UUID")
    most_similar_pair: Optional[dict] = Field(None, description="Most similar pair info")


class CVSearchRequest(BaseModel):
    """Request for semantic CV search.
    
    Attributes:
        query: Natural language search query.
        limit: Maximum results to return.
        min_similarity: Minimum similarity threshold.
    
    Example:
        >>> request = CVSearchRequest(
        ...     query="Python developer with fintech experience",
        ...     limit=10,
        ... )
    """
    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language search query",
    )
    limit: int = Field(10, ge=1, le=50, description="Maximum results")
    min_similarity: float = Field(0.0, ge=0, le=1, description="Minimum similarity")


class CVSearchResponse(BaseModel):
    """Response for semantic CV search.
    
    Attributes:
        query: The search query used.
        results: List of matching CVs.
        total: Number of results found.
    """
    query: str = Field(..., description="Search query")
    results: list[SimilarCVResponse] = Field(..., description="Matching CVs")
    total: int = Field(..., description="Number of results")
