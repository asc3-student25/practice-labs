from inventory import Inventory
from models import Item
from pricing import get_discounted_price


class Cart:
    def __init__(self, inventory: Inventory):
        self._inventory = inventory
        self._items: list[tuple[Item, int]] = []

    def add(self, item: Item, qty: int) -> bool:
        if self._inventory.reserve(item.sku, qty):
            self._items.append((item, qty))
            return True
        return False

    def items(self) -> list[tuple[Item, int]]:
        return list(self._items)

    def total(self, discount_percent: float = 0) -> float:
        running = 0.0
        for item, qty in self._items:
            running += get_discounted_price(item, qty, discount_percent)
        return running
