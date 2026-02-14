"""Unit tests for NotificationService.

Tests cover:
- get_settings: Retrieve notification settings
- update_settings: Update notification preferences
- check_threshold: Score threshold checking
- dispatch_cv_notification: Full notification dispatch pipeline
- send_test_notification: Test notification sending

All external dependencies (repositories, email/whatsapp services) are mocked.
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.features.notification.notification_service import (
    NotificationService,
    NotificationDispatchResult,
)
from app.features.notification.notification_schemas import CVNotificationData
from app.features.notification.email_service import EmailResult
from app.features.notification.whatsapp_service import WhatsAppResult
from app.db.models.notification import NotificationSettings
from app.db.models.user import User


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_session():
    """Create a mock async session."""
    session = AsyncMock()
    return session


@pytest.fixture
def sample_user_id():
    """Sample user UUID."""
    return uuid.uuid4()


@pytest.fixture
def sample_settings(sample_user_id):
    """Create sample notification settings."""
    settings = NotificationSettings(
        id=uuid.uuid4(),
        user_id=sample_user_id,
        email_enabled=True,
        whatsapp_enabled=False,
        whatsapp_number=None,
        threshold_score=70,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    return settings


@pytest.fixture
def sample_cv_data():
    """Create sample CV notification data."""
    return CVNotificationData(
        cv_id=str(uuid.uuid4()),
        filename="resume.pdf",
        candidate_name="John Doe",
        score=85,
        passed=True,
        summary="Strong Python developer with 5 years experience.",
    )


@pytest.fixture
def notification_service(mock_session):
    """Create NotificationService with mocked dependencies."""
    with patch.object(NotificationService, '__init__', lambda x, y: None):
        service = NotificationService(mock_session)
        service.session = mock_session
        service.repo = AsyncMock()
        service.email_service = MagicMock()
        service.whatsapp_service = MagicMock()
        return service


# =============================================================================
# Test: NotificationDispatchResult dataclass
# =============================================================================

class TestNotificationDispatchResult:
    """Tests for the NotificationDispatchResult dataclass."""
    
    def test_success_with_email(self):
        """Should return success=True when email sent."""
        result = NotificationDispatchResult(
            should_notify=True,
            score=85,
            threshold=70,
            email_sent=True,
            whatsapp_sent=False,
        )
        assert result.success is True
        assert result.partial_success is False
    
    def test_success_with_whatsapp(self):
        """Should return success=True when whatsapp sent."""
        result = NotificationDispatchResult(
            should_notify=True,
            score=85,
            threshold=70,
            email_sent=False,
            whatsapp_sent=True,
        )
        assert result.success is True
    
    def test_success_with_both(self):
        """Should return success=True when both sent."""
        result = NotificationDispatchResult(
            should_notify=True,
            score=85,
            threshold=70,
            email_sent=True,
            whatsapp_sent=True,
            channels_attempted=["email", "whatsapp"],
        )
        assert result.success is True
        assert result.partial_success is False
    
    def test_no_success(self):
        """Should return success=False when nothing sent."""
        result = NotificationDispatchResult(
            should_notify=True,
            score=85,
            threshold=70,
            email_sent=False,
            whatsapp_sent=False,
        )
        assert result.success is False
    
    def test_partial_success(self):
        """Should detect partial success."""
        result = NotificationDispatchResult(
            should_notify=True,
            score=85,
            threshold=70,
            email_sent=True,
            whatsapp_sent=False,
            channels_attempted=["email", "whatsapp"],
        )
        assert result.partial_success is True
    
    def test_default_lists(self):
        """Should initialize empty lists by default."""
        result = NotificationDispatchResult(
            should_notify=True,
            score=85,
            threshold=70,
        )
        assert result.channels_attempted == []
        assert result.errors == []


# =============================================================================
# Test: get_settings
# =============================================================================

class TestGetSettings:
    """Tests for the get_settings method."""
    
    @pytest.mark.asyncio
    async def test_get_settings_success(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should return notification settings for user."""
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        result = await notification_service.get_settings(sample_user_id)
        
        assert result == sample_settings
        notification_service.repo.get_or_create.assert_called_once_with(sample_user_id)
    
    @pytest.mark.asyncio
    async def test_get_settings_creates_if_not_exists(
        self,
        notification_service,
        sample_user_id,
    ):
        """Should create default settings if none exist."""
        # get_or_create handles creation internally
        default_settings = NotificationSettings(
            id=uuid.uuid4(),
            user_id=sample_user_id,
            email_enabled=False,
            whatsapp_enabled=False,
            threshold_score=80,
        )
        notification_service.repo.get_or_create = AsyncMock(return_value=default_settings)
        
        result = await notification_service.get_settings(sample_user_id)
        
        assert result.email_enabled is False
        assert result.threshold_score == 80


# =============================================================================
# Test: update_settings
# =============================================================================

class TestUpdateSettings:
    """Tests for the update_settings method."""
    
    @pytest.mark.asyncio
    async def test_update_email_enabled(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should update email_enabled setting."""
        sample_settings.email_enabled = False
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        notification_service.repo.update = AsyncMock(return_value=sample_settings)
        
        result = await notification_service.update_settings(
            sample_user_id,
            email_enabled=True,
        )
        
        assert sample_settings.email_enabled is True
        notification_service.repo.update.assert_called_once_with(sample_settings)
    
    @pytest.mark.asyncio
    async def test_update_whatsapp_settings(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should update WhatsApp settings."""
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        notification_service.repo.update = AsyncMock(return_value=sample_settings)
        
        await notification_service.update_settings(
            sample_user_id,
            whatsapp_enabled=True,
            whatsapp_number="+1234567890",
        )
        
        assert sample_settings.whatsapp_enabled is True
        assert sample_settings.whatsapp_number == "+1234567890"
    
    @pytest.mark.asyncio
    async def test_update_threshold_score(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should update threshold score."""
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        notification_service.repo.update = AsyncMock(return_value=sample_settings)
        
        await notification_service.update_settings(
            sample_user_id,
            threshold_score=90,
        )
        
        assert sample_settings.threshold_score == 90
    
    @pytest.mark.asyncio
    async def test_update_multiple_settings(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should update multiple settings at once."""
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        notification_service.repo.update = AsyncMock(return_value=sample_settings)
        
        await notification_service.update_settings(
            sample_user_id,
            email_enabled=False,
            whatsapp_enabled=True,
            whatsapp_number="+1987654321",
            threshold_score=85,
        )
        
        assert sample_settings.email_enabled is False
        assert sample_settings.whatsapp_enabled is True
        assert sample_settings.whatsapp_number == "+1987654321"
        assert sample_settings.threshold_score == 85
    
    @pytest.mark.asyncio
    async def test_update_no_changes_if_none_provided(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should not change anything if no values provided."""
        original_email = sample_settings.email_enabled
        original_threshold = sample_settings.threshold_score
        
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        notification_service.repo.update = AsyncMock(return_value=sample_settings)
        
        await notification_service.update_settings(sample_user_id)
        
        assert sample_settings.email_enabled == original_email
        assert sample_settings.threshold_score == original_threshold


# =============================================================================
# Test: check_threshold
# =============================================================================

class TestCheckThreshold:
    """Tests for the check_threshold method."""
    
    @pytest.mark.asyncio
    async def test_score_above_threshold(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should return True when score >= threshold."""
        sample_settings.threshold_score = 70
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        should_notify, threshold = await notification_service.check_threshold(
            sample_user_id, score=85
        )
        
        assert should_notify is True
        assert threshold == 70
    
    @pytest.mark.asyncio
    async def test_score_below_threshold(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should return False when score < threshold."""
        sample_settings.threshold_score = 80
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        should_notify, threshold = await notification_service.check_threshold(
            sample_user_id, score=75
        )
        
        assert should_notify is False
        assert threshold == 80
    
    @pytest.mark.asyncio
    async def test_score_equals_threshold(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should return True when score == threshold."""
        sample_settings.threshold_score = 70
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        should_notify, threshold = await notification_service.check_threshold(
            sample_user_id, score=70
        )
        
        assert should_notify is True


# =============================================================================
# Test: dispatch_cv_notification
# =============================================================================

class TestDispatchCVNotification:
    """Tests for the dispatch_cv_notification method."""
    
    @pytest.mark.asyncio
    async def test_dispatch_below_threshold_skips(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should skip notification if score below threshold."""
        sample_settings.threshold_score = 90
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        cv_data = CVNotificationData(
            cv_id=str(uuid.uuid4()),
            filename="test.pdf",
            candidate_name="Test",
            score=70,  # Below threshold
            passed=False,
            summary="Test summary",
        )
        
        result = await notification_service.dispatch_cv_notification(
            sample_user_id, cv_data
        )
        
        assert result.should_notify is False
        assert result.email_sent is False
        assert result.whatsapp_sent is False
        assert result.channels_attempted == []
    
    @pytest.mark.asyncio
    async def test_dispatch_email_success(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
        sample_cv_data,
    ):
        """Should send email notification successfully."""
        sample_settings.email_enabled = True
        sample_settings.whatsapp_enabled = False
        sample_settings.threshold_score = 70
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        # Mock email service
        notification_service.email_service.is_configured = True
        notification_service.email_service.send_cv_notification = AsyncMock(
            return_value=EmailResult(success=True, message_id="msg123")
        )
        
        result = await notification_service.dispatch_cv_notification(
            sample_user_id,
            sample_cv_data,
            user_email="test@example.com",
        )
        
        assert result.should_notify is True
        assert result.email_sent is True
        assert "email" in result.channels_attempted
        assert result.errors == []
    
    @pytest.mark.asyncio
    async def test_dispatch_email_not_configured(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
        sample_cv_data,
    ):
        """Should handle email service not configured."""
        sample_settings.email_enabled = True
        sample_settings.threshold_score = 70
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        # Email service not configured
        notification_service.email_service.is_configured = False
        
        result = await notification_service.dispatch_cv_notification(
            sample_user_id,
            sample_cv_data,
            user_email="test@example.com",
        )
        
        assert result.email_sent is False
        assert "Email service not configured" in result.errors
    
    @pytest.mark.asyncio
    async def test_dispatch_email_no_user_email(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
        sample_cv_data,
    ):
        """Should handle missing user email."""
        sample_settings.email_enabled = True
        sample_settings.threshold_score = 70
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        # No user found in database
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        notification_service.session.execute = AsyncMock(return_value=mock_result)
        
        result = await notification_service.dispatch_cv_notification(
            sample_user_id, sample_cv_data
        )
        
        assert result.email_sent is False
        assert "User email not found" in result.errors
    
    @pytest.mark.asyncio
    async def test_dispatch_fetches_email_from_db(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
        sample_cv_data,
    ):
        """Should fetch user email from database if not provided."""
        sample_settings.email_enabled = True
        sample_settings.threshold_score = 70
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        # Mock user in database
        mock_user = User(id=sample_user_id, email="fetched@example.com")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        notification_service.session.execute = AsyncMock(return_value=mock_result)
        
        # Mock email service
        notification_service.email_service.is_configured = True
        notification_service.email_service.send_cv_notification = AsyncMock(
            return_value=EmailResult(success=True, message_id="msg123")
        )
        
        result = await notification_service.dispatch_cv_notification(
            sample_user_id, sample_cv_data
        )
        
        assert result.email_sent is True
        notification_service.email_service.send_cv_notification.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_dispatch_whatsapp_success(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
        sample_cv_data,
    ):
        """Should send WhatsApp notification successfully."""
        sample_settings.email_enabled = False
        sample_settings.whatsapp_enabled = True
        sample_settings.whatsapp_number = "+1234567890"
        sample_settings.threshold_score = 70
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        # Mock WhatsApp service
        notification_service.whatsapp_service.is_configured = True
        notification_service.whatsapp_service.send_cv_notification = AsyncMock(
            return_value=WhatsAppResult(success=True, message_sid="sid123")
        )
        
        result = await notification_service.dispatch_cv_notification(
            sample_user_id, sample_cv_data
        )
        
        assert result.should_notify is True
        assert result.whatsapp_sent is True
        assert "whatsapp" in result.channels_attempted
    
    @pytest.mark.asyncio
    async def test_dispatch_whatsapp_no_number(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
        sample_cv_data,
    ):
        """Should handle missing WhatsApp number."""
        sample_settings.email_enabled = False
        sample_settings.whatsapp_enabled = True
        sample_settings.whatsapp_number = None
        sample_settings.threshold_score = 70
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        result = await notification_service.dispatch_cv_notification(
            sample_user_id, sample_cv_data
        )
        
        assert result.whatsapp_sent is False
        assert "WhatsApp number not configured" in result.errors
    
    @pytest.mark.asyncio
    async def test_dispatch_whatsapp_not_configured(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
        sample_cv_data,
    ):
        """Should handle WhatsApp service not configured."""
        sample_settings.email_enabled = False
        sample_settings.whatsapp_enabled = True
        sample_settings.whatsapp_number = "+1234567890"
        sample_settings.threshold_score = 70
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        notification_service.whatsapp_service.is_configured = False
        
        result = await notification_service.dispatch_cv_notification(
            sample_user_id, sample_cv_data
        )
        
        assert result.whatsapp_sent is False
        assert "WhatsApp service not configured" in result.errors
    
    @pytest.mark.asyncio
    async def test_dispatch_both_channels_success(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
        sample_cv_data,
    ):
        """Should send to both channels successfully."""
        sample_settings.email_enabled = True
        sample_settings.whatsapp_enabled = True
        sample_settings.whatsapp_number = "+1234567890"
        sample_settings.threshold_score = 70
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        # Mock both services
        notification_service.email_service.is_configured = True
        notification_service.email_service.send_cv_notification = AsyncMock(
            return_value=EmailResult(success=True, message_id="email123")
        )
        notification_service.whatsapp_service.is_configured = True
        notification_service.whatsapp_service.send_cv_notification = AsyncMock(
            return_value=WhatsAppResult(success=True, message_sid="wa123")
        )
        
        result = await notification_service.dispatch_cv_notification(
            sample_user_id,
            sample_cv_data,
            user_email="test@example.com",
        )
        
        assert result.email_sent is True
        assert result.whatsapp_sent is True
        assert result.success is True
        assert result.partial_success is False
        assert len(result.channels_attempted) == 2
    
    @pytest.mark.asyncio
    async def test_dispatch_partial_failure(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
        sample_cv_data,
    ):
        """Should handle partial failure (one channel fails)."""
        sample_settings.email_enabled = True
        sample_settings.whatsapp_enabled = True
        sample_settings.whatsapp_number = "+1234567890"
        sample_settings.threshold_score = 70
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        # Email succeeds, WhatsApp fails
        notification_service.email_service.is_configured = True
        notification_service.email_service.send_cv_notification = AsyncMock(
            return_value=EmailResult(success=True, message_id="email123")
        )
        notification_service.whatsapp_service.is_configured = True
        notification_service.whatsapp_service.send_cv_notification = AsyncMock(
            return_value=WhatsAppResult(success=False, error="Network error")
        )
        
        result = await notification_service.dispatch_cv_notification(
            sample_user_id,
            sample_cv_data,
            user_email="test@example.com",
        )
        
        assert result.email_sent is True
        assert result.whatsapp_sent is False
        assert result.success is True  # At least one succeeded
        assert result.partial_success is True
        assert any("WhatsApp" in e for e in result.errors)


# =============================================================================
# Test: send_test_notification
# =============================================================================

class TestSendTestNotification:
    """Tests for the send_test_notification method."""
    
    @pytest.mark.asyncio
    async def test_send_test_email_success(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should send test email successfully."""
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        notification_service.email_service.send_test_email = AsyncMock(
            return_value=EmailResult(success=True, message_id="test123")
        )
        
        result = await notification_service.send_test_notification(
            sample_user_id,
            channel="email",
            user_email="test@example.com",
        )
        
        assert result["success"] is True
        assert result["message"] == "Test email sent"
    
    @pytest.mark.asyncio
    async def test_send_test_email_no_email_provided(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should fetch email from database if not provided."""
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        # Mock user in database
        mock_user = User(id=sample_user_id, email="db@example.com")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        notification_service.session.execute = AsyncMock(return_value=mock_result)
        
        notification_service.email_service.send_test_email = AsyncMock(
            return_value=EmailResult(success=True, message_id="test123")
        )
        
        result = await notification_service.send_test_notification(
            sample_user_id, channel="email"
        )
        
        assert result["success"] is True
        notification_service.email_service.send_test_email.assert_called_once_with(
            "db@example.com"
        )
    
    @pytest.mark.asyncio
    async def test_send_test_email_user_not_found(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should return error if user email not found."""
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        # No user found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        notification_service.session.execute = AsyncMock(return_value=mock_result)
        
        result = await notification_service.send_test_notification(
            sample_user_id, channel="email"
        )
        
        assert result["success"] is False
        assert result["error"] == "User email not found"
    
    @pytest.mark.asyncio
    async def test_send_test_email_failure(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should return error if email sending fails."""
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        notification_service.email_service.send_test_email = AsyncMock(
            return_value=EmailResult(success=False, error="SMTP error")
        )
        
        result = await notification_service.send_test_notification(
            sample_user_id,
            channel="email",
            user_email="test@example.com",
        )
        
        assert result["success"] is False
        assert result["message"] == "SMTP error"
    
    @pytest.mark.asyncio
    async def test_send_test_whatsapp_success(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should send test WhatsApp successfully."""
        sample_settings.whatsapp_number = "+1234567890"
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        notification_service.whatsapp_service.send_test_message = AsyncMock(
            return_value=WhatsAppResult(success=True, message_sid="wa123")
        )
        
        result = await notification_service.send_test_notification(
            sample_user_id, channel="whatsapp"
        )
        
        assert result["success"] is True
        assert result["message"] == "Test WhatsApp sent"
    
    @pytest.mark.asyncio
    async def test_send_test_whatsapp_no_number(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should return error if WhatsApp number not configured."""
        sample_settings.whatsapp_number = None
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        result = await notification_service.send_test_notification(
            sample_user_id, channel="whatsapp"
        )
        
        assert result["success"] is False
        assert result["error"] == "WhatsApp number not configured"
    
    @pytest.mark.asyncio
    async def test_send_test_whatsapp_failure(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should return error if WhatsApp sending fails."""
        sample_settings.whatsapp_number = "+1234567890"
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        notification_service.whatsapp_service.send_test_message = AsyncMock(
            return_value=WhatsAppResult(success=False, error="Twilio error")
        )
        
        result = await notification_service.send_test_notification(
            sample_user_id, channel="whatsapp"
        )
        
        assert result["success"] is False
        assert result["message"] == "Twilio error"
    
    @pytest.mark.asyncio
    async def test_send_test_unknown_channel(
        self,
        notification_service,
        sample_user_id,
        sample_settings,
    ):
        """Should return error for unknown channel."""
        notification_service.repo.get_or_create = AsyncMock(return_value=sample_settings)
        
        result = await notification_service.send_test_notification(
            sample_user_id, channel="sms"
        )
        
        assert result["success"] is False
        assert result["error"] == "Unknown channel: sms"
