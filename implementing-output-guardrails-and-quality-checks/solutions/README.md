# Output Guardrails and Quality Checks - Solution

Complete guardrail system for safe, compliant AI agent deployment.

## Features

- ✅ **Input validation** - Block restricted topics and jailbreak attempts
- ✅ **Output validation** - Enforce quality, safety, and policy standards
- ✅ **PII detection** - Redact sensitive information automatically
- ✅ **Auto-retry** - Correct policy violations with refined prompts
- ✅ **Quality scoring** - Grade responses on multiple dimensions

## Quick Start

```bash
cp .env.example .env
# Add your OpenAI API key

uv sync
uv run python agent.py
```

## Files

- `input_guards.py` - Input validation (topics, jailbreaks, length)
- `output_guards.py` - Output validation (quality, safety, policy)
- `pii_detector.py` - PII detection and redaction
- `agent.py` - Complete guardrail integration with retry logic

## Usage

```python
from agent import handle_query_with_retry

result = await handle_query_with_retry("What are your hours?")

if result['success']:
    print(result['response'])
    # Guardrails applied: result['guardrails_triggered']
else:
    print(f"Blocked: {result['error']}")
```

## Guardrail Pipeline

1. **Input Validation** - Check query before processing
2. **Agent Execution** - Run if input is valid
3. **Output Validation** - Check response quality/safety
4. **Policy Check** - Verify compliance
5. **PII Redaction** - Remove sensitive data
6. **Retry** - Auto-correct violations (up to 2 retries)

## License

Educational use - GAI-2109 course materials.
