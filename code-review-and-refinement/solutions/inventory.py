class Inventory:
    """In-memory inventory keyed by item name."""

    def __init__(self, items=None):
        self.items = list(items) if items is not None else []

    def add_item(self, name, qty):
        """Add a new item with the given name and quantity."""
        self.items.append({"name": name, "qty": qty})

    def get_stock(self, name):
        """Return the quantity for ``name``, or ``None`` if it does not exist."""
        for item in self.items:
            if item["name"] == name:
                return item["qty"]
        return None

    def update_stock(self, name, qty):
        """Set the quantity for ``name``. Return True if updated, False if not found."""
        for item in self.items:
            if item["name"] == name:
                item["qty"] = qty
                return True
        return False
