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
    """Look up the current status of an order (with analytics tracking)."""
    # YOUR CODE HERE
    # Hint: Wrap the tool logic with analytics.record_call()
    # [SOLUTION]
    try:
        if order_id not in ORDERS:
            analytics.record_call(
                "get_order_status", {"order_id": order_id}, success=False
            )
            return f"Order {order_id} not found in the system."

        order = ORDERS[order_id]
        status = order["status"]
        total = order["total"]
        # See customer_agent.py:get_order_status — ORD-002 stores tracking=None,
        # so .get("tracking", "Not yet available") returns None and the analytics
        # row records success=True while the response says "Tracking: None".
        # Use `or` so the default applies for both missing keys and present-but-None.
        tracking = order.get("tracking") or "Not yet available"

        analytics.record_call("get_order_status", {"order_id": order_id}, success=True)
        return f"Order {order_id}: Status is '{status}', Total: ${total:.2f}, Tracking: {tracking}"
    except Exception as e:
        analytics.record_call("get_order_status", {"order_id": order_id}, success=False)
        raise
    # [/SOLUTION]


@agent.tool_plain
def check_inventory(product_name: str) -> str:
    """Check if a product is in stock (with analytics tracking)."""
    # YOUR CODE HERE
    # Hint: Record analytics for both success and failure cases
    # [SOLUTION]
    try:
        if product_name not in INVENTORY:
            analytics.record_call(
                "check_inventory", {"product_name": product_name}, success=False
            )
            return f"Product '{product_name}' not found in inventory."

        product = INVENTORY[product_name]
        available = product["available"]
        price = product["price"]

        analytics.record_call(
            "check_inventory", {"product_name": product_name}, success=True
        )

        if available > 0:
            return f"{product_name}: In stock ({available} units available), Price: ${price:.2f}"
        else:
            return f"{product_name}: Out of stock, Price: ${price:.2f}"
    except Exception as e:
        analytics.record_call(
            "check_inventory", {"product_name": product_name}, success=False
        )
        raise
    # [/SOLUTION]


@agent.tool_plain
def calculate_shipping(destination: str, weight_kg: float) -> str:
    """Calculate shipping cost (with analytics tracking)."""
    # YOUR CODE HERE
    # Hint: Track analytics at multiple exit points (validation failures and success)
    # [SOLUTION]
    try:
        if weight_kg <= 0:
            analytics.record_call(
                "calculate_shipping",
                {"destination": destination, "weight_kg": weight_kg},
                success=False,
            )
            return "Error: Weight must be positive"

        if weight_kg > 30:
            analytics.record_call(
                "calculate_shipping",
                {"destination": destination, "weight_kg": weight_kg},
                success=False,
            )
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

        analytics.record_call(
            "calculate_shipping",
            {"destination": destination, "weight_kg": weight_kg},
            success=True,
        )

        return f"Shipping to {destination.upper()}: ${total_cost:.2f}, Estimated delivery: {estimated_delivery}"
    except Exception as e:
        analytics.record_call(
            "calculate_shipping",
            {"destination": destination, "weight_kg": weight_kg},
            success=False,
        )
        raise
    # [/SOLUTION]


if __name__ == "__main__":
    # YOUR CODE HERE
    # [SOLUTION]
    print("=== Challenge 2: Tool Usage Analytics ===\n")

    # Run multiple queries to generate analytics data
    queries = [
        "Status of ORD-001?",
        "Is Laptop in stock?",
        "Status of ORD-002?",
        "Shipping cost to US for 3kg?",
        "Is Mouse available?",
        "What about Keyboard?",
        "Shipping to CA for 5kg?",
        "Status of ORD-001?",  # Repeat
        "Is Laptop in stock?",  # Repeat
    ]

    print("Running queries to generate analytics...\n")
    for i, query in enumerate(queries, 1):
        print(f'{i}. "{query}"')
        result = agent.run_sync(query)

    # Display analytics
    print("\n" + "=" * 50)
    analytics.get_stats()
    # [/SOLUTION]
