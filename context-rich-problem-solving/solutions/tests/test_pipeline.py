import json

from src.pipeline.export import to_jsonl
from src.pipeline.ingest import ingest_event
from src.pipeline.transform import normalize


def test_ingest_event_builds_event_from_raw():
    raw = {"customer_id": "c42", "type": "CLICK", "ts": "2026-01-01T00:00:00Z", "value": "1.5"}
    event = ingest_event(raw)
    assert event.customer_id == "c42"
    assert event.event_type == "CLICK"
    assert event.value == 1.5


def test_normalize_lowercases_event_type():
    event = ingest_event(
        {"customer_id": "c1", "type": " PAGE_VIEW ", "ts": "2026-01-01T00:00:00Z"}
    )
    normalized = normalize(event)
    assert normalized.event_type == "page_view"
    assert normalized.metadata == {}


def test_to_jsonl_serializes_customer_id_and_schema():
    event = normalize(
        ingest_event({"customer_id": "c7", "type": "click", "ts": "2026-01-01T00:00:00Z"})
    )
    output = to_jsonl([event])
    record = json.loads(output)
    assert record["customer_id"] == "c7"
    assert record["schema"] == "1.3"
