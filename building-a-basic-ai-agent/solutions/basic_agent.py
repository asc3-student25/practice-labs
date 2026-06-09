"""
Lab Solution: Building a Basic AI Agent
Demonstrates creating and running a basic AI agent with Pydantic AI
"""

from pydantic_ai import Agent
from dotenv import load_dotenv
import os

# Load environment variables from .env file
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

# Initialize the agent with a system prompt
agent = Agent(
    model,
    system_prompt="""You are a helpful customer support representative
    for TechCorp, a software company. You provide clear, accurate, and
    friendly assistance to customers. Always maintain a professional
    yet warm tone.""",
)

# Main execution
if __name__ == "__main__":
    # YOUR CODE HERE
    # [SOLUTION]
    # Single query test (Step 5)
    print("\n" + "=" * 60)
    print("Step 5: Single Query Test")
    print("=" * 60)
    result = agent.run_sync("What are your support hours?")
    print(f"Agent Response: {result.output}")

    # Multiple queries test (Step 6)
    print("\n" + "=" * 60)
    print("Step 6: Multiple Queries Test")
    print("=" * 60)
    queries = [
        "How do I reset my password?",
        "Tell me about your product's features",
        "I'm having trouble logging in",
    ]

    for query in queries:
        result = agent.run_sync(query)
        print(f"\nQuery: {query}")
        print(f"Response: {result.output}")

    # Examine execution metadata (Step 7)
    print("\n" + "=" * 60)
    print("Step 7: Execution Metadata")
    print("=" * 60)
    result = agent.run_sync("What payment methods do you accept?")

    print(f"Response: {result.output}")
    print(f"\nExecution Details:")
    print(f"- Total tokens: {result.usage().total_tokens if result.usage() else 'N/A'}")
    # [/SOLUTION]
