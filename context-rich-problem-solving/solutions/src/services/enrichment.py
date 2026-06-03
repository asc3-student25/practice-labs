def enrich(event):
    if event.metadata is None:
        event.metadata = {}
    event.metadata["customer_prefix"] = event.customer_id[:3] if event.customer_id else ""
    return event
