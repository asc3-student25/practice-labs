class Inventory:
    def __init__(self) -> None:
        self._stock: dict[str, int] = {}

    def restock(self, sku: str, qty: int) -> None:
        self._stock[sku] = self._stock.get(sku, 0) + qty

    def get_stock(self, sku: str) -> int:
        return self._stock.get(sku, 0)

    def can_fulfill(self, sku: str, qty: int) -> bool:
        return self.get_stock(sku) >= qty

    def reserve(self, sku: str, qty: int) -> bool:
        if not self.can_fulfill(sku, qty):
            return False
        self._stock[sku] -= qty
        return True

    def check_all_in_stock(self, items_needed: list[tuple[str, int]]) -> list[bool]:
        result = []
        for sku, qty in items_needed:
            found = False
            for known_sku, known_qty in self._stock.items():
                if known_sku == sku and known_qty >= qty:
                    found = True
                    break
            result.append(found)
        return result
