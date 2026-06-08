# Log Tools MCP Server

The starter for the MCP tool design lab. You will build a custom Model Context Protocol server that exposes tools for reading local log files, register it with VS Code's Copilot, and observe how tool description quality shapes tool selection accuracy.

## Layout

```
.
├── log_tools/
│   ├── reader.py          # working log reading logic (do not modify)
│   └── server.py          # MCP server with stub tools (fill these in)
├── sample_logs/
│   └── app.log            # sample log file used as the resource
├── tests/
│   └── test_reader.py     # unit tests for the reader module
├── SCHEMA_TEMPLATES.md    # reference schemas for common tool shapes
├── MCP_CONFIG_EXAMPLES.md # .vscode/mcp.json snippets for MCP servers
└── requirements.txt
```

## Installing

```bash
uv venv --seed --python=3.13
.\.venv\Scripts\activate
pip install -r requirements.txt
pytest
```

All reader tests should pass before you start the lab — they verify that the log reading logic in `log_tools/reader.py` works so that you can focus on the tool *schema* design.

## Running the Server Manually

```bash
python -m log_tools.server
```

The server communicates over stdio. Running it directly is useful to confirm the process starts; it will wait for MCP protocol input. See `MCP_CONFIG_EXAMPLES.md` for how to register it with VS Code so Copilot Agent Mode can invoke it.
