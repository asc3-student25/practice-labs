import logging
from typing import Optional
from tools.models import ToolResponse, User, Order
from mock_api import get_user, search_orders

logger = logging.getLogger(__name__)


def lookup_user(user_id: str) -> str:
    """
    Look up user account by ID.

    Args:
        user_id: User identifier (format: user-XXX)

    Returns:
        JSON string with user information or error details
    """
    # YOUR CODE HERE
    # [SOLUTION]
    logger.info(f"Looking up user: {user_id}")

    try:
        # Call backend API
        result = get_user(user_id)

        if result["success"]:
            user = User(**result["data"])
            response = ToolResponse(success=True, data=user.model_dump())
            logger.info(f"User lookup successful: {user_id}")
        else:
            response = ToolResponse(
                success=False,
                error_type=result["error"],
                error_message=result["message"],
            )
            logger.warning(f"User not found: {user_id}")

        return response.model_dump_json()

    except Exception as e:
        logger.error(f"User lookup failed: {e}")
        response = ToolResponse(
            success=False, error_type="SystemError", error_message=str(e)
        )
        return response.model_dump_json()
    # [/SOLUTION]


def search_user_orders(
    user_id: Optional[str] = None, status: Optional[str] = None, limit: int = 10
) -> str:
    """
    Search for orders matching criteria.

    Args:
        user_id: Filter by user ID (optional)
        status: Filter by order status (optional)
        limit: Maximum number of results

    Returns:
        List of matching orders or error

    NOTE: This function is pre-built and demonstrates the Search tool pattern.
    Read it as a reference example alongside your lookup_user implementation.
    """
    logger.info(f"Searching orders: user_id={user_id}, status={status}")

    try:
        result = search_orders(user_id=user_id, status=status)

        if result["success"]:
            orders = [Order(**o) for o in result["data"][:limit]]
            response = ToolResponse(
                success=True,
                data={
                    "orders": [o.model_dump() for o in orders],
                    "count": len(orders),
                    "total": result["count"],
                },
            )
            logger.info(f"Found {len(orders)} orders")
        else:
            response = ToolResponse(
                success=False, error_type="SearchError", error_message="Search failed"
            )

        return response.model_dump_json()

    except Exception as e:
        logger.error(f"Search error: {e}")
        response = ToolResponse(
            success=False, error_type="SystemError", error_message=str(e)
        )
        return response.model_dump_json()
