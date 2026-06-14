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
    if order_id not in ORDERS:
        return f"Order '{order_id}' not found."

    order = ORDERS[order_id]
    status = order["status"]
    total = order["total"]
    tracking = order.get("tracking") or "Not yet available"

    return f"Order {order_id}: Status: {status}, Total: ${total:.2f}, Tracking: {tracking}"
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
        return f"Product '{product_name}' not found."

    product = INVENTORY[product_name]
    available = product["available"]
    price = product["price"]

    if available > 0:
        return f"{product_name} is in stock: {available} available at ${price:.2f} each."

    return f"{product_name} is out of stock. Price: ${price:.2f}."

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
    if weight_kg <= 0:
        return "Weight must be greater than 0 kg."

    max_weight_kg = 30
    if weight_kg > max_weight_kg:
        return f"Weight exceeds the maximum supported limit of {max_weight_kg} kg."

    destination_code = destination.strip().upper()

    base_rates = {
        "US": 5.99,
        "CA": 7.99,
        "UK": 9.99,
        "MX": 8.49,
    }
    fallback_base_rate = 12.99
    base_rate = base_rates.get(destination_code, fallback_base_rate)

    surcharge_per_kg_over_1 = 1.25
    weight_surcharge = max(0.0, weight_kg - 1) * surcharge_per_kg_over_1

    delivery_windows = {
        "US": "2-4 business days",
        "CA": "4-6 business days",
        "UK": "5-8 business days",
        "MX": "4-7 business days",
    }
    delivery_estimate = delivery_windows.get(destination_code, "7-12 business days")

    total_cost = base_rate + weight_surcharge
    return (
        f"Shipping to {destination_code}: ${total_cost:.2f}. "
        f"Estimated delivery: {delivery_estimate}."
    )


if __name__ == "__main__":
    print("[Order Status]")
    result = agent.run_sync("What's the status of order ORD-001?")
    print(result.output)

    print("[Inventory]")
    result = agent.run_sync("Do you have Laptop in stock, and what is the price?")
    print(result.output)

    print("[Shipping]")
    result = agent.run_sync("Calculate shipping to US for a 2.5 kg package.")
    print(result.output)
