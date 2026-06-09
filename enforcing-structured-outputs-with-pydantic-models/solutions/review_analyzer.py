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
    # [SOLUTION]
    review = """
    This laptop is amazing! The battery lasts all day, the screen is 
    gorgeous, and it's super fast. Setup was a breeze. My only complaint 
    is that it's a bit heavy to carry around. Overall, highly recommend!
    """

    result = agent.run_sync(f"Analyze:\n{review}")

    print(f"Rating: {result.output.rating}/5")
    print(f"Sentiment: {result.output.sentiment}")
    print(f"Summary: {result.output.summary}")
    print(f"\nPros:")
    for pro in result.output.pros.items:
        print(f"  + {pro}")
    print(f"\nCons:")
    for con in result.output.cons.items:
        print(f"  - {con}")
    print(f"\nRecommended: {result.output.recommended}")
    # [/SOLUTION]
