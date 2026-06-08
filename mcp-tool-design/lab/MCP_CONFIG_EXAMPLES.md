# MCP Server Configuration in VS Code

VS Code registers MCP servers for Copilot through `.vscode/mcp.json` (workspace-scoped) or the user-level `mcp.json` (global). The file has a top-level `servers` key. You can also use **MCP: Add Server** from the command palette for an interactive setup. Older community snippets placed MCP servers inside `.vscode/settings.json` under an `mcp` key — that shape is no longer honored; use `mcp.json` instead.

## Register the Log Tools Server

Create `.vscode/mcp.json` at the repository root (or the lab root, if you are treating the lab as a standalone workspace).

```json
{
  "servers": {
    "log-tools": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "log_tools.server"],
      "cwd": "C:/LabFiles/mcp-tool-design/lab",
      "env": {
        "LOG_DIR": "C:/LabFiles/mcp-tool-design/lab/sample_logs"
      }
    }
  }
}
```

Notes:

- `"type": "stdio"` tells VS Code to communicate over the process's stdin/stdout (the transport `FastMCP` uses by default).
- `"cwd"` matters because `server.py` imports `log_tools.reader` — the working directory must be the lab root so Python can resolve the package.
- `"env"` passes `LOG_DIR` so the server reads from the checked-in `sample_logs/` regardless of where it is started from.

## Using the Add Server Command

Alternatively, run **MCP: Add Server** from the VS Code command palette and fill in the fields interactively. You will be prompted for:

- Server ID (use `log-tools`)
- Transport (select `stdio`)
- Command and arguments (use `python` and `-m log_tools.server`)
- Working directory (use the lab directory's absolute path)

The interactive path writes the same `.vscode/mcp.json` structure shown above.

## Verifying the Server Loaded

After configuration:

1. Reload the VS Code window (`Developer: Reload Window`).
2. Open Copilot Chat and switch to Agent Mode.
3. Ask: `What MCP tools are available?`
4. Copilot should list `list_logs` (and any other tools you have registered). If it does not, open the MCP panel or the output channel `GitHub Copilot Chat` for server startup errors.

## Registering the GitHub MCP Server

For comparison, register the GitHub-hosted MCP server as well. Add a second entry to the same `servers` object in your `mcp.json` (after the existing `log-tools` item):

```json
{
  "servers": {
    "log-tools": { 
      ... 
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    }
  }
}
```

This is the HTTP-transport form (authenticated via the same OAuth session your GitHub Copilot extension already has). Use the **MCP: Add Server** command palette entry and select `HTTP` for the interactive path.

Once registered, examine the tool descriptions from the `github` server in the Chat view or in the server's published schema — these are your quality benchmark for writing descriptions in your own tools.
