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
    # YOUR CODE HERE
    # [SOLUTION]
    # Test with different review types
    product_review = "This laptop is great! Fast, light, beautiful screen."
    service_review = "The restaurant service was excellent. Staff were attentive."

    print("Analyzing product review...")
    product_result = agent.run_sync(f"Analyze:\n{product_review}")
    # Shared fields first — present on both Union branches.
    print(f"Product analysis type: {type(product_result.output).__name__}")
    print(f"Rating: {product_result.output.rating}/5")
    print(f"Sentiment: {product_result.output.sentiment}")

    print("\nAnalyzing service review...")
    service_result = agent.run_sync(f"Analyze:\n{service_review}")
    print(f"Service analysis type: {type(service_result.output).__name__}")
    print(f"Rating: {service_result.output.rating}/5")
    print(f"Sentiment: {service_result.output.sentiment}")

    # Service-only fields — guard with isinstance so the same code is
    # safe regardless of which Union branch the agent picked.
    if isinstance(service_result.output, ServiceAnalysis):
        print(f"Staff Rating: {service_result.output.staff_rating}/5")
        print(f"Would Return: {service_result.output.would_return}")
    # [/SOLUTION]
