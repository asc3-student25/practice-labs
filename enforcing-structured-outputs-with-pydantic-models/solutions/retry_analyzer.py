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
    # YOUR CODE HERE
    # [SOLUTION]
    for attempt in range(max_retries):
        try:
            if attempt == 0:
                prompt = f"Analyze this review:\n{review}"
            else:
                # More explicit instructions on retries
                prompt = f"""Analyze this review:\n{review}
                
                IMPORTANT:
                - Rating must be 1-5
                - Sentiment must be: positive, negative, neutral, or mixed
                - Summary must be under 200 characters
                - Provide 2-5 key points
                """

            result = await agent.run(prompt)
            return result.output

        except ValidationError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            print("Retrying with clearer instructions...")
    # [/SOLUTION]


if __name__ == "__main__":
    # YOUR CODE HERE
    # [SOLUTION]
    # Test with a simple review
    review = "This is a test review about a great product!"
    analysis = asyncio.run(analyze_with_retry(review))
    print(f"\nRating: {analysis.rating}/5")
    print(f"Sentiment: {analysis.sentiment}")
    print(f"Summary: {analysis.summary}")
    print(f"Key Points: {analysis.key_points}")
    # [/SOLUTION]
