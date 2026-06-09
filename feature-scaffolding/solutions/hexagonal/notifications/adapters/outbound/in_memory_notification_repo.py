from notifications.application.ports import NotificationRepository
from notifications.domain.notification import Notification


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
