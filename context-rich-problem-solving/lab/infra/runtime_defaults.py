"""Runtime constants owned by platform-infra.

These values are tuned during capacity review and referenced by pipeline
stages at import time. Coordinate changes with the platform-infra team.
"""

SCHEMA_VERSION = "1.3"
MAX_EVENTS_PER_BATCH = 500
DEFAULT_FLUSH_INTERVAL_SECONDS = 30
