import sys
import os
import pytest

# Ensure project root is in sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from inventory import Inventory
from orders import bulk_order, inv, process_order


def setup_function():
    inv.items = []


def test_process_order_returns_formatted_price():
    inv.add_item("widget", 10)
    result = process_order("widget", 2)
    assert isinstance(result, str)
    assert result.startswith("$")


def test_process_order_insufficient_stock_returns_none():
    inv.add_item("gadget", 1)
    result = process_order("gadget", 5)
    assert result is None


def test_inventory_add_and_get():
    local = Inventory()
    local.add_item("thing", 3)
    assert local.get_stock("thing") == 3


def test_inventory_update_stock_updates_and_returns_true():
    local = Inventory()
    local.add_item("thing", 3)

    updated = local.update_stock("thing", 1)

    assert updated is True
    assert local.get_stock("thing") == 1


def test_inventory_update_stock_missing_item_returns_false():
    local = Inventory()

    updated = local.update_stock("missing", 1)

    assert updated is False


def test_bulk_order_propagates_invalid_item_errors():
    with pytest.raises(KeyError):
        bulk_order([{"name": "widget"}])


def test_bulk_order_keeps_process_order_none_signal_for_stock():
    inv.add_item("widget", 1)

    results = bulk_order([{"name": "widget", "qty": 2}])

    assert results == [None]
