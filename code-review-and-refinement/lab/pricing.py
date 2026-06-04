TAX_RATE = 0.08
BULK_DISCOUNT_THRESHOLD = 10
BULK_DISCOUNT_RATE = 0.9


def calculate_price(base_price, quantity):
    subtotal = base_price * quantity
    tax = subtotal * TAX_RATE
    return subtotal + tax


def apply_bulk_discount(price, qty):
    if qty >= BULK_DISCOUNT_THRESHOLD:
        return price * BULK_DISCOUNT_RATE
    return price
