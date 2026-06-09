from notifications.channels.base import Channel, DeliveryResult
from notifications.models.notification import Notification


class SMSAdapter:
    name = "sms"

    def send(self, notification: Notification) -> DeliveryResult:
        """Stub. A real implementation would call an SMS gateway."""
        raise NotImplementedError


_: Channel = SMSAdapter()
