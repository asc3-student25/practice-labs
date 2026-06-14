import os
from pydantic_ai import Agent
from dotenv import load_dotenv
from typing import Optional
import logging
import contextvars
import uuid

# Configure logging with custom format
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

# Import tools
from tools.api_tools import lookup_user as lookup_user_impl
from tools.api_tools import search_user_orders as search_orders_impl

# Thread-local correlation ID storage
correlation_id_var = contextvars.ContextVar("correlation_id", default=None)


def get_correlation_id() -> str:
    """Get or create correlation ID for current request."""
    # YOUR CODE HERE
    # [SOLUTION]
    correlation_id = correlation_id_var.get()
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
        correlation_id_var.set(correlation_id)
    return correlation_id
    # [/SOLUTION]


def log_with_correlation(message: str, level: str = "INFO"):
    """Log message with correlation ID."""
    # YOUR CODE HERE
    # [SOLUTION]
    correlation_id = get_correlation_id()
    logger.log(getattr(logging, level), f"[correlation_id={correlation_id}] {message}")
    # [/SOLUTION]


agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    system_prompt="""You are a customer service assistant with comprehensive
    access to user and order information. Use your tools to provide accurate
    information.""",
)


@agent.tool_plain
def lookup_user(user_id: str) -> str:
    """Look up user with correlation tracking."""
    # YOUR CODE HERE
    # [SOLUTION]
    log_with_correlation(f"Starting user lookup: {user_id}")

    try:
        result = lookup_user_impl(user_id)
        log_with_correlation(f"User lookup completed: {user_id}")
        return result
    except Exception as e:
        log_with_correlation(f"User lookup failed: {e}", level="ERROR")
        raise
    # [/SOLUTION]


@agent.tool_plain
def search_user_orders(
    user_id: Optional[str] = None, status: Optional[str] = None
) -> str:
    """Search orders with correlation tracking."""
    # YOUR CODE HERE
    # [SOLUTION]
    log_with_correlation(f"Starting order search: user_id={user_id}, status={status}")

    try:
        result = search_orders_impl(user_id, status)
        log_with_correlation(f"Order search completed")
        return result
    except Exception as e:
        log_with_correlation(f"Order search failed: {e}", level="ERROR")
        raise
    # [/SOLUTION]


if __name__ == "__main__":
    # YOUR CODE HERE
    # [SOLUTION]
    print("=== Challenge 2: Correlation ID Tracking ===\n")
    print("Watch the console logs for correlation IDs...\n")

    # Request 1: Single tool call
    print("Request 1: Simple user lookup")
    print("-" * 50)
    correlation_id_var.set(str(uuid.uuid4()))  # Set unique ID for this request
    log_with_correlation("New request started")
    result = agent.run_sync("Get user-001's information")
    log_with_correlation("Request completed")
    print(result.output)

    print("\n" + "=" * 50 + "\n")

    # Request 2: Multi-tool call
    print("Request 2: Complex query requiring multiple tools")
    print("-" * 50)
    correlation_id_var.set(str(uuid.uuid4()))  # Set unique ID for this request
    log_with_correlation("New request started")
    result = agent.run_sync("Get user-001's info and show me all their orders")
    log_with_correlation("Request completed")
    print(result.output)

    print("\n" + "=" * 50 + "\n")

    # Request 3: Another request with different correlation ID
    print("Request 3: Search for shipped orders")
    print("-" * 50)
    correlation_id_var.set(str(uuid.uuid4()))  # Set unique ID for this request
    log_with_correlation("New request started")
    result = agent.run_sync("Show me all shipped orders")
    log_with_correlation("Request completed")
    print(result.output)

    print("\n" + "=" * 50)
    print(
        "\nNote: Check the log output above. Each request has a unique correlation_id,"
    )
    print("and all tool calls within that request share the same correlation_id.")
    print(
        "This makes it easy to trace the complete execution flow of a single user request."
    )
    # [/SOLUTION]
