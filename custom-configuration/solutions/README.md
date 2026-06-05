# Solution Reference: Custom Configuration

This folder contains a worked example of the full configuration stack the lab asks you to build. Use it to compare against your own work, not as a drop-in replacement — the *process* of authoring each layer is the point of the lab.

## Files

```
.github/
├── copilot-instructions.md              # repository-wide conventions
├── instructions/
│   ├── backend.instructions.md          # applyTo: backend/**/*.py
│   └── tests.instructions.md            # applyTo: tests/**/*.py
├── content-exclusion-patterns.md        # reference list for Content Exclusion UI
└── skills/
    ├── add-api-endpoint/SKILL.md        # recurring task workflow
    └── check-credentials/SKILL.md       # security-relevant standing check

AGENTS.md                                # agent-specific behavioral guidance
```

## Notes

- `backend.instructions.md` includes an `applyTo` front-matter glob so the rules scope to `backend/**/*.py` only. Chat and Agent sessions that target other paths see only the repository-wide `copilot-instructions.md`.
- `AGENTS.md` is distinct from `copilot-instructions.md`. Agents read both; Chat reads only the latter. Put behavioral *constraints* on autonomous execution in `AGENTS.md`, not general style preferences.
- Copilot **Content Exclusion** is configured through the GitHub UI (Settings -> Copilot -> Content Exclusion) at the repository or organization level, not through a committed file. `content-exclusion-patterns.md` is a reference copy of the patterns a reviewer can paste into that UI so the exclusion set is version-controlled even though the configuration lives outside the repository. The previously-taught `.copilotignore` file is not part of the official Copilot configuration surface.
- The two skills demonstrate the two main use patterns:
  - `add-api-endpoint` is on-demand: it loads when a task description matches its description field.
  - `check-credentials` is standing: it loads on every code-producing task.
