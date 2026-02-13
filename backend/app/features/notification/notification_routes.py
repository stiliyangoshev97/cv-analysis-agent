"""Routes for notification endpoints.

This module defines the FastAPI routes for notification settings management.

Endpoints:
    GET /: Get current notification settings
    PUT /: Update notification settings
    POST /test/{channel}: Send test notification
    GET /status: Get service configuration status
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from .notification_controller import NotificationController
from .notification_dependencies import get_notification_controller
from .notification_schemas import (
    NotificationSettingsResponse,
    NotificationSettingsUpdate,
    NotificationResultResponse,
)

router = APIRouter(tags=["notifications"])


@router.get(
    "/",
    response_model=NotificationSettingsResponse,
    summary="Get notification settings",
    description="Get the current user's notification preferences.",
)
async def get_notification_settings(
    controller: Annotated[NotificationController, Depends(get_notification_controller)],
) -> NotificationSettingsResponse:
    """Get current notification settings."""
    return await controller.get_settings()


@router.put(
    "/",
    response_model=NotificationSettingsResponse,
    summary="Update notification settings",
    description="Update the current user's notification preferences.",
)
async def update_notification_settings(
    update_data: NotificationSettingsUpdate,
    controller: Annotated[NotificationController, Depends(get_notification_controller)],
) -> NotificationSettingsResponse:
    """Update notification settings."""
    return await controller.update_settings(update_data)


@router.post(
    "/test/{channel}",
    response_model=NotificationResultResponse,
    summary="Send test notification",
    description="Send a test notification to verify configuration.",
)
async def send_test_notification(
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
    description="Get the configuration status of notification services.",
)
async def get_service_status(
    controller: Annotated[NotificationController, Depends(get_notification_controller)],
) -> dict:
    """Get notification service configuration status."""
    return await controller.get_service_status()
