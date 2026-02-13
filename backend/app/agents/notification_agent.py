"""Notification Agent for alerts (stub for Phase 5).

This agent will handle notification tasks including email and
WhatsApp alerts when CVs meet certain thresholds.

Tasks:
    SEND_EMAIL: Send email notification.
    SEND_WHATSAPP: Send WhatsApp notification.
    CHECK_THRESHOLD: Check if CV score triggers notification.
    DISPATCH_NOTIFICATION: Route to appropriate notification channel.

Note:
    This is a stub implementation. Full implementation in Phase 5.

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
from typing import Set

from .base import BaseAgent, AgentContext
from .messages import AgentMessage, AgentResult, TaskType

logger = logging.getLogger(__name__)


class NotificationAgent(BaseAgent):
    """Agent for notification handling (stub implementation).
    
    Will be fully implemented in Phase 5 to support:
    - Email notifications via SMTP/SendGrid
    - WhatsApp notifications via Twilio
    - Configurable threshold triggers
    - User notification preferences
    
    Supported Tasks:
        - CHECK_THRESHOLD: Check if score triggers notification
        - SEND_EMAIL: Send email (stub)
        - SEND_WHATSAPP: Send WhatsApp (stub)
        - DISPATCH_NOTIFICATION: Route to channel (stub)
    
    Example:
        >>> agent = NotificationAgent(context)
        >>> result = await agent.execute(AgentMessage(
        ...     task_type=TaskType.CHECK_THRESHOLD,
        ...     payload={"score": 85, "threshold": 80}
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
    
    # Default configuration (will be moved to settings in Phase 5)
    DEFAULT_THRESHOLD = 70  # Notify if score >= 70%
    
    def __init__(self, context: AgentContext) -> None:
        """Initialize notification agent.
        
        Args:
            context: Shared AgentContext with repositories.
        """
        super().__init__(context)
    
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
        
        Compares the CV score against the configured threshold
        to determine if notifications should be sent.
        
        Args:
            message: AgentMessage with score and optional threshold.
        
        Returns:
            AgentResult with should_notify and reason.
        """
        score = message.payload.get("score")
        threshold = message.payload.get("threshold", self.DEFAULT_THRESHOLD)
        cv_id = message.cv_id or message.payload.get("cv_id")
        
        if score is None:
            return AgentResult.fail("Missing score in payload", self.name)
        
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
        """Send email notification (stub).
        
        TODO Phase 5: Implement with SMTP or SendGrid.
        
        Args:
            message: AgentMessage with email details.
        
        Returns:
            AgentResult indicating stub status.
        """
        self._logger.info("Email notification requested (stub - not implemented)")
        
        return AgentResult.skip(
            reason="Email notifications not yet implemented (Phase 5)",
            agent_name=self.name,
        )
    
    async def _send_whatsapp(self, message: AgentMessage) -> AgentResult:
        """Send WhatsApp notification (stub).
        
        TODO Phase 5: Implement with Twilio.
        
        Args:
            message: AgentMessage with WhatsApp details.
        
        Returns:
            AgentResult indicating stub status.
        """
        self._logger.info("WhatsApp notification requested (stub - not implemented)")
        
        return AgentResult.skip(
            reason="WhatsApp notifications not yet implemented (Phase 5)",
            agent_name=self.name,
        )
    
    async def _dispatch_notification(self, message: AgentMessage) -> AgentResult:
        """Route notification to appropriate channel (stub).
        
        Will determine which notification channels are enabled
        and dispatch to each.
        
        TODO Phase 5:
        - Check user notification preferences
        - Support multiple channels
        - Handle failures gracefully
        
        Args:
            message: AgentMessage with notification content.
        
        Returns:
            AgentResult indicating stub status.
        """
        cv_id = message.cv_id or message.payload.get("cv_id")
        score = message.payload.get("score")
        
        self._logger.info(
            f"Notification dispatch requested for CV {cv_id} "
            f"with score {score} (stub - not implemented)"
        )
        
        return AgentResult.skip(
            reason="Notification dispatch not yet implemented (Phase 5)",
            agent_name=self.name,
        )
