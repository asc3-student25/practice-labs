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
    correlation_id = correlation_id_var.get()
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
        correlation_id_var.set(correlation_id)
    return correlation_id


def log_with_correlation(message: str, level: str = "INFO"):
    """Log message with correlation ID."""
    correlation_id = get_correlation_id()
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, f"[correlation_id={correlation_id}] {message}")


agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    system_prompt="""You are a customer service assistant with comprehensive
    access to user and order information. Use your tools to provide accurate
    information.""",
)


@agent.tool_plain
def lookup_user(user_id: str) -> str:
    """Look up user with correlation tracking."""
    log_with_correlation(f"Starting lookup_user for user_id={user_id}")
    try:
        result = lookup_user_impl(user_id)
        log_with_correlation(f"Completed lookup_user for user_id={user_id}")
        return result
    except Exception as exc:
        log_with_correlation(
            f"lookup_user failed for user_id={user_id}: {exc}", level="ERROR"
        )
        raise


@agent.tool_plain
def search_user_orders(
    user_id: Optional[str] = None, status: Optional[str] = None
) -> str:
    """Search orders with correlation tracking."""
    log_with_correlation(
        f"Starting search_user_orders for user_id={user_id}, status={status}"
    )
    try:
        result = search_orders_impl(user_id, status)
        log_with_correlation(
            f"Completed search_user_orders for user_id={user_id}, status={status}"
        )
        return result
    except Exception as exc:
        log_with_correlation(
            f"search_user_orders failed for user_id={user_id}, status={status}: {exc}",
            level="ERROR",
        )
        raise


if __name__ == "__main__":
    requests = [
        (
            "single-tool lookup",
            "Look up user with id 'user_123' and return only the user details.",
        ),
        (
            "multi-tool lookup + orders",
            "For user 'user_123', first look up the user and then search their open orders. Summarize both.",
        ),
        (
            "search-only query",
            "Search orders with status 'shipped' and summarize the results.",
        ),
    ]

    for label, prompt in requests:
        correlation_id_var.set(str(uuid.uuid4()))
        print("\n" + "=" * 72)
        print(f"REQUEST: {label}")
        print("=" * 72)

        log_with_correlation(f"request started: {label}")
        response = agent.run_sync(prompt)
        log_with_correlation(f"request completed: {label}")

        print("\nAgent output:")
        print(response.output)
        print("=" * 72)
