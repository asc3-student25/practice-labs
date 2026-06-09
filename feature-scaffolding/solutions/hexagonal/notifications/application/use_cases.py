"""Use cases: orchestrate the domain through ports.

Use cases depend on ports (application.ports) and the domain package.
They do NOT import anything from adapters. The composition root wires
concrete adapters into these use cases at construction time.
"""

from notifications.application.ports import (
    AuditRepository,
    ChannelGateway,
    NotificationRepository,
)
from notifications.domain.commands import SendNotification
from notifications.domain.notification import Notification


class CreateAndDispatch:
    def __init__(
        self,
        notifications: NotificationRepository,
        audits: AuditRepository,
        channels: dict[str, ChannelGateway],
        max_attempts: int = 3,
        base_delay_seconds: float = 1.0,
    ) -> None:
        self._notifications = notifications
        self._audits = audits
        self._channels = channels
        self._max_attempts = max_attempts
        self._base_delay_seconds = base_delay_seconds

    def execute(self, command: SendNotification) -> Notification:
        raise NotImplementedError


class GetNotification:
    def __init__(self, notifications: NotificationRepository) -> None:
        self._notifications = notifications

    def execute(self, notification_id: str) -> Notification | None:
        raise NotImplementedError


class ListByRecipient:
    def __init__(self, notifications: NotificationRepository) -> None:
        self._notifications = notifications

    def execute(self, recipient: str) -> list[Notification]:
        raise NotImplementedError
