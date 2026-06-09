# Inventory / Pricing / Cart — Debugging Lab

A small shopping cart module with deliberate bugs. Agent Mode's job in this lab is to run the tests, locate the failures, and fix them without being told where the bugs are. Your job is to audit the fixes for root-cause vs. symptom-level corrections.

## Layout

```
.
├── inventory.py         # Inventory class — tracks stock per SKU
├── pricing.py           # pricing helpers — calculates totals and discounts
├── cart.py              # Cart class — uses inventory + pricing
├── models.py            # shared Item dataclass
├── tests/
│   ├── test_inventory.py
│   ├── test_pricing.py
│   └── test_cart.py
└── requirements.txt
```

## Running (Expect Failures)

```bash
uv venv --seed --python=3.13
.\.venv\Scripts\activate
pip install -r requirements.txt
pytest
```

The starter suite has collection-time failures *and* assertion failures by design. Establishing the baseline of what fails is the first step of the lab.
