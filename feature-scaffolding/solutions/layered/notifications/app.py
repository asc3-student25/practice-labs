"""Composition root.

Instantiates each layer in dependency order, wires them together, and
returns a Flask application ready to serve. This is the only place in
the codebase that references every layer at once.
"""

from flask import Flask

from notifications.api.routes import create_blueprint
from notifications.channels.email_adapter import EmailAdapter
from notifications.channels.push_adapter import PushAdapter
from notifications.channels.sms_adapter import SMSAdapter
from notifications.repositories.audit_repository import InMemoryAuditRepository
from notifications.repositories.notification_repository import (
    InMemoryNotificationRepository,
)
from notifications.services.notification_service import NotificationService
from notifications.services.retry_policy import RetryPolicy


def create_app() -> Flask:
    notifications_repo = InMemoryNotificationRepository()
    audits_repo = InMemoryAuditRepository()
    channels = {
        "email": EmailAdapter(),
        "sms": SMSAdapter(),
        "push": PushAdapter(),
    }
    service = NotificationService(
        notifications=notifications_repo,
        audits=audits_repo,
        channels=channels,
        retry_policy=RetryPolicy(),
    )

    app = Flask(__name__)
    app.register_blueprint(create_blueprint(service))
    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
