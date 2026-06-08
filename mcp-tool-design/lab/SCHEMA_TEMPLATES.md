# MCP Tool Schema Templates

Reference shapes for the tools you will author in this lab. When using the `FastMCP` framework (as the starter does), the schema is generated from your type hints, your default values, and your docstring. The templates below show what the generated schema *becomes*; authoring in Python stays concise.

## Simple Read Tool

Generated schema shape:

```json
{
  "name": "list_logs",
  "description": "List the log files available in the configured log directory. Use this when ...",
  "inputSchema": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
```

Python source that produces that schema:

```python
@mcp.tool()
def list_logs() -> list[str]:
    """List the log files available in the configured log directory.

    Use this tool when the user asks which log files exist ...
    """
    return list_log_files(LOG_DIR)
```

## Read Tool With Required and Optional Arguments

Generated schema shape:

```json
{
  "name": "search_logs",
  "description": "Search log messages for lines matching a regex. Use this when ...",
  "inputSchema": {
    "type": "object",
    "properties": {
      "pattern": {
        "type": "string",
        "description": "Regex pattern matched against each log message."
      },
      "level": {
        "type": "string",
        "enum": ["DEBUG", "INFO", "WARNING", "ERROR"],
        "description": "Optional log level filter."
      },
      "limit": {
        "type": "integer",
        "default": 100,
        "description": "Maximum number of results."
      }
    },
    "required": ["pattern"]
  }
}
```

Python source:

```python
from typing import Literal

@mcp.tool()
def search_logs(
    pattern: str,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] | None = None,
    limit: int = 100,
) -> list[dict]:
    """Search log messages for lines matching a regex.

    Use this tool when the user asks to find or search for specific log
    lines by text content. Do NOT use this to count entries — use
    count_logs_by_level instead. Do NOT use this to enumerate files — use
    list_logs instead.

    Args:
        pattern: Regex pattern matched against each log message.
        level: Optional log level filter. One of DEBUG, INFO, WARNING, ERROR.
        limit: Maximum number of results to return. Defaults to 100.

    Returns:
        A list of dicts with keys: file, line_number, timestamp, level, message.
    """
    return search(LOG_DIR, pattern, level, limit)
```

## Write Tool With a Clear Warning

Generated schema shape:

```json
{
  "name": "rotate_log_file",
  "description": "Archive a log file and create a new empty one. WRITE operation: modifies the filesystem. Use this only when the user explicitly asks to rotate or archive a log.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "filename": {
        "type": "string",
        "description": "Name of the log file to rotate (relative to the log directory)."
      }
    },
    "required": ["filename"]
  }
}
```

Python source:

```python
@mcp.tool()
def rotate_log_file(filename: str) -> dict:
    """Archive a log file and create a new empty one in its place.

    WRITE operation: modifies the filesystem. Use this only when the
    user explicitly asks to rotate or archive a log. Do NOT use this
    as part of a read flow.

    Args:
        filename: Name of the log file (relative to the log directory).

    Returns:
        A dict with `archived_as` and `original` keys.
    """
    return rotate_log(LOG_DIR, filename)
```

## Description-Writing Checklist

A good tool description covers:

- **What it does** in one clear sentence.
- **When to use it** — the user intent that should route to this tool.
- **When NOT to use it** — overlapping-sounding tasks that should route elsewhere.
- **Argument semantics** — what each parameter means, not just its type.
- **Write vs. read** — if the tool modifies state, say so explicitly in the first sentence.

Common anti-patterns to avoid:

- Generic single-word descriptions ("Search." "Query.")
- Descriptions that restate the tool name ("search_logs: Searches logs.")
- Marketing language ("Powerful log search for your application.")
- Descriptions that promise a capability the implementation does not deliver
- Descriptions that are identical or near-identical to another tool's description
