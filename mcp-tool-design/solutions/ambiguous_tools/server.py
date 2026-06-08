"""MCP server exposing log tools — Challenge 2 ambiguous variant.

This server exists to demonstrate the failure mode you are trying to
avoid. Both `search_logs` and `find_logs` below do the same thing and
have overlapping, vague descriptions. Observe how Copilot chooses
between them (or fails to) across a range of prompts.

Do NOT use this variant as a reference for how to write real tools.
"""

import os
from typing import Literal

from mcp.server.fastmcp import FastMCP

from log_tools.reader import search

LOG_DIR = os.environ.get("LOG_DIR", "./sample_logs")

mcp = FastMCP("log-tools-ambiguous")


@mcp.tool()
def search_logs(
    pattern: str,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] | None = None,
    limit: int = 100,
) -> list[dict]:
    """Search logs.

    Use this for log-related queries.
    """
    return search(LOG_DIR, pattern, level, limit)


@mcp.tool()
def find_logs(
    query: str,
    severity: Literal["DEBUG", "INFO", "WARNING", "ERROR"] | None = None,
    max_results: int = 100,
) -> list[dict]:
    """Find log entries.

    A tool for when you need to look at log data.
    """
    return search(LOG_DIR, query, severity, max_results)


if __name__ == "__main__":
    mcp.run()
