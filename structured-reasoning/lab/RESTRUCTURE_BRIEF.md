# Restructure Brief

## Goal

Move the messy project to a conventional Python `src/` layout without losing functionality. The app must still run and the tests must still pass after the restructure.

## Target Layout

```
messy_project/
├── README.md
├── src/
│   └── messy_project/
│       ├── __init__.py
│       ├── main.py
│       ├── helpers.py
│       └── old_utils.py      # keep only if something still imports from it
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── test_helpers.py
├── config/
│   └── app.yaml              # renamed from top-level config.yaml
├── data/
│   ├── sample.json
│   └── data_loader.yaml      # renamed from data/config.yaml
└── scripts/
    ├── deploy.sh
    ├── deploy_helpers.py     # renamed from scripts/helpers.py
    └── run_tests.sh
```

## Constraints

1. **Do not delete any file.** If a file genuinely has no remaining use, move it to `archive/` rather than removing it. The decision "unused" requires a code-level justification, not an assumption based on a name.

2. **Do not merge files that share a name.** The three `config.yaml` / `helpers.py` name collisions are semantic, not structural. Each file has a distinct purpose; keep them separate after renaming.

3. **Verify imports before moving.** For every file you plan to move or rename, identify every file that references it (by import, by path string, by filename in a shell script) and update those references in the same step.

4. **The tests must pass after the restructure.** `pytest` must succeed from the project root with no path hacks beyond a single conftest.py or a package configuration.

5. **The app must still run.** `python -m messy_project.main` (or an equivalent entry point) must execute successfully after the move. Document the new invocation in the README.

## Explicitly Destructive Operations That Are Not Authorized

- Deleting `old_utils.py` without confirming nothing imports from it
- Consolidating the two `helpers.py` files into one
- Consolidating the two `config.yaml` files into one
- Rewriting the README before the restructure is verified (you will update it last)

## Out of Scope

- Introducing `pyproject.toml`, `setup.cfg`, or any packaging metadata
- Adding type hints, docstrings, or other code improvements
- Changing the behavior of any function
- Adding new tests beyond what is needed to verify the move
