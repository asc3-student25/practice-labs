# Messy Project

A small application that has grown organically and now has a layout problem: source, tests, config, scripts, and data are all at the top level or nearly so, and some filenames collide semantically across directories.

This lab now uses a conventional `src/` layout while preserving runtime behavior and test behavior.

## Current Layout

```
messy_project/
├── README.md
├── config/
│   └── app.yaml            # application configuration
├── conftest.py             # pytest src-path bootstrap
├── src/
│   └── messy_project/
│       ├── __init__.py
│       ├── helpers.py
│       ├── main.py         # entry point module
│       └── old_utils.py
├── data/
│   ├── sample.json
│   └── data_loader.yaml    # data loader settings (distinct from the app config)
├── scripts/
│   ├── deploy.sh
│   ├── deploy_helpers.py   # deployment helpers (distinct from module helpers)
│   └── run_tests.sh
└── tests/
    ├── __init__.py
    ├── test_main.py
    └── test_helpers.py
```

## Running

```bash
uv venv --seed --python=3.13
.\.venv\Scripts\activate
pip install -r requirements.txt
set PYTHONPATH=src
python -m messy_project.main
pytest
```

Both commands should succeed from the project root.

## Notes

Important separation rules:

1. `config/app.yaml` and `data/data_loader.yaml` serve different purposes and must remain separate.
2. `src/messy_project/helpers.py` and `scripts/deploy_helpers.py` serve different purposes and must remain separate.
3. `old_utils.py` is still used by the app entry module and is intentionally retained.
