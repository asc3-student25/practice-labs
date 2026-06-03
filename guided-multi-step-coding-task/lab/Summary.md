Step-by-step summary of what I changed and why, grouped by file.

Step 1: Data-layer foundation
- File: AIC-1102/LabFiles/guided-multi-step-coding-task/lab/storage.py
- What changed:
1. Extended list_all to accept optional status filtering.
2. Added get(task_id) to retrieve one task.
3. Added update(task_id, title=None, status=None) for partial updates.
4. Added delete(task_id) returning True/False for delete success.
- Why:
1. The feature brief requires single-task retrieval, update, delete, and status-filtered listing.
2. Keeping these as store operations lets route handlers stay focused on HTTP behavior and validation, while storage remains the single in-memory data API.

Step 2: GET/POST API behavior + shared validation
- File: AIC-1102/LabFiles/guided-multi-step-coding-task/lab/app.py
- What changed:
1. Added shared status constant with allowed values: pending, in_progress, done.
2. Added shared error response helper to standardize JSON error bodies.
3. Added shared payload validator used by request handlers.
4. Updated GET /tasks to support ?status=... filtering.
5. Implemented GET /tasks/<task_id> with 200 on hit, 404 with task not found on miss.
6. Updated POST /tasks to enforce title and status validation before create.
7. Incorporated the requirement update: invalid status returns 422 and includes valid_statuses in response body.
- Why:
1. Shared helpers prevent duplicated validation/error logic and keep behavior consistent.
2. GET changes satisfy list filtering and single-task retrieval requirements.
3. POST changes satisfy input validation and error-contract requirements, including your updated 422 status rule for invalid status.

Step 3: PUT/DELETE API behavior
- File: AIC-1102/LabFiles/guided-multi-step-coding-task/lab/app.py
- What changed:
1. Added PUT /tasks/<task_id> for partial updates.
2. PUT returns 404 when task is missing.
3. PUT reuses shared validator so invalid status returns 422 with valid_statuses.
4. Added DELETE /tasks/<task_id> returning 204 on success.
5. DELETE returns 404 when task is missing.
- Why:
1. Completes the missing CRUD endpoints in the brief.
2. Reusing validator ensures POST and PUT follow the same validation contract and your updated status-error behavior.

Step 4: Full test coverage for required behaviors
- File: AIC-1102/LabFiles/guided-multi-step-coding-task/lab/tests/test_app.py
- What changed:
1. Expanded tests for GET /tasks/<id> success and not found.
2. Added PUT tests for title-only, status-only, combined updates, invalid input, and not found.
3. Added DELETE tests for success and not found.
4. Added list filter tests for known status, unknown status, and no filter.
5. Added POST validation tests for missing/invalid title and invalid status.
6. Updated fixture to reset both tasks and ID counter for deterministic tests.
- Why:
1. The brief explicitly asks for success and failure coverage for new endpoints, filtering, validation, and not-found cases.
2. Deterministic IDs improve reliability and reduce flaky assertions.

Step 5: Verification
- Command executed in lab folder: pytest -q
- Result: 21 passed
- Why:
1. Confirms end-to-end implementation aligns with required API behavior and validation contracts.
2. Confirms your changed validation rule (invalid status -> 422 + valid_statuses) is covered and passing.