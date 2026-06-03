import sys
import os
import pytest

# Ensure project root is in sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

for _module in ("inventory", "orders", "pricing", "utils"):
    sys.modules.pop(_module, None)

from inventory import Inventory
from orders import bulk_order, inv, process_order


def setup_function():
    inv.items = []


def test_process_order_returns_correct_formatted_price():
    inv.add_item("widget", 10)
    result = process_order("widget", 2)
    assert result == "$21.58"


def test_process_order_applies_coupon_correctly():
    inv.add_item("widget", 10)
    result = process_order("widget", 1, coupon_percent=20)
    assert result == "$8.63"


def test_process_order_unknown_item_returns_none():
    assert process_order("missing", 1) is None


@pytest.mark.parametrize("qty", [0, -1])
def test_process_order_invalid_quantity_returns_none(qty):
    inv.add_item("widget", 10)
    assert process_order("widget", qty) is None


@pytest.mark.parametrize("coupon", [-5, 101])
def test_process_order_invalid_coupon_returns_none(coupon):
    inv.add_item("widget", 10)
    assert process_order("widget", 1, coupon_percent=coupon) is None


def test_process_order_insufficient_stock_returns_none():
    inv.add_item("gadget", 1)
    result = process_order("gadget", 5)
    assert result is None


def test_process_order_decrements_stock():
    inv.add_item("widget", 5)
    process_order("widget", 2)
    assert inv.get_stock("widget") == 3


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


def test_bulk_order_handles_malformed_items_as_none():
    results = bulk_order([{"name": "widget"}])
    assert results == [None]


def test_bulk_order_keeps_process_order_none_signal_for_stock():
    inv.add_item("widget", 1)

    results = bulk_order([{"name": "widget", "qty": 2}])

    assert results == [None]
