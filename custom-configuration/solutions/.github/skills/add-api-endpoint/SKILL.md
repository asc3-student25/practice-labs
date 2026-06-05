---
name: add-api-endpoint
description: Add a new REST endpoint to the backend, including the route, store access, serialization, and a pytest test that covers success and the primary failure mode.
---

# Add API Endpoint

Use this skill whenever the task is to add a new endpoint to the backend, whether the user uses the words "endpoint", "route", "API", or describes the behavior directly (for example, "let clients list users").

## Steps

1. **Identify the Blueprint.**
   - Find the Blueprint in `backend/api/` whose resource matches the task (for example, `users_bp` for anything under `/api/users`).
   - If no Blueprint matches, create a new file `backend/api/<resource>.py` and register the Blueprint in `create_app()` in `backend/app.py`. State this explicitly before writing code.

2. **Define the route.**
   - Place the route on the identified Blueprint, using the shortest path suffix relative to the Blueprint's `url_prefix`.
   - Use `methods=["GET"]`, `methods=["POST"]`, etc. explicitly. Do not rely on defaults.

3. **Parse input.**
   - For bodies: `data = request.get_json(silent=True) or {}`. Validate required fields. Return `400` with `{"error": "..."}` on a missing field.
   - For path params: use typed converters (`<int:user_id>`). Do not parse integers by hand.
   - For query params: `request.args.get("name")`, with an explicit default.

4. **Touch the store, not the filesystem.**
   - Call methods on the `store` object imported from `backend.store`. If the method does not exist, add it to `UserStore` (or the relevant store class) in the same change.

5. **Serialize the response.**
   - Convert dataclass instances with `dataclasses.asdict()`.
   - Return `jsonify(...)` with an explicit status code.

6. **Write a test.**
   - Add a test in `tests/test_<resource>.py` that reuses the `client` fixture.
   - Cover: the success case (correct status and body shape) and the primary failure mode (missing field, not found, or invalid input).
   - Follow the naming pattern `test_<action>_<expected_outcome>`.

7. **Verify.**
   - Run `pytest` and confirm the new test passes.
   - Run `python -m backend.app` mentally (or literally) and issue a sample request to the new endpoint to confirm the shape.

8. **Report.**
   - Summarize: endpoint added, files changed, test name, sample curl invocation.

## Out of scope for this skill

- Authentication or authorization (not in this project).
- Database migrations — endpoints do not create migrations. If the task also requires a model change, use the migration workflow; it is a separate concern from the endpoint addition.
- Response pagination, sorting, or filtering unless the task asks for them.
