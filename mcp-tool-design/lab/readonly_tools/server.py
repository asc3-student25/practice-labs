"""MCP server for local log reading tools.

Fill in the stub tools marked TODO below. Refer to SCHEMA_TEMPLATES.md
for the expected schema shapes, and compare your tool descriptions
against the GitHub MCP server's tool descriptions as a quality benchmark.
"""

from typing import Literal
import os

from mcp.server.fastmcp import FastMCP

from log_tools.reader import (
    count_by_level,
    list_log_files,
    search,
)

LOG_DIR = os.environ.get("LOG_DIR", "./sample_logs")

mcp = FastMCP(
    "log-tools-readonly",
    instructions=(
        "Read-only log inspection tools. No tool in this server will "
        "modify, rotate, archive, or truncate a log file."
    ),
)


@mcp.tool()
def list_logs() -> list[str]:
    """List the log files available in the configured log directory.

    Use this tool when the user asks which log files exist, or before
    calling a tool that requires a specific filename and the filename
    has not yet been established.

    Returns:
        A list of log filenames (relative to the log directory).
    """
    return list_log_files(LOG_DIR)


@mcp.tool()
def search_logs(
    pattern: str,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] | None = None,
    limit: int = 100,) -> list[dict]:

    """Search log messages for a regex pattern, with optional filters.

    Use this tool when the user is looking for specific log lines by text
    content (examples : find spring boot logs with 400 error code, find logs containing a table not found or not existed).
    Do NOT use this tool for counting log line use count_logs_by_level() tool, 
    listing files or enumerating the files use list_logs() tool, or non-log data.

    Args:
        pattern: A regex pattern to search for in log messages.
        level: Optional log level filter (DEBUG, INFO, WARNING, ERROR).
        limit: Optional maximum number of results to return (default 100).
        
    Returns:
        A list of matching log entries, each represented as a dictionary
        with keys: file, line_number, timestamp, level, and message.

    """
    
    return search(LOG_DIR, pattern, level, limit)

# TODO: Implement `search_logs`.
#
# The tool should:
#   - Take a regex pattern and search log messages for matches
#   - Accept an optional `level` filter (DEBUG, INFO, WARNING, ERROR)
#   - Accept an optional `limit` on the number of results (default 100)
#   - Return a list of matching entries with file, line_number, timestamp,
#     level, and message fields
#
# Write a description that tells Copilot:
#   - When to use this tool (finding specific log lines by content)
#   - When NOT to use this tool (counting, listing files, or non-log data)
#   - What each argument means and what values are valid
#
# Use @mcp.tool() and call reader.search(LOG_DIR, pattern, level, limit).


@mcp.tool()
def count_logs_by_level() -> dict[str, int]:

    """Count the number of log messages at each level across all log files.

    Use this tool when the user wants a summary of log count by log level,
    such as "how many log messages in the ERROR level?" or total log count or volume of log messages, 
    such as "give me a count of log messages in all levels across all files".

    Do not use this tool when the user is looking for specific log lines (use search_logs() instead),
    or when the user is asking about non-log data
    or when the user is asking to list files (use list_logs() instead).

    Returns:
        A dictionary mapping log levels (DEBUG, INFO, WARNING, ERROR) to
        their respective counts.
    """
    return count_by_level(LOG_DIR)

# TODO: Implement `count_logs_by_level`.
#
# The tool should return a dict of level -> count across all log files.
# Call reader.count_by_level(LOG_DIR).


# TODO: Implement `rotate_log_file`. This is a WRITE operation.
#
# The tool archives the named log file with a UTC timestamp suffix and
# creates a new empty file in its place. Be explicit in the description
# that this tool MODIFIES the filesystem. Call reader.rotate_log(LOG_DIR,
# filename).


if __name__ == "__main__":
    mcp.run()
