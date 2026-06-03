from src.pipeline.ingest import ingest_event
from src.pipeline.transform import normalize
from src.services.enrichment import enrich
from src.services.reporting import events_per_customer, total_value_per_customer


def _event(customer_id, event_type="click", value=0.0):
    return normalize(
        ingest_event(
            {
                "customer_id": customer_id,
                "type": event_type,
                "ts": "2026-01-01T00:00:00Z",
                "value": value,
            }
        )
    )


def test_enrich_adds_customer_prefix_to_metadata():
    event = enrich(_event("abcdef"))
    assert event.metadata["customer_prefix"] == "abc"


def test_events_per_customer_counts_by_customer_id():
    events = [_event("c1"), _event("c1"), _event("c2")]
    assert events_per_customer(events) == {"c1": 2, "c2": 1}


def test_total_value_per_customer_sums_value_field():
    events = [_event("c1", value=10), _event("c1", value=5), _event("c2", value=7)]
    assert total_value_per_customer(events) == {"c1": 15.0, "c2": 7.0}
