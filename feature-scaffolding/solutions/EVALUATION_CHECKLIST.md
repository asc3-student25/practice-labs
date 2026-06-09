# Scaffolding Evaluation Checklist

Use this checklist when auditing the scaffolding Copilot generates. The questions are ordered from hard structural properties (either yes or no) to judgment calls (reasonable minds may differ).

## Hard Criteria

### Directory separation

- [ ] Does every top-level source directory have a single, namable responsibility? (If a directory's contents require the word "and" to describe, it probably holds two responsibilities.)
- [ ] Is there exactly one composition root — one file that wires every layer/adapter and is the only file importing from the entire project?
- [ ] Are the REST routes *thin* — no business rules in the route handlers?

### Dependency direction

- [ ] Does the domain (or "models" in layered) depend on no other internal package?
- [ ] Do adapters (or "services" calling repositories) depend on interfaces, not concrete implementations?
- [ ] If the framework (Flask) were removed, would the domain and service/application layer still compile?

### Interface definition

- [ ] Is each substitutable component (repository, channel adapter) defined against an explicit interface (Protocol, abstract base class, or equivalent)?
- [ ] Does at least one static conformance check exist per concrete implementation (for example, `_: Channel = EmailAdapter()` at module scope)?
- [ ] Are interfaces narrow — do they contain only the methods the caller actually uses?

### Naming

- [ ] Do module names describe their role, not their implementation? ("repository" good, "db_helper" weak.)
- [ ] Is the same noun used the same way across modules? ("Notification" everywhere, not "Notification" in one file and "Message" in another.)

### Test layout

- [ ] Does the `tests/` tree mirror the source tree? A reader should be able to guess the test file from the module path.
- [ ] Is there at least one stub test per public surface (API, service/use case, repository, channel adapter)?

## Soft Criteria (Judgment Calls)

These are places where reasonable people disagree. Record the choice and your reasoning rather than a pass/fail.

- Where does the retry policy live — inside the service, as a sibling module, or in its own package?
- Is the audit log a sibling of the notification repository or a sub-module of it?
- Are inbound and outbound adapters separated (hexagonal style) or mixed (layered style)?
- Is the `models/` or `domain/` package shared across layers, or does each layer have its own types and map between them?

## Pattern-Specific Checks

### Layered

- [ ] Each layer only imports from layers below it. `api` imports from `services`; `services` imports from `repositories` and `channels`; none of those import from `api`.
- [ ] No layer skips a layer. `api` does not import from `repositories` directly.
- [ ] Models are shared downward; they never import from services, repositories, or api.

### Hexagonal

- [ ] The domain imports nothing outside `domain/`. No Flask, no database driver, no HTTP client.
- [ ] Ports live in the application layer, not the adapter layer.
- [ ] Adapters depend on ports; ports do not depend on adapters.
- [ ] The composition root is the only file that imports from both `adapters/` and `application/use_cases`.

### Event-Driven (if Copilot produced this pattern)

- [ ] Events are defined as immutable data classes.
- [ ] Handlers register against event types, not function calls into other handlers.
- [ ] The event bus is a port the application depends on; concrete implementations (in-memory queue, Redis Streams) are adapters.

## Scoring

This is not a pass/fail test. Count how many hard criteria passed, note every soft criterion choice, and identify any pattern-specific check the scaffolding got wrong. Then ask:

1. Is the directional discipline (what depends on what) right?
2. Could I swap one adapter for another without editing the core?
3. Could a reader understand the purpose of every directory from its name alone?

If all three are yes, the scaffolding is good regardless of which pattern Copilot picked. If any is no, identify the specific file or import line that caused the answer to be no — *that* is the concrete critique to record in `AUDIT.md`.
