# Reference Scaffolding — Hexagonal Architecture

A worked example of scaffolding the notification dispatcher using a **hexagonal** (ports-and-adapters) pattern: a domain core with no external dependencies, ports (abstract interfaces) owned by the application layer, and adapters on either side (inbound and outbound) that depend *on* the core rather than the other way around.

```
notifications/
├── __init__.py
├── composition_root.py        # wires adapters to ports and returns the app
├── domain/                    # pure domain — no framework dependencies
│   ├── __init__.py
│   ├── notification.py        # entity
│   ├── commands.py            # SendNotification, RetryNotification
│   └── events.py              # NotificationSent, NotificationFailed
├── application/               # use cases + port definitions
│   ├── __init__.py
│   ├── ports.py               # NotificationRepository, AuditRepository, ChannelGateway (abstract)
│   └── use_cases.py           # CreateAndDispatch, GetNotification, ListByRecipient
└── adapters/                  # concrete implementations of ports
    ├── __init__.py
    ├── inbound/
    │   ├── __init__.py
    │   └── rest_api.py        # Flask inbound adapter
    └── outbound/
        ├── __init__.py
        ├── in_memory_notification_repo.py
        ├── in_memory_audit_repo.py
        ├── email_channel.py
        ├── sms_channel.py
        └── push_channel.py
tests/
├── __init__.py
├── test_use_cases.py
└── test_adapters.py
```

## Dependency Direction

```
adapters.inbound  ->  application  ->  domain
adapters.outbound ->  application  ->  domain
composition_root  ->  adapters + application
domain depends on nothing
```

The rule hexagonal enforces that layered does not: *the domain imports nothing from outside.* No Flask, no SQL driver, no HTTP client. If you can swap Flask for FastAPI without editing `domain/` or `application/`, the boundary is correct.

See `../EVALUATION_CHECKLIST.md` for how to audit any hexagonal scaffold against this rule.
