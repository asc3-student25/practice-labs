# Dependency Map — Event Pipeline

Generated after the Space-grounded refactor run (Challenge 2). This map documents every file that references the `Event` data model, the direction of the data flow, and which files depend on `infra/runtime_defaults.py`.

## Event Data Model

Definition: `src/models/event.py` — dataclass with `customer_id`, `event_type`, `timestamp`, `value`, and `metadata`.

### Files that import or construct `Event`

| File                              | Relationship                                                   |
| --------------------------------- | -------------------------------------------------------------- |
| `src/pipeline/ingest.py`          | Constructs `Event` from a raw dict (entry point of the flow)   |
| `src/pipeline/transform.py`       | Reads and mutates `Event` (normalizes `event_type`, metadata)  |
| `src/pipeline/export.py`          | Reads `Event` fields to produce JSONL                          |
| `src/services/enrichment.py`      | Reads `Event`, writes enrichment keys into `metadata`          |
| `src/services/reporting.py`       | Reads `Event` as a consumer (aggregations by `customer_id`)    |
| `tests/test_pipeline.py`          | Constructs and asserts on `Event` through the pipeline stages  |
| `tests/test_services.py`          | Constructs and asserts on `Event` through enrichment/reporting |

## Forward Data Flow

```
raw dict
  → src/pipeline/ingest.py           (ingest_event)
  → src/pipeline/transform.py        (normalize)
  → src/services/enrichment.py       (enrich — mutates metadata)
  → src/pipeline/export.py           (to_jsonl — produces output)
```

The pipeline is **linear forward**. Each stage reads the event produced by the previous stage, optionally mutates it, and passes it on. `export.py` is the terminal stage.

## Consumer Branch

```
src/services/reporting.py
  ← consumes a list of Event objects produced upstream
  ← aggregates by customer_id (events_per_customer, total_value_per_customer)
```

`reporting.py` is a **consumer**, not a pipeline stage. It reads events that have already been exported or are held in memory after enrichment. A common mistake is to describe the system as "ingest → transform → enrich → export → reporting" — that order is wrong. Reporting sits alongside export, not after it.

## Dependencies on `infra/runtime_defaults.py`

The `infra/` directory is outside `src/` and holds constants owned by the platform-infra team. Import graph:

```
infra/runtime_defaults.py
  ↑ imported by src/pipeline/export.py   (uses SCHEMA_VERSION in the JSON output)
```

**Only `src/pipeline/export.py` imports from `infra/`.** Other constants in `runtime_defaults.py` (`MAX_EVENTS_PER_BATCH`, `DEFAULT_FLUSH_INTERVAL_SECONDS`) are unused in the current codebase — they are available for future consumers but do not participate in the current data flow.

### Why this edge is easy to miss

- `infra/` is not under `src/` and is not named in the pipeline docstring.
- The import lives in `export.py`, which students usually audit last.
- `#codebase` answers that describe the flow by directory are likely to skip `infra/` because it does not participate in the sequence of transformations — it only contributes a constant.

A correct audit of any schema-related change must follow the import edge into `infra/`, not just walk the pipeline directory tree.

## Edge-Case Notes

- **Metadata key rename (`user_prefix` → `customer_prefix`):** enrichment writes a key derived from the canonical identifier. If the rename stops at the dataclass field, the metadata key drifts and the audit-log consumer breaks silently.
- **Test data:** both `tests/test_pipeline.py` and `tests/test_services.py` construct raw dicts with `customer_id` keys; the ingest stage then maps them onto `Event`. A rename that misses test fixtures passes the dataclass check but fails the ingest parse.
- **Schema version:** the `SCHEMA_VERSION` constant governs the `schema` field in every exported record. Consumers that key on `schema == "1.3"` reject records from older pipelines — schema bumps are a consumer-coordinated event, not a unilateral bump.
