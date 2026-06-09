from notifications.channels.base import Channel
from notifications.models.notification import Notification
from notifications.repositories.audit_repository import AuditRepository
from notifications.repositories.notification_repository import NotificationRepository
from notifications.services.retry_policy import RetryPolicy


class NotificationService:
    """Orchestrates the dispatch workflow.

    Depends on the repository and channel interfaces, not on any concrete
    implementation. Substituting a new repository or a new channel
    requires no edits to this class.
    """

    def __init__(
        self,
        notifications: NotificationRepository,
        audits: AuditRepository,
        channels: dict[str, Channel],
        retry_policy: RetryPolicy,
    ) -> None:
        self._notifications = notifications
        self._audits = audits
        self._channels = channels
        self._retry_policy = retry_policy

    def create(
        self,
        recipient: str,
        channels: list[str],
        subject: str,
        body: str,
    ) -> Notification:
        raise NotImplementedError

    def get(self, notification_id: str) -> Notification | None:
        raise NotImplementedError

    def list_for_recipient(self, recipient: str) -> list[Notification]:
        raise NotImplementedError

    def dispatch(self, notification_id: str) -> Notification:
        """Run the dispatch workflow for a single notification.

        Walks each requested channel, applies the retry policy to transient
        failures, writes an audit entry for each attempt, and updates the
        notification's status.
        """
        raise NotImplementedError
