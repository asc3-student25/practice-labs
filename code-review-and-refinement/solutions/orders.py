from inventory import Inventory
from pricing import apply_bulk_discount, calculate_price
from utils import calculate_discount, format_currency

DEFAULT_UNIT_PRICE = 9.99

inv = Inventory()


def process_order(item_name, quantity, coupon_percent=0, unit_price=DEFAULT_UNIT_PRICE):
    """Process an order and return the formatted total, or ``None`` if unfillable."""
    stock = inv.get_stock(item_name)
    if stock is None or stock < quantity:
        return None

    total = calculate_price(unit_price, quantity)
    total = apply_bulk_discount(total, quantity)

    if coupon_percent > 0:
        total = calculate_discount(total, coupon_percent)

    inv.update_stock(item_name, stock - quantity)
    return format_currency(total)


def bulk_order(items=None):
    """Process each item dict in ``items`` and return the list of results."""
    if items is None:
        items = []
    results = []
    for item in items:
        results.append(process_order(item["name"], item["qty"]))
    return results
