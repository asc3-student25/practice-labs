from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional


class LineItem(BaseModel):
    """Individual item on invoice."""

    description: str
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    total: float


class InvoiceData(BaseModel):
    """Structured invoice information."""

    invoice_number: Optional[str] = Field(
        None, description="Invoice or reference number"
    )
    vendor_name: str = Field(..., description="Vendor or supplier name")
    invoice_date: Optional[date] = Field(None, description="Invoice date")

    line_items: list[LineItem] = Field(
        default_factory=list, description="Individual items or services"
    )

    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total_amount: float = Field(..., description="Total amount due")

    payment_terms: Optional[str] = Field(
        None, description="Payment terms (e.g., 'Net 30', 'Due on receipt')"
    )

    @field_validator("total_amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Total amount must be positive")
        if v > 1_000_000:
            raise ValueError("Total amount seems unreasonably high")
        return v


class InvoiceDataWithConfidence(BaseModel):
    """Invoice data with confidence scoring.

    Constraints mirror `InvoiceData` even though this schema is leaner —
    a non-empty vendor_name (`min_length=1`, plus a placeholder-rejection
    validator) and a positive total_amount (`gt=0`) are required, so the
    Challenge 2 fallback path is exercised when the source text doesn't
    admit a positive total or a real vendor.
    """

    invoice_number: Optional[str] = None
    vendor_name: str = Field(..., min_length=1, description="Vendor or supplier name")
    invoice_date: Optional[date] = None
    total_amount: float = Field(..., gt=0, description="Total amount due (must be positive)")

    # Confidence scores (0.0 to 1.0)
    vendor_confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence in vendor name extraction"
    )
    amount_confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence in total amount"
    )

    _PLACEHOLDER_VENDOR_NAMES = frozenset(
        {"unknown", "unspecified", "n/a", "none", "tbd", "redacted", "illegible"}
    )

    @field_validator("vendor_name")
    @classmethod
    def reject_placeholder_vendors(cls, v: str) -> str:
        """Reject obvious placeholder text the LLM may invent when no vendor is present.

        Without this guard, an LLM asked to extract a vendor from text that has
        no real vendor (see `PROBLEMATIC_INVOICE`) often returns the literal
        string "Unknown", which trivially satisfies `min_length=1` and lets bad
        data through. This validator forces those cases into the Challenge 2
        fallback path.
        """
        if v.strip().lower() in cls._PLACEHOLDER_VENDOR_NAMES:
            raise ValueError(
                f"vendor_name must be a real vendor, not the placeholder {v!r}"
            )
        return v

    def needs_review(self) -> bool:
        """Check if extraction needs human review."""
        return (
            self.vendor_confidence < 0.7
            or self.amount_confidence < 0.7
            or self.invoice_number is None
        )


class PartialInvoiceData(BaseModel):
    """Fallback schema for incomplete extractions."""

    vendor_name: Optional[str] = None
    total_amount: Optional[float] = None
    raw_text_snippet: str = Field(..., description="Relevant portion of original text")
    extraction_errors: list[str] = Field(
        default_factory=list, description="List of extraction issues"
    )
