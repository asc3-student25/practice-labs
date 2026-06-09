"""
Challenge 2 Solution: Streaming Output
Demonstrates real-time token-by-token response generation
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

# Get model from environment variable
model = os.getenv("AI_MODEL", "openai:gpt-5.4-mini")
print(f"Using model: {model}")

DETAILED_SYSTEM_PROMPT = """You are an expert content strategist for TechWrite,
a B2B software marketing company. Your role is to create blog post outlines
that follow our content standards.

**Brand Voice Guidelines:**
- Professional yet approachable
- Use active voice and clear language
- Avoid jargon unless targeting technical audiences
- Include actionable insights

**Output Format:**
When creating blog outlines, follow this structure:
1. Title (compelling and SEO-friendly)
2. Introduction hook
3. 3-5 main sections with subpoints
4. Key takeaways
5. Call-to-action

**Quality Standards:**
- Each section should have 2-3 subpoints
- Focus on practical, actionable advice
- Include data or examples where relevant
"""

agent = Agent(model, system_prompt=DETAILED_SYSTEM_PROMPT)


async def stream_response(query: str):
    """Stream agent response token-by-token"""
    # YOUR CODE HERE
    # [SOLUTION]
    print(f"\nQuery: {query}")
    print("\nStreaming response:\n")
    print("-" * 60)

    async with agent.run_stream(query) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)

    print("\n" + "-" * 60)
    print(
        f"\nTotal tokens: {response.usage().total_tokens if response.usage() else 'N/A'}"
    )
    # [/SOLUTION]


async def main():
    """Main async execution function"""
    # YOUR CODE HERE
    # [SOLUTION]
    print("\n" + "=" * 60)
    print("Testing Streaming Output")
    print("=" * 60)

    # Test streaming with multiple queries
    queries = [
        "Write a blog outline about AI agents",
        "Create a blog outline about cloud security best practices",
        "Generate a blog outline about API design principles",
    ]

    for query in queries:
        await stream_response(query)
        print()
    # [/SOLUTION]


if __name__ == "__main__":
    # YOUR CODE HERE
    # [SOLUTION]
    asyncio.run(main())
    # [/SOLUTION]
