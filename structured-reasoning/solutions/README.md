# Messy Project (restructured)

The restructured reference solution for the lab. The project now uses a `src/` layout with every name collision resolved.

## Layout

```
.
├── src/
│   └── messy_project/
│       ├── __init__.py
│       ├── main.py
│       ├── helpers.py
│       └── old_utils.py
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── test_helpers.py
├── config/
│   └── app.yaml
├── data/
│   ├── sample.json
│   └── data_loader.yaml
├── scripts/
│   ├── deploy.sh
│   ├── deploy_helpers.py
│   └── run_tests.sh
├── conftest.py
└── requirements.txt
```

## Running

After the restructure, `messy_project` lives under `src/`. Python will not find it with a bare `python -m` call; set `PYTHONPATH` so the import resolves:

```bash
PYTHONPATH=src python -m messy_project.main
pytest
```

`pytest` works without `PYTHONPATH` because `conftest.py` at the repository root adds `src/` to `sys.path` for the test run — but that machinery only runs under `pytest`. Direct `python -m` invocations need `PYTHONPATH=src` (or install the package in editable mode with `pip install -e .` once a `pyproject.toml` is added).
