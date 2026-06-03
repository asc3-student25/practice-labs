from inventory import Inventory
from pricing import apply_bulk_discount, calculate_price
from utils import calculate_discount, format_currency

DEFAULT_UNIT_PRICE = 9.99

inv = Inventory()


def process_order(item_name, quantity, coupon_percent=0, unit_price=DEFAULT_UNIT_PRICE):
    stock = inv.get_stock(item_name)
    if stock is None:
        return None

    if quantity <= 0:
        return None

    if not (0 <= coupon_percent <= 100):
        return None

    if stock < quantity:
        return None

    total = calculate_price(unit_price, quantity)
    total = apply_bulk_discount(total, quantity)

    if coupon_percent > 0:
        total = calculate_discount(total, coupon_percent)

    inv.update_stock(item_name, stock - quantity)
    return format_currency(total)


def bulk_order(items=None):
    if items is None:
        items = []

    results = []
    for item in items:
        if "name" not in item or "qty" not in item:
            results.append(None)
            continue
        results.append(process_order(item["name"], item["qty"]))
    return results
