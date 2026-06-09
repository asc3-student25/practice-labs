import os
import asyncio
from pydantic import ValidationError
from pydantic_ai import Agent
from dotenv import load_dotenv
from models import ReviewAnalysis

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

# Agent with structured output
agent = Agent(
    model,
    output_type=ReviewAnalysis,
    system_prompt="""You are a review analysis system.
    Extract structured information from customer reviews.
    Be accurate and objective in your analysis.""",
)


async def analyze_with_retry(review: str, max_retries: int = 3):
    """Analyze review with custom retry logic."""
    for attempt in range(1, max_retries + 1):
        try:
            if attempt == 1:
                prompt = f"Analyze the following review:\n{review}"
            else:
                prompt = f"""Analyze the following review with the following constraints:
                - Rating must be an integer between 1 and 5
                - Sentiment must be one of: positive, neutral, negative
                - Summary must be concise, max 100 characters
                - Key points must include at least 3 items
                Review: {review}"""
            result = await agent.run(prompt)
            return result.output
        except ValidationError as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt == max_retries:
                raise

if __name__ == "__main__":
    # YOUR CODE HERE

    review = "This product is excellent overall, but has some minor issues."
    analysis = asyncio.run(analyze_with_retry(review))

    print(f"Rating: {analysis.rating}")
    print(f"Sentiment: {analysis.sentiment}")
    print(f"Summary: {analysis.summary}")
    print("Key Points:")
    for point in analysis.key_points:
        print(f"- {point}")
