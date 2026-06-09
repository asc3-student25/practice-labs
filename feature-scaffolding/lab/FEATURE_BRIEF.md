# Feature Brief: Notification Dispatcher

## Summary

A microservice that accepts notification requests, routes each request to one or more delivery channels (email, SMS, push), tracks delivery status, and retries failed deliveries with exponential backoff.

## Capabilities

### Public API

- `POST /notifications` — create a new notification. Body:
  ```json
  {
    "recipient": "user-123",
    "channels": ["email", "sms"],
    "subject": "Your order has shipped",
    "body": "Tracking: ZZ123..."
  }
  ```
  Returns `201` with the created notification including its generated `id` and initial status.

- `GET /notifications/<id>` — retrieve current status of a notification.

- `GET /notifications?recipient=<id>` — list notifications for a recipient.

### Status Lifecycle

Every notification tracks one of the following statuses:

- `pending` — accepted but not yet dispatched
- `sending` — dispatch in progress
- `sent` — successfully delivered on at least one channel
- `partial` — succeeded on some channels, failed on others
- `failed` — all channels failed after retries exhausted
- `retrying` — at least one channel failed and is awaiting retry

Every status change produces an audit log entry with timestamp, previous status, new status, and reason.

### Delivery Channels

The service supports three channels: `email`, `sms`, `push`. Each channel:

- Has its own adapter
- Is pluggable (adding a fourth channel requires only a new adapter, not changes to the core workflow)
- Reports success or a categorized failure (`transient`, `permanent`) back to the dispatch workflow

For this lab the adapters are **stubs** — no real email or SMS is sent. The structure must nonetheless be present.

### Retry Policy

- Transient failures retry up to 3 times with exponential backoff (1s, 2s, 4s)
- Permanent failures do not retry
- The retry scheduler is abstracted behind an interface (in-process task queue is fine for this lab)

### Persistence

- Notifications persist in a repository. For this lab the repository is in-memory, but its interface must be defined so a real store (Redis, Postgres, etc.) could be substituted.

### Audit Log

- Every status change and every channel attempt produces an audit entry
- Audit entries persist in a separate store (also in-memory for this lab, behind a repository interface)

## Non-Functional Requirements

- Written in Python 3.13+. Use Flask for the REST layer.
- No persistent storage. The in-memory implementations are the *only* implementations in scope; the interfaces must be defined such that persistent stores could be added without changing the workflow code.
- A test layout must exist alongside the source, even if the tests are empty.
- The module layout must make the direction of dependency obvious: tell a reader which module depends on which.

## Out of Scope

- Authentication and authorization
- Rate limiting
- Deduplication
- Webhooks or admin endpoints
- Real delivery to any channel
- Database migrations
- Deployment manifests (Docker, Helm, Terraform)
- Monitoring and metrics (beyond audit logging)

## Architectural Pattern

The brief does not prescribe a pattern. Whatever pattern Copilot chooses, the resulting scaffolding must satisfy:

- Channel adapters are pluggable without editing the workflow code
- Persistence is abstracted so the in-memory store can be swapped later
- The retry policy is a separate concern from the dispatch workflow
- The REST layer is a thin translation between HTTP and the workflow, not a place where business rules live

The choice of *how* to achieve that — layered, hexagonal, event-driven, or hybrid — is Copilot's to make. Your job is to audit the choice.
