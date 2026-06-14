from pydantic import BaseModel
from typing import Optional, Any


class ToolResponse(BaseModel):
    """Standard tool response format."""

    success: bool
    data: Optional[Any] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None


class User(BaseModel):
    """User account information."""

    id: str
    name: str
    email: str
    tier: str


class Order(BaseModel):
    """Order information."""

    id: str
    user_id: str
    status: str
    total: float
