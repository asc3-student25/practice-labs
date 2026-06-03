TAX_RATE = 0.08
BULK_DISCOUNT_THRESHOLD = 10
BULK_DISCOUNT_RATE = 0.9


def calculate_price(base_price, quantity):
    """Return the pre-discount total including tax for ``quantity`` units of ``base_price``."""
    subtotal = base_price * quantity
    return subtotal + (subtotal * TAX_RATE)


def apply_bulk_discount(price, qty):
    """Apply the bulk discount when ``qty`` meets the threshold."""
    if qty >= BULK_DISCOUNT_THRESHOLD:
        return price * BULK_DISCOUNT_RATE
    return price
