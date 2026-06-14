import os
from pydantic_ai import Agent
from dotenv import load_dotenv
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

load_dotenv()

agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    system_prompt="""You are a customer service assistant with access to
    user account information. Use tools to look up accurate information.
    If a tool returns an error, explain it clearly to the user.""",
)


@agent.tool_plain
def lookup_user(user_id: str) -> str:
    """
    Look up user account by ID.

    Args:
        user_id: User identifier

    Returns:
        User information or error details
    """
    from tools.api_tools import lookup_user as impl

    return impl(user_id)


@agent.tool_plain
def search_user_orders(
    user_id: Optional[str] = None, status: Optional[str] = None
) -> str:
    """Search for orders by user or status."""
    from tools.api_tools import search_user_orders as impl

    return impl(user_id, status)


if __name__ == "__main__":
    # Lookup tool (Core deliverable) — exercises the lookup_user
    # implementation students just wrote.
    result = agent.run_sync("Look up the account details for user-001")
    print(f"\n{result.output}\n")

    # Search tool — exercises the pre-built search_user_orders pattern.
    result = agent.run_sync("Show me all shipped orders")
    print(f"\n{result.output}\n")

    result = agent.run_sync("What orders does user-001 have?")
    print(f"\n{result.output}\n")
