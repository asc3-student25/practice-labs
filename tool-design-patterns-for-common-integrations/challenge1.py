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
    try:
        if idempotency_key and idempotency_key in processed_requests:
            logger.info(f"Duplicate request detected for key: {idempotency_key}")
            return processed_requests[idempotency_key]

        user = get_user(user_id)
        if not user:
            return ToolResponse(
                success=False,
                error_type="UserNotFound",
                message=f"User {user_id} not found",
            ).model_dump_json()

        changed_fields = {}
        target = USERS[user_id]

        if email is not None and target.get("email") != email:
            changed_fields["email"] = {"old": target.get("email"), "new": email}
            target["email"] = email

        if tier is not None and target.get("tier") != tier:
            changed_fields["tier"] = {"old": target.get("tier"), "new": tier}
            target["tier"] = tier

        response_json = ToolResponse(
            success=True,
            message="User updated successfully",
            data={
                "user": target,
                "changed_fields": changed_fields,
                "timestamp": datetime.now().isoformat(),
            },
        ).model_dump_json()

        if idempotency_key:
            processed_requests[idempotency_key] = response_json

        return response_json
    except Exception as e:
        logger.exception("Unexpected error updating user")
        return ToolResponse(
            success=False,
            error_type="UpdateError",
            message=str(e),
        ).model_dump_json()

if __name__ == "__main__":
    user_ids = list(USERS.keys())
    if len(user_ids) < 2:
        raise RuntimeError("Need at least two users in USERS for this demo")

    user1 = user_ids[0]
    user2 = user_ids[1]

    idem_key_1 = "idem-email-001"
    idem_key_2 = "idem-tier-002"

    print("\n" + "=" * 70)
    print("TEST 1: First update (email) with idempotency key")
    print("=" * 70)
    before_user1 = USERS[user1].copy()
    result1 = agent.run_sync(
        f"Update user {user1} email to first_email@example.com using idempotency key {idem_key_1}."
    )
    print(result1)
    print(f"User {user1} before: {before_user1}")
    print(f"User {user1} after : {USERS[user1]}")

    print("\n" + "=" * 70)
    print("TEST 2: Duplicate key with different email (should return cached result)")
    print("=" * 70)
    before_dup_user1 = USERS[user1].copy()
    result2 = agent.run_sync(
        f"Update user {user1} email to second_email@example.com using idempotency key {idem_key_1}."
    )
    print(result2)
    print(f"User {user1} before duplicate call: {before_dup_user1}")
    print(f"User {user1} after duplicate call : {USERS[user1]}")

    print("\n" + "=" * 70)
    print("TEST 3: New key update on different user tier")
    print("=" * 70)
    before_user2 = USERS[user2].copy()
    result3 = agent.run_sync(
        f"Update user {user2} tier to premium using idempotency key {idem_key_2}."
    )
    print(result3)
    print(f"User {user2} before: {before_user2}")
    print(f"User {user2} after : {USERS[user2]}")
