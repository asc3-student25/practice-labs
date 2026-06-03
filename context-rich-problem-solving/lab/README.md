# Event Pipeline

A small event-processing pipeline: events are ingested, normalized, enriched, and exported. The flow spans multiple directories so you will need cross-file context to work on it effectively.

## Project Layout

```
.
├── conftest.py              # adds the project root to sys.path for tests
├── src/
│   ├── models/
│   │   └── event.py         # Event dataclass (data model)
│   ├── pipeline/
│   │   ├── ingest.py        # raw dict -> Event
│   │   ├── transform.py     # normalize fields
│   │   └── export.py        # serialize a batch
│   └── services/
│       ├── enrichment.py    # adds derived metadata
│       └── reporting.py     # summarizes a batch
├── infra/
│   └── runtime_defaults.py  # runtime constants used across the pipeline
└── tests/
    ├── test_pipeline.py
    └── test_services.py
```

## Running

Create a virtual environment, install dependencies, and run the tests:

```bash
uv venv --seed --python=3.13
.\.venv\Scripts\activate
pip install -r requirements.txt
pytest
```

All starter tests pass.

## Data Flow

```
raw dict
  -> ingest.ingest_event         (src/pipeline/ingest.py)
  -> transform.normalize         (src/pipeline/transform.py)
  -> enrichment.enrich           (src/services/enrichment.py)
  -> export.to_jsonl             (src/pipeline/export.py)

reporting.events_per_customer    (src/services/reporting.py)
  consumes lists of Event objects produced by the pipeline above
```
