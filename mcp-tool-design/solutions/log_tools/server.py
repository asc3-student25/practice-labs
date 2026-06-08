"""MCP server exposing log tools — full Core solution."""

import os
from typing import Literal

from mcp.server.fastmcp import FastMCP

from log_tools.reader import count_by_level, list_log_files, rotate_log, search

LOG_DIR = os.environ.get("LOG_DIR", "./sample_logs")

mcp = FastMCP("log-tools")


@mcp.tool()
def list_logs() -> list[str]:
    """List the log files available in the configured log directory.

    Use this tool when the user asks which log files exist, or before
    calling a tool that requires a specific filename and the filename
    has not yet been established. Do NOT use this to read log content —
    use search_logs instead.

    Returns:
        A list of log filenames (relative to the log directory).
    """
    return list_log_files(LOG_DIR)


@mcp.tool()
def search_logs(
    pattern: str,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] | None = None,
    limit: int = 100,
) -> list[dict]:
    """Search log messages for lines matching a regex.

    Use this tool when the user asks to find or search for specific log
    lines by text content (for example, "find errors about redis" or
    "show me slow query warnings"). Do NOT use this to count entries —
    use count_logs_by_level instead. Do NOT use this to enumerate log
    files — use list_logs instead.

    Args:
        pattern: Regex pattern matched against each log message.
        level: Optional log level filter. One of DEBUG, INFO, WARNING, ERROR.
        limit: Maximum number of results to return. Defaults to 100.

    Returns:
        A list of dicts with keys: file, line_number, timestamp, level, message.
    """
    return search(LOG_DIR, pattern, level, limit)


@mcp.tool()
def count_logs_by_level() -> dict:
    """Return the number of log entries at each level across all log files.

    Use this tool when the user asks for counts, totals, or a summary of
    log volume by level. Do NOT use this to find specific log lines —
    use search_logs instead.

    Returns:
        A dict mapping each level (DEBUG, INFO, WARNING, ERROR) to its count.
    """
    return count_by_level(LOG_DIR)


@mcp.tool()
def rotate_log_file(filename: str) -> dict:
    """Archive a log file and create a new empty one in its place.

    WRITE operation: modifies the filesystem. Use this only when the
    user explicitly asks to rotate, archive, or truncate a log. Do NOT
    use this as part of a search or diagnostic flow, even if a log
    appears large.

    Args:
        filename: Name of the log file to rotate, relative to the log
            directory. Use list_logs first if the filename is not known.

    Returns:
        A dict with `archived_as` (new archive filename) and `original`
        (the filename that was rotated).
    """
    return rotate_log(LOG_DIR, filename)


if __name__ == "__main__":
    mcp.run()
