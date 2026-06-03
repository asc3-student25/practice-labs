# Event Data Model — Canonical Specification

This document is the authoritative reference for the `Event` data model used across the ingest → transform → enrich → export pipeline. Downstream consumers (billing, reporting, audit) are keyed on the identifiers defined here; renames must be reflected in every consumer simultaneously.

> **Note for Challenge 2:** This spec intentionally does **not** match the starter code. The starter code uses `user_id`; this spec uses `customer_id`. The mismatch is the point of the exercise — the Copilot Space you attach contains this spec, and the refactor is expected to adopt its vocabulary.

## Canonical Identifier

The canonical identifier is **`customer_id`**, not `user_id`.

**Reason:** the downstream billing system keys on customer, not user. A user is an authentication identity; a customer is the billable entity. One customer can have multiple users (team seats), and one user can appear under multiple customers (contractor relationships). Billing reconciliation, invoice generation, and revenue reporting all join on `customer_id`. A rename from `user_id` to `customer_id` is therefore not cosmetic — it is a correction of a long-standing naming drift between the event pipeline and the consumer systems.

## Event Fields

| Field         | Type     | Description                                                           | Required |
| ------------- | -------- | --------------------------------------------------------------------- | -------- |
| `customer_id` | `str`    | Canonical customer identifier (matches billing system)                | Yes      |
| `event_type`  | `str`    | Normalized action name (lowercase, underscore-separated)              | Yes      |
| `ts`          | `str`    | ISO 8601 timestamp of the event                                       | Yes      |
| `value`       | `float`  | Monetary or numeric value associated with the event (0.0 if N/A)      | Yes      |
| `metadata`    | `dict`   | Enrichment-added context; keys prefixed with the enricher name        | No       |

Note: the starter code stores a `user_prefix` key inside `metadata`. Under this spec, that key becomes `customer_prefix`. Metadata key renames are part of the rename, not optional polish.

## Consumers That Depend on `customer_id`

The following systems consume events from the export stage and join on `customer_id`. A rename that misses any of these breaks the consumer contract:

1. **Billing pipeline** — nightly invoice generation reads the JSONL export and aggregates by `customer_id`. A missing or mis-named key produces invoices with zero line items.
2. **Reporting service** — the `events_per_user` and `total_value_per_user` queries in `src/services/reporting.py` must be renamed to `events_per_customer` and `total_value_per_customer` and return the new field.
3. **Audit log consumer** — the compliance team indexes events by `customer_id` for retention and subject-access requests. Events with `user_id` are ingested as orphaned records.
4. **Data warehouse loader** — the warehouse schema has a `customer_id` column; the loader asserts on field presence and fails the batch if the source field is absent.

## Non-Goals

This spec does **not** describe:

- The authentication subsystem's `user_id` — that identifier continues to exist in the auth service and is unchanged by this rename.
- The mapping between users and customers — that lives in `identity_service` and is out of scope for the event pipeline.
- Historical events already emitted with `user_id` — backfill is the responsibility of the warehouse loader, not the pipeline rewrite.

## Rename Checklist

A correct rename touches, at minimum:

- `src/models/event.py` — field name on the dataclass
- `src/pipeline/ingest.py` — the raw-dict key read and the attribute set
- `src/pipeline/transform.py` — any reference to the field during normalization
- `src/pipeline/export.py` — the serializer's output key
- `src/services/enrichment.py` — the `user_prefix` metadata key becomes `customer_prefix`
- `src/services/reporting.py` — function names (`events_per_user` → `events_per_customer`, `total_value_per_user` → `total_value_per_customer`) and their implementations
- `tests/test_pipeline.py` and `tests/test_services.py` — fixtures, arguments, and assertions

A rename that stops at the dataclass is not a rename. The consumers carry the cost of the mismatch.
