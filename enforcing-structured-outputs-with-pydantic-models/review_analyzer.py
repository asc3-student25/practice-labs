import os
from pydantic_ai import Agent
from dotenv import load_dotenv
from models import DetailedReviewAnalysis

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

# Agent with nested structured output
agent = Agent(
    model,
    output_type=DetailedReviewAnalysis,
    system_prompt="""Analyze reviews and extract:
    - Overall rating and sentiment
    - Specific pros and cons
    - Whether product is recommended
    Be thorough and objective.""",
)

if __name__ == "__main__":
    # YOUR CODE HERE

    review = """
    I recently purchased this product and overall, I'm quite satisfied. The build quality is excellent and it performs well under heavy use. However, I did encounter some minor issues with the software interface, which can be a bit confusing at times. Customer support was helpful in resolving my concerns. I would recommend this product to others, but with a note about the software quirks.
    """
    result = agent.run_sync(f"Analyze the following review:\n{review}")
    
    print(result.output)

    print("\nPros:")
    for item in result.output.pros.items:
        print(f"- {item}")

    print("\nCons:")
    for item in result.output.cons.items:
        print(f"- {item}")

    print(f"\nRating: {result.output.rating}/5")
    print(f"Sentiment: {result.output.sentiment}")
    print(f"Summary: {result.output.summary}")
    print(f"Recommended: {result.output.recommended}")
