"""MCP server exposing log tools — Challenge 1 read-only variant.

Differences from the Core solution:
  * No `rotate_log_file` tool is registered.
  * Server identifier differs so both variants can be registered side by side.
  * Server-level description states the read-only boundary.
"""

import os
from typing import Literal

from mcp.server.fastmcp import FastMCP

from log_tools.reader import count_by_level, list_log_files, search

LOG_DIR = os.environ.get("LOG_DIR", "./sample_logs")

mcp = FastMCP(
    "log-tools-readonly",
    instructions=(
        "Read-only log inspection tools. These tools only read from log "
        "files. Do not expect any tool in this server to modify, rotate, "
        "archive, or truncate a log file."
    ),
)


@mcp.tool()
def list_logs() -> list[str]:
    """List the log files available in the configured log directory.

    Read-only. Use this tool when the user asks which log files exist.

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

    Read-only. Use this tool when the user asks to find specific log
    lines by text content. This server does NOT support writes —
    rotating, archiving, or truncating logs is not available here.

    Args:
        pattern: Regex pattern matched against each log message.
        level: Optional log level filter.
        limit: Maximum number of results.

    Returns:
        A list of matching entries.
    """
    return search(LOG_DIR, pattern, level, limit)


@mcp.tool()
def count_logs_by_level() -> dict:
    """Return the number of log entries at each level.

    Read-only.

    Returns:
        A dict mapping DEBUG, INFO, WARNING, ERROR to counts.
    """
    return count_by_level(LOG_DIR)


if __name__ == "__main__":
    mcp.run()
