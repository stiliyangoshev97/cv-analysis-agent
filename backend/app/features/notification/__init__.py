"""Notification feature module.

This module provides notification functionality including:
- Email notifications via SMTP
- WhatsApp notifications via Twilio
- User notification preferences management

Exports:
    notification_router: FastAPI router for notification endpoints.
    NotificationService: Orchestration service for notifications.
    NotificationRepository: Database operations for notification settings.
    EmailService: Email sending service.
    WhatsAppService: WhatsApp sending service.

Example:
    from app.features.notification import notification_router, NotificationService
    
    # In main.py
    app.include_router(notification_router, prefix="/api/notifications")
"""

from .notification_routes import router as notification_router
from .notification_service import NotificationService
from .notification_repository import NotificationRepository
from .email_service import EmailService
from .whatsapp_service import WhatsAppService

__all__ = [
    "notification_router",
    "NotificationService",
    "NotificationRepository",
    "EmailService",
    "WhatsAppService",
]
