class Inventory:
    def __init__(self, items=[]):
        self.items = items

    """
    Inventory class to manage stock items.

    Parameters:
    - items (list): A list of dictionaries representing items, each with 'name' and 'qty' keys.

    Methods:
    - add_item(name, qty): Adds a new item to the inventory.
    - get_stock(name): Returns the quantity of the specified item. If the item does not exist, returns None.
    - update_stock(name, qty): Updates the quantity of the specified item. If the item does not exist, returns False. Otherwise, updates the quantity and returns True.
    """

    def add_item(self, name, qty):
        self.items.append({"name": name, "qty": qty})

    def get_stock(self, name):
        for item in self.items:
            if item["name"] == name:
                return item["qty"]
        return None

    def update_stock(self, name, qty):
        for item in self.items:
            if item["name"] == name:
                item["qty"] = qty
                return True
        return False
