# Baseline Sketch

Fill this in **before** you prompt Copilot. Once you start a scaffolding run, the run will shape your judgment about what "looks right" — the point of the baseline is to capture your expectation uncontaminated by the agent's output.

Copy this template to `BASELINE.md` at the repository root and edit there. Leave this template file unchanged so later runs can reuse it.

---

## Expected Directory Layout

Sketch the tree you would produce if you were scaffolding this microservice by hand. Include every module you expect and the intended purpose of each.

```
notifications/
├── ...
tests/
├── ...
```

## Expected Public Interfaces

For each major module in the sketch, write the function or class signatures you would expect, with type hints. Interface, not implementation.

### `notifications/<module>.py`

```python
def example(arg: str) -> None: ...
```

### `notifications/<other>.py`

```python
...
```

## Dependency Direction

Draw (in text) which modules depend on which. This is what you will audit most carefully in the generated scaffolding.

```
api -> service -> repository
                \-> channels
```

## Architectural Pattern

One or two sentences naming the pattern you are defaulting to (layered, hexagonal, event-driven, CQRS, pipes-and-filters) and why.

## Decisions You Are Leaving to Copilot

List the structural choices you deliberately did *not* make, so you can observe how the agent resolves them.

- (for example) Whether retry scheduling lives inside the service or as a separate module
- (for example) Whether channel adapters implement a shared protocol or extend a base class
- (for example) Whether the audit log is a sibling module or a sub-module of the repository layer
