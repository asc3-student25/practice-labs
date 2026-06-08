"""Log reading logic. Treat this module as stable; fill in the MCP
server surface in server.py instead.
"""

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

LOG_LINE_RE = re.compile(
    r"^(?P<timestamp>\S+)\s+(?P<level>DEBUG|INFO|WARNING|ERROR)\s+(?P<message>.*)$"
)

VALID_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


def _iter_entries(log_dir):
    base = Path(log_dir)
    for path in sorted(base.glob("*.log")):
        with path.open(encoding="utf-8") as f:
            for lineno, line in enumerate(f, start=1):
                match = LOG_LINE_RE.match(line.strip())
                if not match:
                    continue
                yield {
                    "file": str(path.relative_to(base)),
                    "line_number": lineno,
                    "timestamp": match["timestamp"],
                    "level": match["level"],
                    "message": match["message"],
                }


def search(log_dir, pattern, level=None, limit=100):
    """Return log entries whose message matches ``pattern`` (regex)."""
    compiled = re.compile(pattern)
    results = []
    for entry in _iter_entries(log_dir):
        if level and entry["level"] != level:
            continue
        if compiled.search(entry["message"]):
            results.append(entry)
            if len(results) >= limit:
                break
    return results


def count_by_level(log_dir):
    """Return a dict of level -> count for all entries in the directory."""
    counts = {level: 0 for level in VALID_LEVELS}
    for entry in _iter_entries(log_dir):
        counts[entry["level"]] = counts.get(entry["level"], 0) + 1
    return counts


def list_log_files(log_dir):
    """Return the list of .log filenames (relative paths) in the directory."""
    base = Path(log_dir)
    return sorted(str(p.relative_to(base)) for p in base.glob("*.log"))


def rotate_log(log_dir, filename):
    """Archive ``filename`` with a UTC timestamp suffix and truncate the original.

    Write operation. Moves ``<filename>`` to ``<filename>.<timestamp>.archive``
    and creates a new empty file at the original path.
    """
    base = Path(log_dir)
    source = base / filename
    if not source.is_file():
        raise FileNotFoundError(f"log file not found: {filename}")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive = base / f"{filename}.{timestamp}.archive"
    shutil.move(str(source), str(archive))
    source.touch()
    return {"archived_as": str(archive.relative_to(base)), "original": filename}
