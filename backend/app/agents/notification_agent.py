"""Notification Agent for email and WhatsApp alerts.

This agent handles notification tasks including email and
WhatsApp alerts when CVs meet certain thresholds.

Tasks:
    SEND_EMAIL: Send email notification.
    SEND_WHATSAPP: Send WhatsApp notification.
    CHECK_THRESHOLD: Check if CV score triggers notification.
    DISPATCH_NOTIFICATION: Route to appropriate notification channel.

Example:
    Using the notification agent::
    
        agent = NotificationAgent(context)
        result = await agent.execute(AgentMessage(
            task_type=TaskType.CHECK_THRESHOLD,
            payload={"cv_id": uuid, "score": 85},
            metadata={"user_id": uuid}
        ))
"""

import logging
import uuid
from typing import Set, Optional

from .base import BaseAgent, AgentContext
from .messages import AgentMessage, AgentResult, TaskType

logger = logging.getLogger(__name__)


class NotificationAgent(BaseAgent):
    """Agent for notification handling.
    
    Integrates with NotificationService to send email and WhatsApp
    notifications based on user preferences and CV scores.
    
    Supported Tasks:
        - CHECK_THRESHOLD: Check if score triggers notification
        - SEND_EMAIL: Send email notification
        - SEND_WHATSAPP: Send WhatsApp notification
        - DISPATCH_NOTIFICATION: Route to enabled channels
    
    Example:
        >>> agent = NotificationAgent(context)
        >>> result = await agent.execute(AgentMessage(
        ...     task_type=TaskType.CHECK_THRESHOLD,
        ...     payload={"score": 85},
        ...     metadata={"user_id": user_id}
        ... ))
        >>> print(result.data["should_notify"])  # True
    """
    
    name = "notification_agent"
    supported_tasks: Set[TaskType] = {
        TaskType.SEND_EMAIL,
        TaskType.SEND_WHATSAPP,
        TaskType.CHECK_THRESHOLD,
        TaskType.DISPATCH_NOTIFICATION,
    }
    
    # Default threshold if user has no settings
    DEFAULT_THRESHOLD = 70
    
    def __init__(self, context: AgentContext) -> None:
        """Initialize notification agent.
        
        Args:
            context: Shared AgentContext with repositories.
        """
        super().__init__(context)
        self._notification_service = None
    
    @property
    def notification_service(self):
        """Get or create NotificationService instance."""
        if self._notification_service is None:
            from app.features.notification.notification_service import NotificationService
            self._notification_service = NotificationService(self.context.session)
        return self._notification_service
    
    async def process(self, message: AgentMessage) -> AgentResult:
        """Process a notification task.
        
        Routes to appropriate handler based on task type.
        
        Args:
            message: AgentMessage with notification data.
        
        Returns:
            AgentResult with notification status.
        """
        if message.task_type == TaskType.CHECK_THRESHOLD:
            return await self._check_threshold(message)
        elif message.task_type == TaskType.SEND_EMAIL:
            return await self._send_email(message)
        elif message.task_type == TaskType.SEND_WHATSAPP:
            return await self._send_whatsapp(message)
        elif message.task_type == TaskType.DISPATCH_NOTIFICATION:
            return await self._dispatch_notification(message)
        else:
            return AgentResult.fail(
                f"Unknown task type: {message.task_type}",
                agent_name=self.name,
            )
    
    async def _check_threshold(self, message: AgentMessage) -> AgentResult:
        """Check if CV score triggers notification.
        
        Uses user's notification settings to determine threshold.
        
        Args:
            message: AgentMessage with score and user_id.
        
        Returns:
            AgentResult with should_notify and reason.
        """
        score = message.payload.get("score")
        user_id = message.user_id
        cv_id = message.cv_id or message.payload.get("cv_id")
        
        if score is None:
            return AgentResult.fail("Missing score in payload", self.name)
        
        threshold = self.DEFAULT_THRESHOLD
        if user_id:
            try:
                should_notify, threshold = await self.notification_service.check_threshold(
                    user_id=user_id,
                    score=score,
                )
            except Exception as e:
                self._logger.warning(f"Could not check user threshold: {e}")
                should_notify = score >= threshold
        else:
            should_notify = score >= threshold
        
        self._logger.info(
            f"Threshold check: score={score}, threshold={threshold}, "
            f"notify={should_notify}"
        )
        
        if should_notify:
            return AgentResult.ok(
                data={
                    "should_notify": True,
                    "score": score,
                    "threshold": threshold,
                    "cv_id": str(cv_id) if cv_id else None,
                    "reason": f"Score {score}% meets threshold {threshold}%",
                },
                agent_name=self.name,
                next_task=TaskType.DISPATCH_NOTIFICATION,
            )
        else:
            return AgentResult.ok(
                data={
                    "should_notify": False,
                    "score": score,
                    "threshold": threshold,
                    "cv_id": str(cv_id) if cv_id else None,
                    "reason": f"Score {score}% below threshold {threshold}%",
                },
                agent_name=self.name,
            )
    
    async def _send_email(self, message: AgentMessage) -> AgentResult:
        """Send email notification.
        
        Args:
            message: AgentMessage with cv_data and user email.
        
        Returns:
            AgentResult with send status.
        """
        from app.features.notification.email_service import EmailService
        from app.features.notification.notification_schemas import CVNotificationData
        
        to_email = message.payload.get("to_email")
        cv_data_dict = message.payload.get("cv_data", {})
        
        if not to_email:
            return AgentResult.fail("Missing to_email in payload", self.name)
        
        cv_data = CVNotificationData(
            cv_id=cv_data_dict.get("cv_id", "unknown"),
            filename=cv_data_dict.get("filename", "unknown.pdf"),
            candidate_name=cv_data_dict.get("candidate_name"),
            score=cv_data_dict.get("score", 0),
            passed=cv_data_dict.get("passed", False),
            summary=cv_data_dict.get("summary", "No summary available"),
        )
        
        email_service = EmailService()
        
        if not email_service.is_configured:
            return AgentResult.skip(
                reason="Email service not configured",
                agent_name=self.name,
            )
        
        self._logger.info(f"Sending email notification to {to_email}")
        
        result = await email_service.send_cv_notification(
            to_email=to_email,
            cv_data=cv_data,
        )
        
        if result.success:
            return AgentResult.ok(
                data={
                    "channel": "email",
                    "to": to_email,
                    "message_id": result.message_id,
                },
                agent_name=self.name,
            )
        else:
            return AgentResult.fail(
                error=f"Email failed: {result.error}",
                agent_name=self.name,
            )
    
    async def _send_whatsapp(self, message: AgentMessage) -> AgentResult:
        """Send WhatsApp notification.
        
        Args:
            message: AgentMessage with cv_data and phone number.
        
        Returns:
            AgentResult with send status.
        """
        from app.features.notification.whatsapp_service import WhatsAppService
        from app.features.notification.notification_schemas import CVNotificationData
        
        to_number = message.payload.get("to_number")
        cv_data_dict = message.payload.get("cv_data", {})
        
        if not to_number:
            return AgentResult.fail("Missing to_number in payload", self.name)
        
        cv_data = CVNotificationData(
            cv_id=cv_data_dict.get("cv_id", "unknown"),
            filename=cv_data_dict.get("filename", "unknown.pdf"),
            candidate_name=cv_data_dict.get("candidate_name"),
            score=cv_data_dict.get("score", 0),
            passed=cv_data_dict.get("passed", False),
            summary=cv_data_dict.get("summary", "No summary available"),
        )
        
        whatsapp_service = WhatsAppService()
        
        if not whatsapp_service.is_configured:
            return AgentResult.skip(
                reason="WhatsApp service not configured",
                agent_name=self.name,
            )
        
        self._logger.info(f"Sending WhatsApp notification to {to_number}")
        
        result = await whatsapp_service.send_cv_notification(
            to_number=to_number,
            cv_data=cv_data,
        )
        
        if result.success:
            return AgentResult.ok(
                data={
                    "channel": "whatsapp",
                    "to": to_number,
                    "message_sid": result.message_sid,
                },
                agent_name=self.name,
            )
        else:
            return AgentResult.fail(
                error=f"WhatsApp failed: {result.error}",
                agent_name=self.name,
            )
    
    async def _dispatch_notification(self, message: AgentMessage) -> AgentResult:
        """Dispatch notification to all enabled channels.
        
        Uses NotificationService to send to email and/or WhatsApp
        based on user preferences.
        
        Args:
            message: AgentMessage with cv_data and user_id.
        
        Returns:
            AgentResult with dispatch status.
        """
        from app.features.notification.notification_schemas import CVNotificationData
        
        user_id = message.user_id
        cv_id = message.cv_id or message.payload.get("cv_id")
        
        if not user_id:
            return AgentResult.skip(
                reason="No user_id provided for notification dispatch",
                agent_name=self.name,
            )
        
        cv_data = CVNotificationData(
            cv_id=str(cv_id) if cv_id else message.payload.get("cv_id", "unknown"),
            filename=message.payload.get("filename", "unknown.pdf"),
            candidate_name=message.payload.get("candidate_name"),
            score=message.payload.get("score", 0),
            passed=message.payload.get("passed", False),
            summary=message.payload.get("summary", "CV evaluation completed"),
        )
        
        self._logger.info(
            f"Dispatching notification for CV {cv_data.cv_id} "
            f"with score {cv_data.score}%"
        )
        
        try:
            result = await self.notification_service.dispatch_cv_notification(
                user_id=user_id,
                cv_data=cv_data,
            )
            
            # Commit notification history entries if any were created
            if result.should_notify:
                await self.context.session.commit()
            
            return AgentResult.ok(
                data={
                    "should_notify": result.should_notify,
                    "score": result.score,
                    "threshold": result.threshold,
                    "email_sent": result.email_sent,
                    "whatsapp_sent": result.whatsapp_sent,
                    "channels_attempted": result.channels_attempted,
                    "errors": result.errors,
                },
                agent_name=self.name,
            )
            
        except Exception as e:
            self._logger.error(f"Notification dispatch failed: {e}")
            return AgentResult.fail(
                error=f"Dispatch failed: {e}",
                agent_name=self.name,
            )
