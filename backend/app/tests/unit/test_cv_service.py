"""Unit tests for CVService.

This module tests the CVService class which orchestrates CV processing,
evaluation, and database persistence. All external dependencies
(repositories, LangChain components) are mocked.

Test Categories:
    - Initialization: Service setup with dependencies
    - process_and_evaluate: Full CV processing pipeline
    - get_cv: CV retrieval with ownership checks
    - list_user_cvs: Paginated CV listing
    - delete_cv: CV deletion with ownership checks
    - re_evaluate: Re-evaluation with different templates
    - convert_to_response: Schema conversion
    - health_check: Service health verification
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.features.cv.cv_service import CVService, ProcessingResult
from app.features.cv.cv_schemas import PassFailStatus
from app.db.models.cv import CV, CVStatus, CVEvaluation, EvaluationStatus
from app.db.models.template import EvaluationTemplate, TemplateCriterion


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_session():
    """Create a mock async database session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def mock_cv_repo():
    """Create a mock CVRepository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_evaluation_repo():
    """Create a mock EvaluationRepository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_template_repo():
    """Create a mock TemplateRepository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_embedding_repo():
    """Create a mock EmbeddingRepository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_document_processor():
    """Create a mock DocumentProcessor."""
    processor = AsyncMock()
    return processor


@pytest.fixture
def mock_evaluation_chain():
    """Create a mock EvaluationChain."""
    chain = AsyncMock()
    return chain


@pytest.fixture
def mock_embedding_service():
    """Create a mock EmbeddingService."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_pdf_service():
    """Create a mock PDFService."""
    service = MagicMock()
    service.validate_pdf.return_value = (True, None)
    return service


@pytest.fixture
def sample_user_id():
    """Generate a sample user UUID."""
    return uuid.uuid4()


@pytest.fixture
def sample_cv_id():
    """Generate a sample CV UUID."""
    return uuid.uuid4()


@pytest.fixture
def sample_template_id():
    """Generate a sample template UUID."""
    return uuid.uuid4()


@pytest.fixture
def sample_cv(sample_cv_id, sample_user_id):
    """Create a sample CV entity."""
    cv = MagicMock(spec=CV)
    cv.id = sample_cv_id
    cv.user_id = sample_user_id
    cv.filename = "test_cv.pdf"
    cv.original_text = "John Doe\nSoftware Engineer\n5 years experience..."
    cv.status = CVStatus.EVALUATED.value
    cv.uploaded_at = datetime.now(timezone.utc)
    cv.evaluations = []
    return cv


@pytest.fixture
def sample_template(sample_template_id, sample_user_id):
    """Create a sample evaluation template."""
    template = MagicMock(spec=EvaluationTemplate)
    template.id = sample_template_id
    template.user_id = sample_user_id
    template.name = "Test Template"
    template.description = "Test description"
    template.is_system_template = False
    template.passing_score = 60
    template.minimum_criteria_met = 3
    
    # Create sample criteria
    criteria = []
    for i, name in enumerate(["Technical Skills", "Experience", "Education"]):
        criterion = MagicMock(spec=TemplateCriterion)
        criterion.id = uuid.uuid4()
        criterion.name = name
        criterion.description = f"Evaluate {name.lower()}"
        criterion.max_points = 30 if i == 0 else 25
        criteria.append(criterion)
    
    template.criteria = criteria
    return template


@pytest.fixture
def sample_evaluation(sample_cv_id, sample_template_id):
    """Create a sample evaluation entity."""
    evaluation = MagicMock(spec=CVEvaluation)
    evaluation.id = uuid.uuid4()
    evaluation.cv_id = sample_cv_id
    evaluation.template_id = sample_template_id
    evaluation.score = 75
    evaluation.status = EvaluationStatus.PASS.value
    evaluation.reasoning = "Strong technical background"
    evaluation.criteria_results = {
        "Technical Skills": {"score": 25, "max_score": 30, "reasoning": "Good"},
        "Experience": {"score": 20, "max_score": 25, "reasoning": "Solid"},
        "Education": {"score": 20, "max_score": 25, "reasoning": "Good degree"},
    }
    return evaluation


@pytest.fixture
def sample_langchain_evaluation():
    """Create a mock LangChain evaluation result."""
    result = MagicMock()
    result.percentage = 75
    result.passed = True
    result.summary = "Strong candidate with good technical skills"
    
    # Create criteria scores
    criteria_scores = []
    for name, score, max_score in [
        ("Technical Skills", 25, 30),
        ("Experience", 20, 25),
        ("Education", 20, 25),
    ]:
        criterion_score = MagicMock()
        criterion_score.name = name
        criterion_score.score = score
        criterion_score.max_score = max_score
        criterion_score.reasoning = f"Good {name.lower()}"
        criterion_score.evidence = ["Evidence 1", "Evidence 2"]
        criteria_scores.append(criterion_score)
    
    result.criteria_scores = criteria_scores
    return result


@pytest.fixture
def sample_processed_document():
    """Create a mock processed document."""
    doc = MagicMock()
    doc.full_text = "John Doe\nSoftware Engineer\nPython, JavaScript, React..."
    doc.chunks = [MagicMock(), MagicMock(), MagicMock()]
    doc.chunk_count = 3
    return doc


@pytest.fixture
def cv_service(
    mock_session,
    mock_cv_repo,
    mock_evaluation_repo,
    mock_template_repo,
    mock_embedding_repo,
    mock_document_processor,
    mock_evaluation_chain,
    mock_embedding_service,
    mock_pdf_service,
):
    """Create a CVService with all dependencies mocked."""
    with patch.object(CVService, '__init__', lambda self, session, evaluation_chain=None: None):
        service = CVService.__new__(CVService)
        service.session = mock_session
        service.cv_repo = mock_cv_repo
        service.evaluation_repo = mock_evaluation_repo
        service.template_repo = mock_template_repo
        service.embedding_repo = mock_embedding_repo
        service.document_processor = mock_document_processor
        service.evaluation_chain = mock_evaluation_chain
        service.embedding_service = mock_embedding_service
        service.pdf_service = mock_pdf_service
        return service


# =============================================================================
# Test: Initialization
# =============================================================================

class TestCVServiceInit:
    """Tests for CVService initialization."""
    
    def test_init_creates_repositories(self, mock_session):
        """Should initialize all repositories with session."""
        with patch('app.features.cv.cv_service.CVRepository') as MockCVRepo, \
             patch('app.features.cv.cv_service.EvaluationRepository') as MockEvalRepo, \
             patch('app.features.cv.cv_service.TemplateRepository') as MockTemplateRepo, \
             patch('app.features.cv.cv_service.EmbeddingRepository') as MockEmbedRepo, \
             patch('app.features.cv.cv_service.DocumentProcessor'), \
             patch('app.features.cv.cv_service.get_evaluation_chain'), \
             patch('app.features.cv.cv_service.EmbeddingService'), \
             patch('app.features.cv.cv_service.PDFService'):
            
            service = CVService(mock_session)
            
            MockCVRepo.assert_called_once_with(mock_session)
            MockEvalRepo.assert_called_once_with(mock_session)
            MockTemplateRepo.assert_called_once_with(mock_session)
            MockEmbedRepo.assert_called_once_with(mock_session)
    
    def test_init_with_custom_evaluation_chain(self, mock_session, mock_evaluation_chain):
        """Should use provided evaluation chain if given."""
        with patch('app.features.cv.cv_service.CVRepository'), \
             patch('app.features.cv.cv_service.EvaluationRepository'), \
             patch('app.features.cv.cv_service.TemplateRepository'), \
             patch('app.features.cv.cv_service.EmbeddingRepository'), \
             patch('app.features.cv.cv_service.DocumentProcessor'), \
             patch('app.features.cv.cv_service.get_evaluation_chain') as mock_get_chain, \
             patch('app.features.cv.cv_service.EmbeddingService'), \
             patch('app.features.cv.cv_service.PDFService'):
            
            service = CVService(mock_session, evaluation_chain=mock_evaluation_chain)
            
            # Should not call get_evaluation_chain when one is provided
            assert service.evaluation_chain == mock_evaluation_chain


# =============================================================================
# Test: process_and_evaluate
# =============================================================================

class TestProcessAndEvaluate:
    """Tests for the process_and_evaluate method."""
    
    @pytest.mark.asyncio
    async def test_process_pdf_success(
        self,
        cv_service,
        sample_user_id,
        sample_cv,
        sample_template,
        sample_evaluation,
        sample_langchain_evaluation,
        sample_processed_document,
    ):
        """Should process PDF and return evaluation result."""
        # Setup mocks
        cv_service.pdf_service.validate_pdf.return_value = (True, None)
        cv_service.document_processor.process_upload = AsyncMock(return_value=sample_processed_document)
        cv_service.cv_repo.create = AsyncMock(return_value=sample_cv)
        cv_service.cv_repo.update = AsyncMock(return_value=sample_cv)
        cv_service.embedding_service.store_cv_embeddings = AsyncMock(return_value=[MagicMock(), MagicMock()])
        cv_service.template_repo.get_with_criteria = AsyncMock(return_value=None)
        cv_service.template_repo.get_default_template = AsyncMock(return_value=sample_template)
        cv_service.evaluation_chain.evaluate_with_template = AsyncMock(return_value=sample_langchain_evaluation)
        cv_service.evaluation_repo.create = AsyncMock(return_value=sample_evaluation)
        
        # Execute
        result = await cv_service.process_and_evaluate(
            file_content=b"%PDF-1.4...",
            filename="test.pdf",
            user_id=sample_user_id,
        )
        
        # Assert
        assert isinstance(result, ProcessingResult)
        assert result.cv == sample_cv
        assert result.evaluation == sample_langchain_evaluation
        assert result.db_evaluation == sample_evaluation
        assert result.chunks_stored == 2
        cv_service.session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_docx_success(
        self,
        cv_service,
        sample_user_id,
        sample_cv,
        sample_template,
        sample_evaluation,
        sample_langchain_evaluation,
        sample_processed_document,
    ):
        """Should process DOCX without PDF validation."""
        # Setup mocks
        cv_service.document_processor.process_upload = AsyncMock(return_value=sample_processed_document)
        cv_service.cv_repo.create = AsyncMock(return_value=sample_cv)
        cv_service.cv_repo.update = AsyncMock(return_value=sample_cv)
        cv_service.embedding_service.store_cv_embeddings = AsyncMock(return_value=[MagicMock()])
        cv_service.template_repo.get_with_criteria = AsyncMock(return_value=None)
        cv_service.template_repo.get_default_template = AsyncMock(return_value=sample_template)
        cv_service.evaluation_chain.evaluate_with_template = AsyncMock(return_value=sample_langchain_evaluation)
        cv_service.evaluation_repo.create = AsyncMock(return_value=sample_evaluation)
        
        # Execute
        result = await cv_service.process_and_evaluate(
            file_content=b"PK...",
            filename="test.docx",
            user_id=sample_user_id,
        )
        
        # Assert - PDF validation should not be called for DOCX
        cv_service.pdf_service.validate_pdf.assert_not_called()
        assert isinstance(result, ProcessingResult)
    
    @pytest.mark.asyncio
    async def test_process_invalid_pdf(self, cv_service, sample_user_id):
        """Should raise ValueError for invalid PDF."""
        cv_service.pdf_service.validate_pdf.return_value = (False, "Invalid PDF structure")
        
        with pytest.raises(ValueError, match="Invalid PDF structure"):
            await cv_service.process_and_evaluate(
                file_content=b"not a pdf",
                filename="bad.pdf",
                user_id=sample_user_id,
            )
    
    @pytest.mark.asyncio
    async def test_process_with_specific_template(
        self,
        cv_service,
        sample_user_id,
        sample_cv,
        sample_template,
        sample_evaluation,
        sample_langchain_evaluation,
        sample_processed_document,
        sample_template_id,
    ):
        """Should use specified template when provided."""
        # Setup mocks
        cv_service.pdf_service.validate_pdf.return_value = (True, None)
        cv_service.document_processor.process_upload = AsyncMock(return_value=sample_processed_document)
        cv_service.cv_repo.create = AsyncMock(return_value=sample_cv)
        cv_service.cv_repo.update = AsyncMock(return_value=sample_cv)
        cv_service.embedding_service.store_cv_embeddings = AsyncMock(return_value=[])
        cv_service.template_repo.get_with_criteria = AsyncMock(return_value=sample_template)
        cv_service.evaluation_chain.evaluate_with_template = AsyncMock(return_value=sample_langchain_evaluation)
        cv_service.evaluation_repo.create = AsyncMock(return_value=sample_evaluation)
        
        # Execute
        await cv_service.process_and_evaluate(
            file_content=b"%PDF-1.4...",
            filename="test.pdf",
            user_id=sample_user_id,
            template_id=sample_template_id,
        )
        
        # Assert template lookup was called with the ID
        cv_service.template_repo.get_with_criteria.assert_called_once_with(sample_template_id)
        cv_service.template_repo.get_default_template.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_process_no_template_raises_error(
        self,
        cv_service,
        sample_user_id,
        sample_cv,
        sample_processed_document,
    ):
        """Should raise ValueError when no template is available."""
        cv_service.pdf_service.validate_pdf.return_value = (True, None)
        cv_service.document_processor.process_upload = AsyncMock(return_value=sample_processed_document)
        cv_service.cv_repo.create = AsyncMock(return_value=sample_cv)
        cv_service.cv_repo.update = AsyncMock(return_value=sample_cv)
        cv_service.embedding_service.store_cv_embeddings = AsyncMock(return_value=[])
        cv_service.template_repo.get_with_criteria = AsyncMock(return_value=None)
        cv_service.template_repo.get_default_template = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError, match="No evaluation template available"):
            await cv_service.process_and_evaluate(
                file_content=b"%PDF-1.4...",
                filename="test.pdf",
                user_id=sample_user_id,
            )
    
    @pytest.mark.asyncio
    async def test_process_evaluation_failure_sets_error_status(
        self,
        cv_service,
        sample_user_id,
        sample_cv,
        sample_template,
        sample_processed_document,
    ):
        """Should set CV status to ERROR on evaluation failure."""
        cv_service.pdf_service.validate_pdf.return_value = (True, None)
        cv_service.document_processor.process_upload = AsyncMock(return_value=sample_processed_document)
        cv_service.cv_repo.create = AsyncMock(return_value=sample_cv)
        cv_service.cv_repo.update = AsyncMock(return_value=sample_cv)
        cv_service.embedding_service.store_cv_embeddings = AsyncMock(return_value=[])
        cv_service.template_repo.get_with_criteria = AsyncMock(return_value=None)
        cv_service.template_repo.get_default_template = AsyncMock(return_value=sample_template)
        cv_service.evaluation_chain.evaluate_with_template = AsyncMock(
            side_effect=Exception("LLM API error")
        )
        
        with pytest.raises(Exception, match="LLM API error"):
            await cv_service.process_and_evaluate(
                file_content=b"%PDF-1.4...",
                filename="test.pdf",
                user_id=sample_user_id,
            )
        
        # CV status should be updated to ERROR
        assert sample_cv.status == CVStatus.ERROR.value
        cv_service.cv_repo.update.assert_called()
        cv_service.session.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_process_stores_evaluation_with_pass_status(
        self,
        cv_service,
        sample_user_id,
        sample_cv,
        sample_template,
        sample_langchain_evaluation,
        sample_processed_document,
    ):
        """Should store evaluation with PASS status when passed=True."""
        sample_langchain_evaluation.passed = True
        
        cv_service.pdf_service.validate_pdf.return_value = (True, None)
        cv_service.document_processor.process_upload = AsyncMock(return_value=sample_processed_document)
        cv_service.cv_repo.create = AsyncMock(return_value=sample_cv)
        cv_service.cv_repo.update = AsyncMock(return_value=sample_cv)
        cv_service.embedding_service.store_cv_embeddings = AsyncMock(return_value=[])
        cv_service.template_repo.get_with_criteria = AsyncMock(return_value=None)
        cv_service.template_repo.get_default_template = AsyncMock(return_value=sample_template)
        cv_service.evaluation_chain.evaluate_with_template = AsyncMock(return_value=sample_langchain_evaluation)
        cv_service.evaluation_repo.create = AsyncMock(side_effect=lambda x: x)
        
        await cv_service.process_and_evaluate(
            file_content=b"%PDF-1.4...",
            filename="test.pdf",
            user_id=sample_user_id,
        )
        
        # Check evaluation was created with PASS status
        call_args = cv_service.evaluation_repo.create.call_args[0][0]
        assert call_args.status == EvaluationStatus.PASS.value
    
    @pytest.mark.asyncio
    async def test_process_stores_evaluation_with_fail_status(
        self,
        cv_service,
        sample_user_id,
        sample_cv,
        sample_template,
        sample_langchain_evaluation,
        sample_processed_document,
    ):
        """Should store evaluation with FAIL status when passed=False."""
        sample_langchain_evaluation.passed = False
        sample_langchain_evaluation.percentage = 45
        
        cv_service.pdf_service.validate_pdf.return_value = (True, None)
        cv_service.document_processor.process_upload = AsyncMock(return_value=sample_processed_document)
        cv_service.cv_repo.create = AsyncMock(return_value=sample_cv)
        cv_service.cv_repo.update = AsyncMock(return_value=sample_cv)
        cv_service.embedding_service.store_cv_embeddings = AsyncMock(return_value=[])
        cv_service.template_repo.get_with_criteria = AsyncMock(return_value=None)
        cv_service.template_repo.get_default_template = AsyncMock(return_value=sample_template)
        cv_service.evaluation_chain.evaluate_with_template = AsyncMock(return_value=sample_langchain_evaluation)
        cv_service.evaluation_repo.create = AsyncMock(side_effect=lambda x: x)
        
        await cv_service.process_and_evaluate(
            file_content=b"%PDF-1.4...",
            filename="test.pdf",
            user_id=sample_user_id,
        )
        
        # Check evaluation was created with FAIL status
        call_args = cv_service.evaluation_repo.create.call_args[0][0]
        assert call_args.status == EvaluationStatus.FAIL.value


# =============================================================================
# Test: get_cv
# =============================================================================

class TestGetCV:
    """Tests for the get_cv method."""
    
    @pytest.mark.asyncio
    async def test_get_cv_success(self, cv_service, sample_cv, sample_user_id, sample_cv_id):
        """Should return CV when found and owned by user."""
        cv_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        
        result = await cv_service.get_cv(sample_cv_id, sample_user_id)
        
        assert result == sample_cv
        cv_service.cv_repo.get_by_id.assert_called_once_with(sample_cv_id, include_evaluations=True)
    
    @pytest.mark.asyncio
    async def test_get_cv_not_found(self, cv_service, sample_user_id, sample_cv_id):
        """Should return None when CV not found."""
        cv_service.cv_repo.get_by_id = AsyncMock(return_value=None)
        
        result = await cv_service.get_cv(sample_cv_id, sample_user_id)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_cv_wrong_user(self, cv_service, sample_cv, sample_cv_id):
        """Should return None when CV owned by different user."""
        other_user_id = uuid.uuid4()
        cv_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        
        result = await cv_service.get_cv(sample_cv_id, other_user_id)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_cv_without_evaluation(self, cv_service, sample_cv, sample_user_id, sample_cv_id):
        """Should not load evaluations when include_evaluation=False."""
        cv_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        
        await cv_service.get_cv(sample_cv_id, sample_user_id, include_evaluation=False)
        
        cv_service.cv_repo.get_by_id.assert_called_once_with(sample_cv_id, include_evaluations=False)


# =============================================================================
# Test: list_user_cvs
# =============================================================================

class TestListUserCVs:
    """Tests for the list_user_cvs method."""
    
    @pytest.mark.asyncio
    async def test_list_cvs_success(self, cv_service, sample_cv, sample_user_id):
        """Should return list of CVs and total count."""
        cv_service.cv_repo.get_by_user = AsyncMock(return_value=[sample_cv])
        cv_service.cv_repo.count_by_user = AsyncMock(return_value=1)
        
        cvs, total = await cv_service.list_user_cvs(sample_user_id)
        
        assert cvs == [sample_cv]
        assert total == 1
    
    @pytest.mark.asyncio
    async def test_list_cvs_empty(self, cv_service, sample_user_id):
        """Should return empty list when no CVs exist."""
        cv_service.cv_repo.get_by_user = AsyncMock(return_value=[])
        cv_service.cv_repo.count_by_user = AsyncMock(return_value=0)
        
        cvs, total = await cv_service.list_user_cvs(sample_user_id)
        
        assert cvs == []
        assert total == 0
    
    @pytest.mark.asyncio
    async def test_list_cvs_with_pagination(self, cv_service, sample_user_id):
        """Should pass pagination parameters to repository."""
        cv_service.cv_repo.get_by_user = AsyncMock(return_value=[])
        cv_service.cv_repo.count_by_user = AsyncMock(return_value=50)
        
        await cv_service.list_user_cvs(sample_user_id, limit=10, offset=20)
        
        cv_service.cv_repo.get_by_user.assert_called_once_with(
            user_id=sample_user_id,
            include_evaluations=True,
            limit=10,
            offset=20,
        )
    
    @pytest.mark.asyncio
    async def test_list_cvs_default_pagination(self, cv_service, sample_user_id):
        """Should use default pagination values."""
        cv_service.cv_repo.get_by_user = AsyncMock(return_value=[])
        cv_service.cv_repo.count_by_user = AsyncMock(return_value=0)
        
        await cv_service.list_user_cvs(sample_user_id)
        
        cv_service.cv_repo.get_by_user.assert_called_once_with(
            user_id=sample_user_id,
            include_evaluations=True,
            limit=20,
            offset=0,
        )


# =============================================================================
# Test: delete_cv
# =============================================================================

class TestDeleteCV:
    """Tests for the delete_cv method."""
    
    @pytest.mark.asyncio
    async def test_delete_cv_success(self, cv_service, sample_cv, sample_user_id, sample_cv_id):
        """Should delete CV and return True."""
        cv_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        cv_service.cv_repo.delete = AsyncMock()
        
        result = await cv_service.delete_cv(sample_cv_id, sample_user_id)
        
        assert result is True
        cv_service.cv_repo.delete.assert_called_once_with(sample_cv)
        cv_service.session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_cv_not_found(self, cv_service, sample_user_id, sample_cv_id):
        """Should return False when CV not found."""
        cv_service.cv_repo.get_by_id = AsyncMock(return_value=None)
        
        result = await cv_service.delete_cv(sample_cv_id, sample_user_id)
        
        assert result is False
        cv_service.cv_repo.delete.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_delete_cv_wrong_user(self, cv_service, sample_cv, sample_cv_id):
        """Should return False when CV owned by different user."""
        other_user_id = uuid.uuid4()
        cv_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        
        result = await cv_service.delete_cv(sample_cv_id, other_user_id)
        
        assert result is False
        cv_service.cv_repo.delete.assert_not_called()


# =============================================================================
# Test: re_evaluate
# =============================================================================

class TestReEvaluate:
    """Tests for the re_evaluate method."""
    
    @pytest.mark.asyncio
    async def test_re_evaluate_success(
        self,
        cv_service,
        sample_cv,
        sample_template,
        sample_langchain_evaluation,
        sample_user_id,
        sample_cv_id,
        sample_template_id,
    ):
        """Should re-evaluate CV with new template."""
        cv_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        cv_service.template_repo.get_with_criteria = AsyncMock(return_value=sample_template)
        cv_service.evaluation_chain.evaluate_with_template = AsyncMock(return_value=sample_langchain_evaluation)
        cv_service.evaluation_repo.create = AsyncMock(side_effect=lambda x: x)
        cv_service.embedding_repo.count_by_cv = AsyncMock(return_value=3)
        
        result = await cv_service.re_evaluate(sample_cv_id, sample_user_id, sample_template_id)
        
        assert isinstance(result, ProcessingResult)
        assert result.cv == sample_cv
        assert result.evaluation == sample_langchain_evaluation
        assert result.chunks_stored == 3
        cv_service.session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_re_evaluate_cv_not_found(self, cv_service, sample_user_id, sample_cv_id):
        """Should return None when CV not found."""
        cv_service.cv_repo.get_by_id = AsyncMock(return_value=None)
        
        result = await cv_service.re_evaluate(sample_cv_id, sample_user_id)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_re_evaluate_wrong_user(self, cv_service, sample_cv, sample_cv_id):
        """Should return None when CV owned by different user."""
        other_user_id = uuid.uuid4()
        cv_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        
        result = await cv_service.re_evaluate(sample_cv_id, other_user_id)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_re_evaluate_uses_default_template(
        self,
        cv_service,
        sample_cv,
        sample_template,
        sample_langchain_evaluation,
        sample_user_id,
        sample_cv_id,
    ):
        """Should use default template when none specified."""
        cv_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        cv_service.template_repo.get_with_criteria = AsyncMock(return_value=None)
        cv_service.template_repo.get_default_template = AsyncMock(return_value=sample_template)
        cv_service.evaluation_chain.evaluate_with_template = AsyncMock(return_value=sample_langchain_evaluation)
        cv_service.evaluation_repo.create = AsyncMock(side_effect=lambda x: x)
        cv_service.embedding_repo.count_by_cv = AsyncMock(return_value=0)
        
        await cv_service.re_evaluate(sample_cv_id, sample_user_id)
        
        cv_service.template_repo.get_default_template.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_re_evaluate_no_template_raises_error(
        self,
        cv_service,
        sample_cv,
        sample_user_id,
        sample_cv_id,
    ):
        """Should raise ValueError when no template available."""
        cv_service.cv_repo.get_by_id = AsyncMock(return_value=sample_cv)
        cv_service.template_repo.get_with_criteria = AsyncMock(return_value=None)
        cv_service.template_repo.get_default_template = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError, match="No evaluation template available"):
            await cv_service.re_evaluate(sample_cv_id, sample_user_id)


# =============================================================================
# Test: convert_to_response
# =============================================================================

class TestConvertToResponse:
    """Tests for the convert_to_response method."""
    
    def test_convert_pass_evaluation(self, cv_service, sample_cv, sample_langchain_evaluation, sample_evaluation):
        """Should convert passing evaluation to response."""
        sample_langchain_evaluation.passed = True
        sample_langchain_evaluation.percentage = 75
        
        result = ProcessingResult(
            cv=sample_cv,
            evaluation=sample_langchain_evaluation,
            db_evaluation=sample_evaluation,
            chunks_stored=3,
        )
        
        response = cv_service.convert_to_response(result)
        
        assert response.success is True
        assert response.evaluation.status == PassFailStatus.PASS
        assert response.evaluation.match_score == 75
        assert len(response.evaluation.criteria) == 3
    
    def test_convert_fail_evaluation(self, cv_service, sample_cv, sample_langchain_evaluation, sample_evaluation):
        """Should convert failing evaluation to response."""
        sample_langchain_evaluation.passed = False
        sample_langchain_evaluation.percentage = 45
        
        result = ProcessingResult(
            cv=sample_cv,
            evaluation=sample_langchain_evaluation,
            db_evaluation=sample_evaluation,
            chunks_stored=3,
        )
        
        response = cv_service.convert_to_response(result)
        
        assert response.evaluation.status == PassFailStatus.FAIL
        assert response.evaluation.match_score == 45
    
    def test_convert_criteria_passed_threshold(self, cv_service, sample_cv, sample_langchain_evaluation, sample_evaluation):
        """Should mark criteria as passed if score >= 50% of max."""
        # First criterion: 25/30 = 83% >= 50% → passed
        # Second criterion: 20/25 = 80% >= 50% → passed
        result = ProcessingResult(
            cv=sample_cv,
            evaluation=sample_langchain_evaluation,
            db_evaluation=sample_evaluation,
            chunks_stored=3,
        )
        
        response = cv_service.convert_to_response(result)
        
        assert response.evaluation.criteria[0].passed is True
        assert response.evaluation.criteria[1].passed is True


# =============================================================================
# Test: health_check
# =============================================================================

class TestHealthCheck:
    """Tests for the health_check method."""
    
    def test_health_check_success(self, cv_service):
        """Should return True when evaluation chain is available."""
        with patch('app.features.cv.cv_service.get_evaluation_chain') as mock_get_chain:
            mock_get_chain.return_value = MagicMock()
            
            result = cv_service.health_check()
            
            assert result is True
    
    def test_health_check_failure(self, cv_service):
        """Should return False when evaluation chain fails."""
        with patch('app.features.cv.cv_service.get_evaluation_chain') as mock_get_chain:
            mock_get_chain.side_effect = Exception("API key not configured")
            
            result = cv_service.health_check()
            
            assert result is False
    
    def test_health_check_returns_none(self, cv_service):
        """Should return False when evaluation chain returns None."""
        with patch('app.features.cv.cv_service.get_evaluation_chain') as mock_get_chain:
            mock_get_chain.return_value = None
            
            result = cv_service.health_check()
            
            assert result is False
