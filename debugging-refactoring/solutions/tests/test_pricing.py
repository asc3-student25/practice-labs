import pytest

from models import Item
from pricing import TAX_RATE, calculate_price, get_discounted_price


def _item(price):
    return Item(sku="widget", name="Widget", price=price)


def test_calculate_price_applies_tax():
    result = calculate_price(_item(10.00), 2)
    assert result == pytest.approx(20.00 * (1 + TAX_RATE))


def test_calculate_price_zero_quantity():
    assert calculate_price(_item(10.00), 0) == 0.0


def test_get_discounted_price_applies_discount_after_tax():
    result = get_discounted_price(_item(10.00), 2, discount_percent=10)
    expected = 20.00 * (1 + TAX_RATE) * 0.9
    assert result == pytest.approx(expected)


def test_get_discounted_price_zero_discount_matches_calculate_price():
    result_with = get_discounted_price(_item(5.00), 3, discount_percent=0)
    result_without = calculate_price(_item(5.00), 3)
    assert result_with == pytest.approx(result_without)
