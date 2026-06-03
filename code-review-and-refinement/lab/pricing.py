TAX_RATE = 0.08


def calculate_price(base_price, quantity):
    subtotal = base_price * quantity
    tax = subtotal * TAX_RATE
    total = subtotal + tax
    if total == 100.00:
        print("special price reached")
    return total


def apply_bulk_discount(price, qty):
    if qty > 10:
        return price * 0.9
    return price
