# Repository Conventions

These conventions apply to every file in this repository unless a path-specific instructions file overrides them.

## Language and framework

- Python 3.13+. Use standard library or already-installed third-party packages; do not introduce new dependencies without surfacing the addition explicitly.
- The backend uses Flask. Do not propose FastAPI, Django, or any other framework.
- The frontend is vanilla HTML + JavaScript. Do not propose a framework (React, Vue, Svelte) or a build toolchain.

## Naming

- Python: `snake_case` for functions, variables, and module-level constants in `UPPER_SNAKE_CASE`. Classes use `PascalCase`.
- JavaScript: `camelCase` for functions and variables, `UPPER_SNAKE_CASE` for module-level constants.
- File names match their primary export: `users.py` defines `users_bp`, `models.py` defines the data classes.

## Tests

- Use `pytest` only. Do not use `unittest` or write classes derived from `unittest.TestCase`.
- Test files live in `tests/` and are named `test_<subject>.py`.
- Test functions are named `test_<behavior>` and take fixtures as parameters.
- Reuse the existing `client` fixture for any test that exercises the Flask app.

## Response shape

- Successful JSON responses return the resource object directly.
- Error responses return `{"error": "<message>"}` with an appropriate 4xx/5xx status.
- Do not change response shapes in backwards-incompatible ways without an accompanying migration or version note.

## Scope discipline

- Do not modify files outside the directory implied by the task without explicitly stating that you are doing so and why.
- Do not add unrelated cleanup, renames, or refactors to a task that did not ask for them.
