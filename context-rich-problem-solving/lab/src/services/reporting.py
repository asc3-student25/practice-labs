from collections import defaultdict


def events_per_customer(events):
    counts = defaultdict(int)
    for event in events:
        counts[event.customer_id] += 1
    return dict(counts)


def total_value_per_customer(events):
    totals = defaultdict(float)
    for event in events:
        totals[event.customer_id] += event.value
    return dict(totals)
