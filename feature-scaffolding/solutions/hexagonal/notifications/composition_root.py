"""Composition root.

Instantiates concrete outbound adapters, wires them into use cases
through their port interfaces, constructs the inbound adapter, and
returns a Flask app. This is the *only* module that imports from every
subtree.
"""

from flask import Flask

from notifications.adapters.inbound.rest_api import create_blueprint
from notifications.adapters.outbound.email_channel import EmailChannel
from notifications.adapters.outbound.in_memory_audit_repo import (
    InMemoryAuditRepository,
)
from notifications.adapters.outbound.in_memory_notification_repo import (
    InMemoryNotificationRepository,
)
from notifications.adapters.outbound.push_channel import PushChannel
from notifications.adapters.outbound.sms_channel import SMSChannel
from notifications.application.use_cases import (
    CreateAndDispatch,
    GetNotification,
    ListByRecipient,
)


def build_app() -> Flask:
    notifications_repo = InMemoryNotificationRepository()
    audits_repo = InMemoryAuditRepository()
    channels = {
        "email": EmailChannel(),
        "sms": SMSChannel(),
        "push": PushChannel(),
    }

    create_and_dispatch = CreateAndDispatch(
        notifications=notifications_repo,
        audits=audits_repo,
        channels=channels,
    )
    get_notification = GetNotification(notifications=notifications_repo)
    list_by_recipient = ListByRecipient(notifications=notifications_repo)

    app = Flask(__name__)
    app.register_blueprint(
        create_blueprint(create_and_dispatch, get_notification, list_by_recipient)
    )
    return app


if __name__ == "__main__":
    build_app().run(debug=True, port=5000)
