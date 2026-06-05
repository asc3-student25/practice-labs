---
applyTo: "backend/**/*.py"
---

# Backend Instructions

These rules apply to all Python files under `backend/`.

## Blueprints and routing

- Every set of related endpoints lives in its own Blueprint in `backend/api/`.
- Blueprint names match their module (`users_bp` in `users.py`).
- Register new Blueprints in `backend/app.py` inside `create_app()`.
- Every Blueprint has a `url_prefix`. Do not register routes without one.

## Request handling

- Parse JSON with `request.get_json(silent=True) or {}`. Never raise on missing or malformed JSON.
- Validate required fields explicitly and return `400` with an `{"error": "..."}` body if any are missing.
- Use `jsonify()` for every response body, including errors.

## Data access

- Go through `backend/store.py`. Do not instantiate a new `UserStore` in route handlers; use the module-level `store`.
- Never read or write from a file system path inside a route handler.

## Serialization

- Use `dataclasses.asdict()` to serialize dataclass models. Do not hand-roll `to_dict` methods.

## What not to do

- Do not add authentication, authorization, or rate limiting to any endpoint in this lab.
- Do not introduce ORMs or database drivers. The store is in-memory by design.
