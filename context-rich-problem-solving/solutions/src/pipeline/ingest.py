from src.models.event import Event


def ingest_event(raw):
    return Event(
        customer_id=raw["customer_id"],
        event_type=raw["type"],
        timestamp=raw["ts"],
        value=float(raw.get("value", 0)),
    )
