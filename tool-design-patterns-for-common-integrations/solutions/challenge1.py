import os
from pydantic_ai import Agent
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime
import logging
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Import mock API and models
from mock_api import USERS, get_user
from tools.models import ToolResponse


class UpdateRequest(BaseModel):
    """User update request."""

    user_id: str
    email: Optional[str] = None
    tier: Optional[str] = None
    idempotency_key: str  # Prevents duplicate operations


# Track processed requests for idempotency
processed_requests = {}

agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    system_prompt="""You are a customer service assistant with the ability
    to update user account information. Always use unique idempotency keys
    for update operations to prevent duplicate processing.""",
)


@agent.tool_plain
def update_user(
    user_id: str,
    email: Optional[str] = None,
    tier: Optional[str] = None,
    idempotency_key: str = None,
) -> str:
    """
    Update user information idempotently.

    Args:
        user_id: User to update
        email: New email (optional)
        tier: New tier (optional)
        idempotency_key: Unique request identifier

    Returns:
        Update result with idempotency protection
    """
    # YOUR CODE HERE
    # [SOLUTION]
    # Check idempotency
    if idempotency_key and idempotency_key in processed_requests:
        logger.info(f"Duplicate request detected: {idempotency_key}")
        return processed_requests[idempotency_key]

    try:
        # Validate user exists
        user_result = get_user(user_id)
        if not user_result["success"]:
            response = ToolResponse(
                success=False,
                error_type="UserNotFound",
                error_message=f"User {user_id} does not exist",
            )
            return response.model_dump_json()

        # Apply updates
        user = USERS[user_id]
        updates_made = []

        if email and email != user["email"]:
            user["email"] = email
            updates_made.append(f"email updated to {email}")

        if tier and tier != user["tier"]:
            user["tier"] = tier
            updates_made.append(f"tier updated to {tier}")

        if not updates_made:
            response = ToolResponse(
                success=True,
                data={
                    "user": user,
                    "message": "No changes needed",
                    "updated_at": datetime.now().isoformat(),
                },
            )
        else:
            response = ToolResponse(
                success=True,
                data={
                    "user": user,
                    "changes": updates_made,
                    "updated_at": datetime.now().isoformat(),
                },
            )

        result_json = response.model_dump_json()

        # Cache for idempotency
        if idempotency_key:
            processed_requests[idempotency_key] = result_json

        logger.info(f"User updated: {user_id} - {updates_made}")
        return result_json

    except Exception as e:
        logger.error(f"Update failed: {e}")
        return ToolResponse(
            success=False, error_type="UpdateError", error_message=str(e)
        ).model_dump_json()
    # [/SOLUTION]


if __name__ == "__main__":
    # YOUR CODE HERE
    # [SOLUTION]
    print("=== Challenge 1: Idempotent Write Operations ===\n")

    # First update with idempotency key
    print("First request with idempotency key 'update-123':")
    result = agent.run_sync(
        "Update user-001's email to newemail@example.com, use idempotency key update-123"
    )
    print(result.output)

    print("\n" + "=" * 50 + "\n")

    # Duplicate request with same idempotency key - should return cached result
    print("Duplicate request with same idempotency key 'update-123':")
    result = agent.run_sync(
        "Update user-001's email to differentemail@example.com, use idempotency key update-123"
    )
    print(result.output)
    print(
        "\n(Notice: Email should NOT be 'differentemail@example.com' - cached result returned)"
    )

    print("\n" + "=" * 50 + "\n")

    # New request with different idempotency key
    print("New request with different idempotency key 'update-456':")
    result = agent.run_sync(
        "Update user-002's tier to premium, use idempotency key update-456"
    )
    print(result.output)
    # [/SOLUTION]
