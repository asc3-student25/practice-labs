from pydantic import BaseModel, Field, field_validator


class ReviewAnalysis(BaseModel):
    """Structured analysis of a customer review."""

    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    sentiment: str = Field(..., description="Overall sentiment")
    summary: str = Field(..., max_length=200, description="Brief summary")
    key_points: list[str] = Field(
        ..., min_length=2, max_length=5, description="2-5 key points from the review"
    )

    @field_validator("sentiment")
    @classmethod
    def validate_sentiment(cls, v: str) -> str:
        valid = ["positive", "negative", "neutral", "mixed"]
        if v.lower() not in valid:
            raise ValueError(f"Sentiment must be one of: {valid}")
        return v.lower()


class Pros(BaseModel):
    """Positive aspects mentioned in review."""

    items: list[str] = Field(..., min_length=0, max_length=5)


class Cons(BaseModel):
    """Negative aspects mentioned in review."""

    items: list[str] = Field(..., min_length=0, max_length=5)


class DetailedReviewAnalysis(BaseModel):
    """Enhanced review analysis with pros/cons breakdown."""

    rating: int = Field(..., ge=1, le=5)
    sentiment: str = Field(..., description="Overall sentiment")
    summary: str = Field(..., max_length=200)
    pros: Pros
    cons: Cons
    recommended: bool

    @field_validator("sentiment")
    @classmethod
    def validate_sentiment(cls, v: str) -> str:
        # Mirrors ReviewAnalysis.validate_sentiment so the Core Lab's
        # validation-failure claim ("sentiment outside the four allowed
        # values triggers re-prompt") is true for DetailedReviewAnalysis
        # as well, not just for the Challenge 1 ReviewAnalysis schema.
        valid = ["positive", "negative", "neutral", "mixed"]
        if v.lower() not in valid:
            raise ValueError(f"Sentiment must be one of: {valid}")
        return v.lower()


class ProductReviewAnalysis(BaseModel):
    """Analysis for product reviews."""

    rating: int = Field(..., ge=1, le=5)
    sentiment: str
    key_features: list[str] = Field(..., min_length=1, max_length=5)
    recommended: bool


class ServiceAnalysis(BaseModel):
    """Analysis for service reviews."""

    rating: int = Field(..., ge=1, le=5)
    sentiment: str
    service_quality: str = Field(..., description="excellent/good/fair/poor")
    staff_rating: int = Field(..., ge=1, le=5)
    would_return: bool
