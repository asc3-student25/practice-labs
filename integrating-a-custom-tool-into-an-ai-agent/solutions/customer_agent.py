import os
from pydantic_ai import Agent
from dotenv import load_dotenv
from mock_database import ORDERS, INVENTORY

load_dotenv()

agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    system_prompt="""You are a customer service assistant. Use your tools to
    look up order information, check inventory, and calculate shipping costs.
    Always provide accurate, helpful responses based on the tool results.""",
)


@agent.tool_plain
def get_order_status(order_id: str) -> str:
    """
    Look up the current status of an order.

    Args:
        order_id: The unique identifier for the order (e.g., 'ORD-001')

    Returns:
        String containing order status and details, or error message
    """
    # YOUR CODE HERE
    # [SOLUTION]
    if order_id not in ORDERS:
        return f"Order {order_id} not found in the system."

    order = ORDERS[order_id]
    status = order["status"]
    total = order["total"]
    # Some orders (e.g. ORD-002) have tracking=None rather than a missing
    # "tracking" key. dict.get(key, default) returns the *value* when the
    # key is present, so .get("tracking", "Not yet available") would
    # return None and we'd format the string as "Tracking: None". Use an
    # `or` fallback to handle both missing keys and present-but-None.
    tracking = order.get("tracking") or "Not yet available"

    return f"Order {order_id}: Status is '{status}', Total: ${total:.2f}, Tracking: {tracking}"
    # [/SOLUTION]


@agent.tool_plain
def check_inventory(product_name: str) -> str:
    """
    Check if a product is in stock and get its price.

    Args:
        product_name: Name of the product to check

    Returns:
        Availability and price information, or error if product not found
    """
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
    """
    Calculate shipping cost based on destination and weight.

    Args:
        destination: Destination country code (US, CA, UK, etc.)
        weight_kg: Package weight in kilograms

    Returns:
        Estimated shipping cost and delivery time
    """
    # Validate inputs
    if weight_kg <= 0:
        return "Error: Weight must be positive"

    if weight_kg > 30:
        return "Error: Package exceeds maximum weight limit (30kg)"

    # Simple shipping cost calculation
    base_rates = {"US": 10.00, "CA": 12.00, "UK": 15.00, "MX": 18.00}

    # Default rate for other countries
    base_rate = base_rates.get(destination.upper(), 20.00)

    # Add weight surcharge ($2 per kg over 1kg)
    if weight_kg > 1:
        weight_charge = (weight_kg - 1) * 2.00
    else:
        weight_charge = 0

    total_cost = base_rate + weight_charge

    # Estimate delivery time
    delivery_days = {
        "US": "3-5 business days",
        "CA": "5-7 business days",
        "UK": "7-10 business days",
        "MX": "7-10 business days",
    }

    estimated_delivery = delivery_days.get(destination.upper(), "10-14 business days")

    return f"Shipping to {destination.upper()}: ${total_cost:.2f}, Estimated delivery: {estimated_delivery}"


if __name__ == "__main__":
    # YOUR CODE HERE
    # [SOLUTION]
    # Test basic tool functionality
    print("=== Testing get_order_status ===")
    result = agent.run_sync("What's the status of order ORD-001?")
    print(result.output)

    print("\n=== Testing check_inventory ===")
    result = agent.run_sync("Is Keyboard in stock?")
    print(result.output)

    print("\n=== Testing calculate_shipping ===")
    result = agent.run_sync("How much to ship 3kg to US?")
    print(result.output)
    # [/SOLUTION]
