"""Mock API server for testing tools."""

# Simulated data stores
USERS = {
    "user-001": {
        "id": "user-001",
        "name": "John Smith",
        "email": "john@example.com",
        "tier": "premium",
    },
    "user-002": {
        "id": "user-002",
        "name": "Jane Doe",
        "email": "jane@example.com",
        "tier": "basic",
    },
}

ORDERS = {
    "ord-001": {
        "id": "ord-001",
        "user_id": "user-001",
        "status": "shipped",
        "total": 299.99,
    },
    "ord-002": {
        "id": "ord-002",
        "user_id": "user-002",
        "status": "processing",
        "total": 89.99,
    },
}

PRODUCTS = {
    "prod-001": {"id": "prod-001", "name": "Laptop", "price": 1299.99, "stock": 15},
    "prod-002": {"id": "prod-002", "name": "Mouse", "price": 29.99, "stock": 0},
}


def get_user(user_id: str):
    """Simulate user lookup."""
    if user_id in USERS:
        return {"success": True, "data": USERS[user_id]}
    return {
        "success": False,
        "error": "UserNotFound",
        "message": f"User {user_id} not found",
    }


def search_orders(user_id: str = None, status: str = None):
    """Simulate order search."""
    results = list(ORDERS.values())

    if user_id:
        results = [o for o in results if o["user_id"] == user_id]
    if status:
        results = [o for o in results if o["status"] == status]

    return {"success": True, "data": results, "count": len(results)}
