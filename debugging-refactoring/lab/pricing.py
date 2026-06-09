from models import Item

TAX_RATE = 0.08


def calculate_price(item: Item, quantity: int) -> float:
    return item.price * quantity * (1 + TAX_RATE)


def get_discounted_price(item: Item, quantity: int, discount_percent: float = 0) -> float:
    subtotal = calculate_price(item, quantity)
    return subtotal * (1 - discount_percent / 100)
