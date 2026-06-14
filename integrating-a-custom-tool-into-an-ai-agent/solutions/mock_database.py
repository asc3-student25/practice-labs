from datetime import datetime, timedelta

# Mock order database
ORDERS = {
    "ORD-001": {
        "order_id": "ORD-001",
        "customer": "John Smith",
        "status": "shipped",
        "items": ["Laptop", "Mouse"],
        "total": 1299.99,
        "tracking": "TRACK123456",
    },
    "ORD-002": {
        "order_id": "ORD-002",
        "customer": "Jane Doe",
        "status": "processing",
        "items": ["Keyboard", "Monitor"],
        "total": 450.00,
        "tracking": None,
    },
}

# Mock inventory
INVENTORY = {
    "Laptop": {"available": 15, "price": 1199.99},
    "Mouse": {"available": 50, "price": 29.99},
    "Keyboard": {"available": 0, "price": 89.99},
    "Monitor": {"available": 8, "price": 299.99},
}
