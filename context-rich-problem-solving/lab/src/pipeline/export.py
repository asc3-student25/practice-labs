import json

from infra.runtime_defaults import SCHEMA_VERSION


def to_jsonl(events):
    lines = []
    for event in events:
        lines.append(
            json.dumps(
                {
                    "schema": SCHEMA_VERSION,
                    "customer_id": event.customer_id,
                    "event_type": event.event_type,
                    "timestamp": event.timestamp,
                    "value": event.value,
                    "metadata": event.metadata,
                }
            )
        )
    return "\n".join(lines)
