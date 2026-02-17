"""Routes for notification endpoints.

This module defines the FastAPI routes for notification settings management.
Supports BYOK (Bring Your Own Keys) for SMTP and Twilio credentials.

Rate Limits:
    - Settings endpoints: 100/minute (standard)
    - Test notification: 5/hour (prevent spam)

Endpoints:
    GET /: Get current notification settings
    PUT /: Update notification settings
    POST /test/{channel}: Send test notification
    GET /status: Get service configuration status
    DELETE /smtp-config: Clear SMTP configuration
    DELETE /twilio-config: Clear Twilio configuration
    GET /history: Get notification history
    GET /history/stats: Get notification statistics
    GET /history/{notification_id}: Get single notification
    POST /history/{notification_id}/resend: Resend failed notification
    DELETE /history/{notification_id}: Delete notification
"""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request, Query, status

from app.core.rate_limit import limiter, RATE_LIMIT_DEFAULT, RATE_LIMIT_NOTIFICATION_TEST
from .notification_controller import NotificationController
from .notification_dependencies import get_notification_controller
from .notification_schemas import (
    NotificationSettingsResponse,
    NotificationSettingsUpdate,
    NotificationResultResponse,
    NotificationHistoryListResponse,
    NotificationHistoryItem,
    NotificationHistoryStatsResponse,
    ResendNotificationResponse,
)

router = APIRouter(tags=["notifications"])


@router.get(
    "/",
    response_model=NotificationSettingsResponse,
    summary="Get notification settings",
    description="Get the current user's notification preferences including SMTP/Twilio config status.",
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def get_notification_settings(
    request: Request,
    controller: Annotated[NotificationController, Depends(get_notification_controller)],
) -> NotificationSettingsResponse:
    """Get current notification settings."""
    return await controller.get_settings()


@router.put(
    "/",
    response_model=NotificationSettingsResponse,
    summary="Update notification settings",
    description="Update the current user's notification preferences. Supports BYOK for SMTP and Twilio credentials.",
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def update_notification_settings(
    request: Request,
    update_data: NotificationSettingsUpdate,
    controller: Annotated[NotificationController, Depends(get_notification_controller)],
) -> NotificationSettingsResponse:
    """Update notification settings."""
    return await controller.update_settings(update_data)


@router.post(
    "/test/{channel}",
    response_model=NotificationResultResponse,
    summary="Send test notification",
    description="Send a test notification to verify configuration. Uses BYOK credentials if configured.",
)
@limiter.limit(RATE_LIMIT_NOTIFICATION_TEST)
async def send_test_notification(
    request: Request,
    channel: str,
    controller: Annotated[NotificationController, Depends(get_notification_controller)],
) -> NotificationResultResponse:
    """Send a test notification.
    
    Args:
        channel: 'email' or 'whatsapp'
    """
    return await controller.send_test_notification(channel)


@router.get(
    "/status",
    summary="Get service status",
    description="Get the configuration status of notification services (BYOK and server).",
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def get_service_status(
    request: Request,
    controller: Annotated[NotificationController, Depends(get_notification_controller)],
) -> dict:
    """Get notification service configuration status."""
    return await controller.get_service_status()


@router.delete(
    "/smtp-config",
    summary="Clear SMTP configuration",
    description="Clear user's SMTP configuration (BYOK). Falls back to server config.",
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def clear_smtp_config(
    request: Request,
    controller: Annotated[NotificationController, Depends(get_notification_controller)],
) -> dict:
    """Clear SMTP configuration."""
    return await controller.clear_smtp_config()


@router.delete(
    "/twilio-config",
    summary="Clear Twilio configuration",
    description="Clear user's Twilio configuration (BYOK). Falls back to server config.",
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def clear_twilio_config(
    request: Request,
    controller: Annotated[NotificationController, Depends(get_notification_controller)],
) -> dict:
    """Clear Twilio configuration."""
    return await controller.clear_twilio_config()


# =============================================================================
# Notification History Endpoints
# =============================================================================

@router.get(
    "/history",
    response_model=NotificationHistoryListResponse,
    summary="Get notification history",
    description="Get paginated list of sent notifications with filtering options.",
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def get_notification_history(
    request: Request,
    controller: Annotated[NotificationController, Depends(get_notification_controller)],
    type: Annotated[Optional[str], Query(description="Filter by type: 'email' or 'whatsapp'")] = None,
    status: Annotated[Optional[str], Query(description="Filter by status: 'pending', 'sent', or 'failed'")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Results per page")] = 50,
    offset: Annotated[int, Query(ge=0, description="Number of results to skip")] = 0,
) -> NotificationHistoryListResponse:
    """Get notification history with optional filtering."""
    return await controller.get_history(
        notification_type=type,
        status=status,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/history/stats",
    response_model=NotificationHistoryStatsResponse,
    summary="Get notification statistics",
    description="Get aggregate statistics about notification history.",
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def get_notification_stats(
    request: Request,
    controller: Annotated[NotificationController, Depends(get_notification_controller)],
) -> NotificationHistoryStatsResponse:
    """Get notification statistics."""
    return await controller.get_history_stats()


@router.get(
    "/history/{notification_id}",
    response_model=NotificationHistoryItem,
    summary="Get notification by ID",
    description="Get a single notification history entry.",
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def get_notification_by_id(
    request: Request,
    notification_id: uuid.UUID,
    controller: Annotated[NotificationController, Depends(get_notification_controller)],
) -> NotificationHistoryItem:
    """Get single notification by ID."""
    return await controller.get_history_item(notification_id)


@router.post(
    "/history/{notification_id}/resend",
    response_model=ResendNotificationResponse,
    summary="Resend notification",
    description="Resend a failed notification. Uses current BYOK credentials.",
)
@limiter.limit(RATE_LIMIT_NOTIFICATION_TEST)
async def resend_notification(
    request: Request,
    notification_id: uuid.UUID,
    controller: Annotated[NotificationController, Depends(get_notification_controller)],
) -> ResendNotificationResponse:
    """Resend a failed notification."""
    return await controller.resend_notification(notification_id)


@router.delete(
    "/history/{notification_id}",
    summary="Delete notification",
    description="Delete a notification from history.",
)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def delete_notification(
    request: Request,
    notification_id: uuid.UUID,
    controller: Annotated[NotificationController, Depends(get_notification_controller)],
) -> dict:
    """Delete a notification from history."""
    return await controller.delete_history_item(notification_id)
