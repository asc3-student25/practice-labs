import os
from pydantic_ai import Agent
from dotenv import load_dotenv
from mock_database import ORDERS, INVENTORY

load_dotenv()

agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    system_prompt="""You are a customer service assistant with comprehensive
    order inquiry capabilities. Use your tools to provide complete order information
    including inventory status for all items.""",
)


@agent.tool_plain
def get_order_status(order_id: str) -> str:
    """Look up the current status of an order."""
    if order_id not in ORDERS:
        return f"Order {order_id} not found in the system."

    order = ORDERS[order_id]
    status = order["status"]
    total = order["total"]
    # See customer_agent.py:get_order_status — ORD-002 stores tracking=None,
    # so .get("tracking", "Not yet available") returns None. Use `or` so the
    # default applies for both missing keys and present-but-None.
    tracking = order.get("tracking") or "Not yet available"

    return f"Order {order_id}: Status is '{status}', Total: ${total:.2f}, Tracking: {tracking}"


@agent.tool_plain
def check_inventory(product_name: str) -> str:
    """Check if a product is in stock and get its price."""
    if product_name not in INVENTORY:
        return f"Product '{product_name}' not found in inventory."

    product = INVENTORY[product_name]
    available = product["available"]
    price = product["price"]

    if available > 0:
        return f"{product_name}: In stock ({available} units available), Price: ${price:.2f}"
    else:
        return f"{product_name}: Out of stock, Price: ${price:.2f}"


@agent.tool_plain
def calculate_shipping(destination: str, weight_kg: float) -> str:
    """Calculate shipping cost based on destination and weight."""
    if weight_kg <= 0:
        return "Error: Weight must be positive"

    if weight_kg > 30:
        return "Error: Package exceeds maximum weight limit (30kg)"

    base_rates = {"US": 10.00, "CA": 12.00, "UK": 15.00, "MX": 18.00}

    base_rate = base_rates.get(destination.upper(), 20.00)

    if weight_kg > 1:
        weight_charge = (weight_kg - 1) * 2.00
    else:
        weight_charge = 0

    total_cost = base_rate + weight_charge

    delivery_days = {
        "US": "3-5 business days",
        "CA": "5-7 business days",
        "UK": "7-10 business days",
        "MX": "7-10 business days",
    }

    estimated_delivery = delivery_days.get(destination.upper(), "10-14 business days")

    return f"Shipping to {destination.upper()}: ${total_cost:.2f}, Estimated delivery: {estimated_delivery}"


@agent.tool_plain
def complete_order_inquiry(order_id: str) -> str:
    """
    Provide comprehensive order information including items and availability.

    This tool demonstrates a multi-tool workflow pattern where one tool
    combines data from multiple sources (order database and inventory system)
    to provide a complete response.

    Args:
        order_id: The unique identifier for the order

    Returns:
        Complete order details with inventory status for all items
    """
    # YOUR CODE HERE
    # Hint: Combine order data with inventory status for each item
    # [SOLUTION]
    if order_id not in ORDERS:
        return f"Order {order_id} not found."

    order = ORDERS[order_id]

    # Build comprehensive response combining order and inventory data
    response = f"Order {order_id} Details:\n"
    response += f"Status: {order['status']}\n"
    response += f"Total: ${order['total']:.2f}\n"
    response += f"\nItems:\n"

    for item in order["items"]:
        if item in INVENTORY:
            avail = INVENTORY[item]["available"]
            price = INVENTORY[item]["price"]
            stock_status = "In stock" if avail > 0 else "Out of stock"
            response += f"- {item}: {stock_status} (${price:.2f})\n"
        else:
            response += f"- {item}: Unknown availability\n"

    if order["tracking"]:
        response += f"\nTracking: {order['tracking']}"
    else:
        response += f"\nTracking: Not yet available"

    return response
    # [/SOLUTION]


if __name__ == "__main__":
    # YOUR CODE HERE
    # [SOLUTION]
    print("=== Challenge 1: Complete Order Inquiry ===\n")

    # Test comprehensive order inquiry
    result = agent.run_sync(
        "Give me complete details on order ORD-001, including inventory status for all items"
    )
    print(result.output)

    print("\n" + "=" * 50 + "\n")

    result = agent.run_sync("Show me everything about order ORD-002")
    print(result.output)
    # [/SOLUTION]
