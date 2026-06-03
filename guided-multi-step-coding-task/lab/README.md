# Task Manager API

A small Flask-based task manager API. This starter has a minimal implementation that you will extend during the lab.

## What Is Implemented

- `GET /tasks` — list all tasks
- `POST /tasks` — create a new task

## What Is Missing

See `FEATURE_BRIEF.md` for the feature you will implement.

## Running the Application

Create a virtual environment, install dependencies, and start the server:

```bash
uv venv --seed --python=3.13
.\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The server runs on `http://localhost:5000`.

## Running the Tests

```bash
pytest
```

## Project Layout

```
.
├── app.py              # Flask routes
├── storage.py          # In-memory task store
├── requirements.txt
├── tests/
│   └── test_app.py     # Test suite (pytest)
└── FEATURE_BRIEF.md    # Feature specification for the lab
```
