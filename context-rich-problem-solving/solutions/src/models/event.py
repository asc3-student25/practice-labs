from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Event:
    customer_id: str
    event_type: str
    timestamp: str
    value: float = 0.0
    metadata: Optional[dict] = field(default=None)
