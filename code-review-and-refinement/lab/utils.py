"""
Calculate the discounted price.

Parameters:
- price (float): The original price.
- discount_percent (float): The discount percentage.

Returns:
- float: The discounted price.
"""
def calculate_discount(price, discount_percent):
    return price - (price * discount_percent / 100)


def format_currency(amount):
    return f"${amount:.2f}"
