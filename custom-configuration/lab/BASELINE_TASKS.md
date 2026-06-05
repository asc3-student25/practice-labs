# Baseline Tasks

Run each of the following three tasks against Copilot in order. Record the response and your evaluation in `RESULTS.md` for every run.

You will run this set **seven** times during the lab:

1. With no configuration (baseline)
2. After adding `.github/copilot-instructions.md`
3. After adding path-specific `.github/instructions/*.instructions.md`
4. After adding `AGENTS.md`
5. After configuring Copilot Content Exclusion
6. After adding an Agent Skill
7. Final verification run

You do not need to accept the generated code. The point is to *compare* Copilot's output across the runs.

## Task 1 — Add a list endpoint

Prompt (issue in Chat, Agent Mode, whichever matches your workflow):

> Add a `GET /api/users` endpoint to the backend that returns all users as JSON. Follow the conventions of the existing endpoints.

Evaluate:

- Did Copilot use Flask (matching the codebase) or propose another framework?
- Did it match the naming conventions of the existing file?
- Did it add error handling, validation, or response shaping in line with the existing endpoint?
- Did it touch files outside `backend/api/users.py`?

## Task 2 — Add a test for the list endpoint

Prompt:

> Write a pytest test for the `GET /api/users` endpoint. Follow the conventions of the existing tests.

Evaluate:

- Did Copilot use `pytest` fixtures, or did it import `unittest`?
- Did it match the file / function naming patterns of the existing tests?
- Did it use the existing `client` fixture or invent its own?

## Task 3 — Propose a schema change

Prompt:

> Add an `is_active` boolean field to the User model that defaults to `True`. Propose how to implement this change across the codebase.

Evaluate:

- Did Copilot edit an existing migration file or propose a *new* migration?
- Did it update the model, the API serializer, and the tests?
- Did it flag the migration directory as append-only, or did it silently treat migrations as editable?

## Recording Template

For each run, append a section to `RESULTS.md` in this shape:

```
## Run N: <config layer added>

### Task 1
- Output summary:
- Evaluation:

### Task 2
- Output summary:
- Evaluation:

### Task 3
- Output summary:
- Evaluation:

### Overall delta vs previous run:
```
