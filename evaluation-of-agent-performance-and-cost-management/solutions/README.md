# Evaluation and Cost Management - Solution

Comprehensive framework for agent evaluation and cost tracking.

## Features

- ✅ Test suite execution with quality metrics
- ✅ Model tier comparison (cost vs quality)
- ✅ Cost tracking per user/day
- ✅ Performance dashboards

## Quick Start

```bash
cp .env.example .env
uv sync
uv run python main.py
```

## Usage

```python
from main import AgentEvaluator, TestCase

test_cases = [TestCase(...), ...]
evaluator = AgentEvaluator(test_cases)

results = await evaluator.evaluate('gpt-4o-mini')
report = evaluator.generate_report(results)
```

Educational use - GAI-2109 course.
