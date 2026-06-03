def calculate_discount(price, discount_percent):
    """Return ``price`` reduced by ``discount_percent`` (e.g. 15 for 15%)."""
    return price - (price * discount_percent / 100)


def format_currency(amount):
    """Format ``amount`` as a two-decimal-place dollar string."""
    return f"${amount:.2f}"
