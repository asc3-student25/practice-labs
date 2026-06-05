---
name: check-credentials
description: Scan new or modified code for hardcoded credentials, API keys, tokens, or secrets before proposing the change. Applies to every feature implementation, bug fix, or refactor the agent produces in this repository.
---

# Check Credentials

Use this skill as a standing pre-commit check on any code the agent writes or modifies in this repository. It does not require a user to invoke it; it loads whenever the task involves producing or editing source files.

## Before proposing code

Scan any file the agent is about to write or modify for the following patterns. If any match, pause and flag them before completing the task.

### String patterns

- Assignments where the value is a non-empty string literal and the variable name matches any of: `password`, `passwd`, `secret`, `token`, `api_key`, `apikey`, `access_key`, `private_key`, `auth`, `credential`, `bearer`.
- String literals starting with known prefixes: `sk-`, `ghp_`, `gho_`, `AKIA` (AWS access key), `xoxb-` (Slack), `AIza` (Google).
- URLs embedding credentials: `https?://[^:]+:[^@]+@`.
- Base64-encoded strings longer than 40 characters with no surrounding context that explains them.

### Config file patterns

- Non-empty string values in `config.yaml`, `.env`, `settings.py`, or similar files for any key matching the variable name list above.

### Test file patterns

Test files may legitimately contain placeholder credentials. When scanning tests:

- Require that placeholder values obviously *look* like placeholders: `"test-token"`, `"dummy"`, `"placeholder"`, `"x"` * n.
- Flag test files that contain strings matching real-token prefixes (`sk-`, `ghp_`, `AKIA`, etc.) even in tests.

## When a pattern matches

1. Do not silently replace the value. Flag it with a short explanation: file, line, which pattern matched, and why the match is concerning.
2. Propose one of: move to an environment variable, move to a secrets store, or (for tests) replace with an obvious placeholder.
3. Wait for direction before applying the proposal if the task is ambiguous about secrets handling.

## When no pattern matches

Record in the task summary: "Credential scan clean" with the list of files scanned. This explicit statement makes the absence of findings auditable.

## Out of scope

- Scanning dependencies or third-party code (anything under `node_modules/`, `build/`, `generated/`, or covered by Copilot Content Exclusion).
- Cryptographic analysis — the skill flags plausible secrets, not analyses of whether a value is a good or bad secret.
