import os
from pydantic_ai import Agent
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime
from mock_database import ORDERS, INVENTORY

load_dotenv()


class ToolAnalytics:
    """Track tool usage statistics for monitoring and optimization."""

    def __init__(self):
        self.call_counts = defaultdict(int)
        self.call_history = []

    def record_call(self, tool_name: str, args: dict, success: bool):
        """Record a tool invocation with timestamp."""
        self.call_counts[tool_name] += 1
        self.call_history.append(
            {
                "timestamp": datetime.now(),
                "tool": tool_name,
                "args": args,
                "success": success,
            }
        )

    def get_stats(self):
        """Display usage statistics."""
        total = sum(self.call_counts.values())
        print(f"\nTool Usage Statistics ({total} total calls):")
        print("=" * 50)
        for tool, count in sorted(
            self.call_counts.items(), key=lambda x: x[1], reverse=True
        ):
            pct = (count / total) * 100 if total > 0 else 0
            print(f"  {tool}: {count} calls ({pct:.1f}%)")

        print(f"\nMost recent calls:")
        for call in self.call_history[-5:]:  # Show last 5 calls
            timestamp = call["timestamp"].strftime("%H:%M:%S")
            status = "✓" if call["success"] else "✗"
            print(f"  {status} [{timestamp}] {call['tool']} - {call['args']}")


# Initialize analytics tracker
analytics = ToolAnalytics()

agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    system_prompt="""You are a customer service assistant with tool analytics.
    Use your tools to provide accurate information about orders, inventory, and shipping.""",
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
    try:
        if order_id not in ORDERS:
            result = f"Order '{order_id}' not found."
            analytics.record_call("get_order_status", {"order_id": order_id}, False)
            return result

        order = ORDERS[order_id]
        status = order["status"]
        total = order["total"]
        tracking = order.get("tracking") or "Not yet available"

        result = (
            f"Order {order_id}: Status: {status}, Total: ${total:.2f}, "
            f"Tracking: {tracking}"
        )
        analytics.record_call("get_order_status", {"order_id": order_id}, True)
        return result
    except Exception:
        analytics.record_call("get_order_status", {"order_id": order_id}, False)
        raise


@agent.tool_plain
def check_inventory(product_name: str) -> str:
    """
    Check if a product is in stock and get its price.

    Args:
        product_name: Name of the product to check

    Returns:
        Availability and price information, or error if product not found
    """
    try:
        if product_name not in INVENTORY:
            result = f"Product '{product_name}' not found."
            analytics.record_call("check_inventory", {"product_name": product_name}, False)
            return result

        product = INVENTORY[product_name]
        available = product["available"]
        price = product["price"]

        if available > 0:
            result = f"{product_name} is in stock: {available} available at ${price:.2f} each."
            analytics.record_call("check_inventory", {"product_name": product_name}, True)
            return result

        result = f"{product_name} is out of stock. Price: ${price:.2f}."
        analytics.record_call("check_inventory", {"product_name": product_name}, True)
        return result
    except Exception:
        analytics.record_call("check_inventory", {"product_name": product_name}, False)
        raise

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
    try:
        if weight_kg <= 0:
            result = "Weight must be greater than 0 kg."
            analytics.record_call(
                "calculate_shipping",
                {"destination": destination, "weight_kg": weight_kg},
                False,
            )
            return result

        max_weight_kg = 30
        if weight_kg > max_weight_kg:
            result = f"Weight exceeds the maximum supported limit of {max_weight_kg} kg."
            analytics.record_call(
                "calculate_shipping",
                {"destination": destination, "weight_kg": weight_kg},
                False,
            )
            return result

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
        result = (
            f"Shipping to {destination_code}: ${total_cost:.2f}. "
            f"Estimated delivery: {delivery_estimate}."
        )
        analytics.record_call(
            "calculate_shipping",
            {"destination": destination, "weight_kg": weight_kg},
            True,
        )
        return result
    except Exception:
        analytics.record_call(
            "calculate_shipping",
            {"destination": destination, "weight_kg": weight_kg},
            False,
        )
        raise


if __name__ == "__main__":
    queries = [
        "What's the status of order ORD-1001?",
        "Can you check order ORD-9999 for me?",
        "Is widget in stock?",
        "Check inventory for gadget.",
        "Do you have unknown in inventory?",
        "Calculate shipping to US for 2.5 kg.",
        "How much is shipping to moon for 2.5 kg?",
        "Calculate shipping to CA for -1 kg.",
        "Please check order ORD-1001 again.",
        "Is widget still available?",
    ]

    for query in queries:
        response = agent.run_sync(query)
        output = getattr(response, "output", response)
        print(f"Q: {query}")
        print(f"A: {output}\n")

    analytics.get_stats()
