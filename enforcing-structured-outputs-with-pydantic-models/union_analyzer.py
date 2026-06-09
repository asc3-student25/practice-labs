import os
from typing import Union
from pydantic_ai import Agent
from dotenv import load_dotenv
from models import ProductReviewAnalysis, ServiceAnalysis

load_dotenv()

# Verify API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. "
        "Make sure .env file exists in the same directory as this script."
    )

# Get model from environment variable
model = os.getenv("AI_MODEL", "openai:gpt-5.4-mini")
print(f"Using model: {model}")

# Agent supporting multiple output types
agent = Agent(
    model,
    output_type=Union[ProductReviewAnalysis, ServiceAnalysis],
    system_prompt="""Analyze customer feedback.
    - For product reviews, use ProductReviewAnalysis format
    - For service reviews, use ServiceAnalysis format
    Choose the appropriate format based on the review content.""",
)

if __name__ == "__main__":
    product_review = "This blender is powerful and easy to clean. Great value for the price."
    service_review = "The staff was friendly and quick, and the check-in process was smooth."

    product_result = agent.run_sync(product_review)
    service_result = agent.run_sync(service_review)

    print(f"Product output type: {type(product_result.output).__name__}")
    print(f"Service output type: {type(service_result.output).__name__}")

    print(
        f"Product shared fields -> rating: {product_result.output.rating}, "
        f"sentiment: {product_result.output.sentiment}"
    )
    print(
        f"Service shared fields -> rating: {service_result.output.rating}, "
        f"sentiment: {service_result.output.sentiment}"
    )

    if isinstance(service_result.output, ServiceAnalysis):
        print(
            f"Service-only fields -> staff_rating: {service_result.output.staff_rating}, "
            f"would_return: {service_result.output.would_return}"
        )
