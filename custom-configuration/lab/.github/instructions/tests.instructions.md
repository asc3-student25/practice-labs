---
applyTo: "tests/**/*.py"
---

# Test Instructions

These rules apply to all Python files under `tests/`.

## Framework

- Use `pytest`. Do not use `unittest` classes.
- Use function-based tests. Each test is a top-level function named `test_<behavior>`.

## Fixtures

- Reuse the `client` fixture defined in `tests/test_users.py` rather than redefining it. If you need a variant, parameterize the existing fixture.
- Clear shared state (the in-memory `store._users`) inside the `client` fixture, not inside individual tests.

## Assertions

- Assert on status codes explicitly: `assert response.status_code == 201`.
- Assert on response bodies with `response.get_json()`, not `response.data` or `response.text`.
- Do not use `assert response.ok`; it masks the distinction between 2xx codes.

## Test naming

- `test_<action>_<expected_outcome>`, for example: `test_create_user_returns_201`, `test_get_user_not_found`.
- One behavior per test. If a test needs more than three assertions, split it.

## What not to do

- Do not add mocking frameworks (`unittest.mock`, `pytest-mock`) to this lab's tests. The store is in-memory; prefer exercising real code paths.
- Do not add tests that depend on external services, the filesystem, or sleep timing.
