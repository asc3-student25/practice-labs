# Solution Reference

Three worked implementations of the same server, each showing a different slice of the lab.

## `log_tools/server.py` — Core solution

A fully implemented server with four tools: `list_logs`, `search_logs`, `count_logs_by_level`, and `rotate_log_file`. Descriptions follow the "what / when / when-not" shape.

## `readonly_tools/server.py` — Challenge 1 variant

The same server with the write-capable tool (`rotate_log_file`) removed. Use this to observe whether Copilot refuses, requests a different tool, or surfaces the limitation when asked to rotate a log.

## `ambiguous_tools/server.py` — Challenge 2 variant

A version where two tools (`search_logs` and a new `find_logs`) have overlapping, vague descriptions. Use this to observe how description quality drives tool selection accuracy.

## Notes

- Only register one variant with VS Code at a time. Running two servers with overlapping tool names at once is what Challenge 2 explores, but *unintentional* overlap between your own server and another one (for example, the GitHub MCP server) will muddy your observations.
- Each variant is a self-contained server. You can register them under different server IDs (`log-tools`, `log-tools-readonly`, `log-tools-ambiguous`) in `.vscode/mcp.json` if you want to switch between them without editing the config repeatedly.

### Where to place the variants on disk

Both `readonly_tools/` and `ambiguous_tools/` import from `log_tools.reader`:

```
from log_tools.reader import count_by_level, list_log_files, search
```

For those imports to resolve, the variant must be staged as a **sibling** of `log_tools/`, not inside it. The expected layout:

```
<lab-root>/
├── log_tools/              # original package (holds reader.py)
│   ├── reader.py
│   └── server.py
├── readonly_tools/         # Challenge 1 variant (sibling of log_tools)
│   └── server.py
└── ambiguous_tools/        # Challenge 2 variant (sibling of log_tools)
    └── server.py
```

Running a variant uses its own module name (`python -m readonly_tools.server` or `python -m ambiguous_tools.server`), but the working directory must be the lab root so Python can find `log_tools` on the import path.
