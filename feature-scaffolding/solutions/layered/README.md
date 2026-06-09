# Reference Scaffolding — Layered Architecture

A worked example of scaffolding the notification dispatcher using a **layered** pattern: each directory is a horizontal layer, higher layers depend on lower layers, lower layers do not reach upward.

```
notifications/
├── __init__.py
├── app.py                     # composition root: wires layers and starts Flask
├── api/                       # transport layer
│   ├── __init__.py
│   └── routes.py              # Flask routes -> service layer
├── services/                  # workflow / business logic
│   ├── __init__.py
│   ├── notification_service.py
│   └── retry_policy.py
├── repositories/              # persistence layer (abstraction + in-memory impl)
│   ├── __init__.py
│   ├── notification_repository.py
│   └── audit_repository.py
├── channels/                  # outbound adapters (one per delivery channel)
│   ├── __init__.py
│   ├── base.py                # Channel protocol + FailureKind enum
│   ├── email_adapter.py
│   ├── sms_adapter.py
│   └── push_adapter.py
└── models/                    # shared domain entities (pure data)
    ├── __init__.py
    └── notification.py
tests/
├── __init__.py
├── test_api.py
├── test_service.py
├── test_repository.py
└── test_channels.py
```

## Dependency Direction

```
api -> services -> repositories
                \-> channels -> models
models stands alone (imported by every layer, depends on none)
```

This is a reference, not the *only* correct layered scaffolding. Acceptable variants move the audit log into `repositories/`, combine `models/` with `services/`, or flatten `channels/` under `services/`. See `../EVALUATION_CHECKLIST.md` for the objective criteria.
