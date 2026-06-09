from typing import Protocol

from notifications.models.notification import Notification


class NotificationRepository(Protocol):
    """Persistence interface. The in-memory implementation below is one
    possible substitution; production would swap in a database-backed
    implementation without changing the service layer.
    """

    def save(self, notification: Notification) -> Notification: ...
    def get(self, notification_id: str) -> Notification | None: ...
    def list_by_recipient(self, recipient: str) -> list[Notification]: ...


class InMemoryNotificationRepository:
    def __init__(self) -> None:
        self._notifications: dict[str, Notification] = {}

    def save(self, notification: Notification) -> Notification:
        raise NotImplementedError

    def get(self, notification_id: str) -> Notification | None:
        raise NotImplementedError

    def list_by_recipient(self, recipient: str) -> list[Notification]:
        raise NotImplementedError


_: NotificationRepository = InMemoryNotificationRepository()
