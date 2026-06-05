# User Directory

A small multi-layer application used as the substrate for the context engineering lab. The code is deliberately minimal — the lab is about building the *configuration* around this code, not building the code itself.

## Layout

```
.
├── backend/            # Python / Flask API
│   ├── app.py
│   ├── models.py
│   └── api/
│       └── users.py
├── frontend/           # Minimal HTML + vanilla JS
│   ├── index.html
│   └── app.js
├── migrations/         # Numbered database migrations (treat as append-only)
│   ├── 0001_initial.py
│   └── 0002_add_email.py
├── tests/              # pytest suite
│   └── test_users.py
├── build/              # build artifacts (auto-generated)
├── generated/          # generated schemas (auto-generated)
├── package-lock.json   # JS dependency lock (auto-generated)
└── requirements.txt
```

## Running

```bash
uv venv --seed --python=3.13
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m backend.app    # start the API
pytest                   # run the test suite
```

## What You Will Build in the Lab

Nothing in this repository. You will run Copilot against this code *as it is* and build a configuration stack that shapes how Copilot responds:

- `.github/copilot-instructions.md` — repository-wide conventions
- `.github/instructions/*.instructions.md` — path-specific rules
- `AGENTS.md` — agent-specific behavioral constraints
- Copilot Content Exclusion — repo/org path exclusions (configured in the GitHub UI)
- `.github/skills/*/SKILL.md` — reusable task procedures

See `BASELINE_TASKS.md` for the tasks you will run before and after each configuration layer.
