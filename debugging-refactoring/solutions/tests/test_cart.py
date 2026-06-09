import pytest

from cart import Cart
from inventory import Inventory
from models import Item
from pricing import TAX_RATE


def _inventory_with_widget(qty=10):
    inv = Inventory()
    inv.restock("widget", qty)
    return inv


def _widget(price=5.00):
    return Item(sku="widget", name="Widget", price=price)


def test_add_succeeds_when_stock_available():
    cart = Cart(_inventory_with_widget(5))
    assert cart.add(_widget(), 2) is True
    assert cart.items() == [(_widget(), 2)]


def test_add_fails_when_stock_insufficient():
    cart = Cart(_inventory_with_widget(1))
    assert cart.add(_widget(), 5) is False
    assert cart.items() == []


def test_total_sums_each_line_with_tax():
    cart = Cart(_inventory_with_widget(10))
    cart.add(_widget(10.00), 2)
    expected = 20.00 * (1 + TAX_RATE)
    assert cart.total() == pytest.approx(expected)


def test_total_applies_discount_percent_to_each_line():
    cart = Cart(_inventory_with_widget(10))
    cart.add(_widget(10.00), 2)
    expected = 20.00 * (1 + TAX_RATE) * 0.9
    assert cart.total(discount_percent=10) == pytest.approx(expected)
