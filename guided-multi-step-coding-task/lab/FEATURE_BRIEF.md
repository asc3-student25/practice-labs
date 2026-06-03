# Feature Brief: Complete the Task Manager API

## Goal

Extend the existing Task Manager API with the missing CRUD operations, a status filter on the list endpoint, and input validation. Add tests covering the new behavior.

## Functional Requirements

### 1. Retrieve a single task

- Route: `GET /tasks/<task_id>`
- Returns the task as JSON with status `200` when it exists.
- Returns status `404` with a JSON body `{"error": "task not found"}` when it does not.

### 2. Update a task

- Route: `PUT /tasks/<task_id>`
- Accepts a JSON body that may contain `title` and/or `status`.
- Updates only the fields provided. Omitted fields stay the same.
- Returns the updated task as JSON with status `200`.
- Returns status `404` when the task does not exist.
- Returns status `400` for invalid input (see Validation below).

### 3. Delete a task

- Route: `DELETE /tasks/<task_id>`
- Returns status `204` with no body when the task is deleted.
- Returns status `404` when the task does not exist.

### 4. Filter the list by status

- Route: `GET /tasks?status=<status>`
- When the `status` query parameter is present, return only tasks with that status.
- When omitted, return all tasks (existing behavior).
- An unknown status value returns an empty list with status `200`.

## Validation Rules

- `title` is required on `POST /tasks` and must be a non-empty string.
- `status` must be one of: `pending`, `in_progress`, `done`.
- Invalid input returns status `400` with a JSON body `{"error": "<message>"}`.
- These rules apply to both `POST /tasks` and `PUT /tasks/<task_id>`.

## Test Coverage

Add tests in `tests/test_app.py` that cover each new endpoint, the status filter, and both the success and failure paths for validation and not-found cases.

## Out of Scope

- Persistence to disk or a database. The in-memory store is sufficient.
- Authentication or authorization.
- Pagination or sorting on the list endpoint.
