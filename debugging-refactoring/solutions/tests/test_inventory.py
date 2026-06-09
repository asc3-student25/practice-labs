from inventory import Inventory


def test_restock_sets_stock_level():
    inv = Inventory()
    inv.restock("widget", 5)
    assert inv.get_stock("widget") == 5


def test_can_fulfill_when_stock_equals_request():
    inv = Inventory()
    inv.restock("widget", 3)
    assert inv.can_fulfill("widget", 3) is True


def test_cannot_fulfill_when_request_exceeds_stock():
    inv = Inventory()
    inv.restock("widget", 3)
    assert inv.can_fulfill("widget", 4) is False


def test_reserve_decrements_stock_on_success():
    inv = Inventory()
    inv.restock("widget", 5)
    assert inv.reserve("widget", 3) is True
    assert inv.get_stock("widget") == 2


def test_reserve_fails_without_modifying_stock():
    inv = Inventory()
    inv.restock("widget", 2)
    assert inv.reserve("widget", 5) is False
    assert inv.get_stock("widget") == 2


def test_fresh_inventory_is_empty():
    inv = Inventory()
    assert inv.get_stock("widget") == 0
    assert inv.get_stock("gadget") == 0


def test_two_inventories_are_independent():
    a = Inventory()
    b = Inventory()
    a.restock("widget", 10)
    assert b.get_stock("widget") == 0


def test_check_all_in_stock_returns_status_per_item():
    inv = Inventory()
    inv.restock("widget", 10)
    inv.restock("gadget", 1)
    result = inv.check_all_in_stock([("widget", 5), ("gadget", 2), ("unknown", 1)])
    assert result == [True, False, False]
