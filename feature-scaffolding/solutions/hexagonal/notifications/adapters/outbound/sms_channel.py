from notifications.application.ports import ChannelGateway, DeliveryResult
from notifications.domain.notification import Notification


class SMSChannel:
    name = "sms"

    def send(self, notification: Notification) -> DeliveryResult:
        raise NotImplementedError


_: ChannelGateway = SMSChannel()
