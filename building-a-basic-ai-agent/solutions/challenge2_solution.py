"""
Challenge 2 Solution: Asynchronous Execution
Demonstrates using async/await for parallel query execution
"""

import asyncio
import os
from pydantic_ai import Agent
from dotenv import load_dotenv

load_dotenv()

# Verify API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

model = os.getenv("AI_MODEL", "openai:gpt-5.4-mini")
print(f"Using model: {model}")

agent = Agent(
    model,
    system_prompt="""You are a helpful customer support representative
    for TechCorp, a software company. You provide clear, accurate, and
    friendly assistance to customers.""",
)


async def main():
    """Execute multiple queries in parallel using asyncio"""
    # YOUR CODE HERE
    # [SOLUTION]
    print("\n" + "=" * 60)
    print("Testing Asynchronous Execution")
    print("=" * 60)

    # Define queries
    queries = [
        "What are your support hours?",
        "How do I reset my password?",
        "What payment methods do you accept?",
    ]

    # Execute all queries in parallel
    print("\nExecuting queries in parallel...")
    tasks = [agent.run(query) for query in queries]
    results = await asyncio.gather(*tasks)

    # Display results
    print("\nResults:")
    for query, result in zip(queries, results):
        print(f"\n--- Query ---")
        print(f"Q: {query}")
        print(f"A: {result.output}")
        print(f"Tokens: {result.usage().total_tokens if result.usage() else 'N/A'}")
    # [/SOLUTION]


if __name__ == "__main__":
    # YOUR CODE HERE
    # [SOLUTION]
    asyncio.run(main())
    # [/SOLUTION]
