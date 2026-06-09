# Solution Reference

A worked fix for every bug in the starter.

## What Was Fixed

| File          | Bug                                                              | Root-cause fix |
|---------------|------------------------------------------------------------------|-----------------|
| `pricing.py`  | Missing colon on `def calculate_price(...) -> float`             | Add the colon.  |
| `inventory.py`| `can_fulfill` used `>` instead of `>=`                           | Change operator. |
| `inventory.py`| `_stock` was a class-level dict, causing state leakage across instances | Move initialization into `__init__(self)`. |
| `inventory.py`| `check_all_in_stock` iterated the dict per lookup (O(n·m))        | Use `self._stock.get(sku, 0)` — O(1) per lookup. |

The first three cause test failures. The fourth is a performance issue that passes the tests and is only visible on code review — included as a prompt for Challenge 2's refactor.

## Tempting Symptom Fixes

Two of the bugs have obvious-looking symptom fixes that pass the tests without fixing the root cause. Watch for these in the agent's autonomous run:

- For the state leak: a per-test fixture that calls `Inventory._stock.clear()` between tests. The tests pass, but the class is still broken in production — any code that creates two `Inventory` instances sees them share state.
- For the `>` vs `>=` logic bug: editing the failing test assertion to `is False` instead of fixing the operator. No reputable agent should do this, but it is worth checking explicitly.

## Running

```bash
pytest
```

All tests should pass.
