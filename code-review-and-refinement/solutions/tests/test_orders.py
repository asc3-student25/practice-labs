import sys
import os
import pytest

# Ensure project root is in sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from inventory import Inventory
from orders import bulk_order, inv, process_order
from pricing import TAX_RATE, apply_bulk_discount
from utils import calculate_discount


def setup_function():
    inv.items = []


def test_process_order_returns_formatted_price():
    inv.add_item("widget", 10)
    result = process_order("widget", 2)
    assert isinstance(result, str)
    assert result.startswith("$")


def test_process_order_insufficient_stock_returns_none():
    inv.add_item("gadget", 1)
    assert process_order("gadget", 5) is None


def test_process_order_unknown_item_returns_none():
    assert process_order("missing", 1) is None


def test_process_order_decrements_stock():
    inv.add_item("widget", 5)
    process_order("widget", 2)
    assert inv.get_stock("widget") == 3


def test_calculate_discount_uses_percent_correctly():
    assert calculate_discount(100, 15) == pytest.approx(85.0)


def test_bulk_discount_applies_at_threshold():
    assert apply_bulk_discount(100, 10) == pytest.approx(90.0)
    assert apply_bulk_discount(100, 9) == pytest.approx(100.0)


def test_inventory_instances_do_not_share_state():
    a = Inventory()
    a.add_item("x", 1)
    b = Inventory()
    assert b.items == []


def test_bulk_order_handles_empty_and_missing_items():
    results = bulk_order([{"name": "nope", "qty": 1}])
    assert results == [None]
    assert bulk_order() == []


def test_tax_rate_applied_once():
    inv.add_item("widget", 1)
    result = process_order("widget", 1)
    expected = 9.99 * (1 + TAX_RATE)
    assert result == f"${expected:.2f}"
