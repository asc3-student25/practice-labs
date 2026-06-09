"""
Challenge 2 Starter: Streaming Output

Implement the `stream_response()` and `main()` async functions below so the
agent's reply prints token-by-token as it's generated. Drive `main()` from
`__main__` via `asyncio.run()`.

When you're ready to compare your work to the reference implementation,
see `solutions/challenge2_solution.py`.
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
    async with agent.run_stream(query) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end='', flush=True)
        print()
        if response.usage() and response.usage().total_tokens:
            print(f"Total tokens used: {response.usage().total_tokens}")


async def main():
    """Main async execution function"""
    queries = [
        "Create a blog outline about microservices architecture",
        "Create a blog outline about serverless computing",
        "Create a blog outline about DevOps best practices"
    ]
    for query in queries:
        await stream_response(query)


if __name__ == "__main__":
    asyncio.run(main())
