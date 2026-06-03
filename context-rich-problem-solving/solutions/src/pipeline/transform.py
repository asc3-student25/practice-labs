def normalize(event):
    event.event_type = event.event_type.lower().strip()
    if event.metadata is None:
        event.metadata = {}
    return event
