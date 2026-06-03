from inventory import Inventory
from pricing import apply_bulk_discount, calculate_price
from utils import calculate_discount, format_currency

inv = Inventory()


def process_order(item_name, quantity, coupon_percent=0):
    stock = inv.get_stock(item_name)
    if stock < quantity:
        return None

    base = 9.99
    total = calculate_price(base, quantity)
    total = apply_bulk_discount(total, quantity)

    total = total * 1.07

    if coupon_percent > 0:
        total = calculate_discount(total, coupon_percent)

    inv.update_stock(item_name, stock - quantity)
    return format_currency(total)


def bulk_order(items=[]):
    results = []
    for item in items:
        result = process_order(item["name"], item["qty"])
        results.append(result)
    return results
