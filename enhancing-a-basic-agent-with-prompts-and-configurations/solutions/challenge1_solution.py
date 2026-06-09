"""
Challenge 1 Solution: Dynamic Context Injection
Demonstrates adapting agent output based on runtime context
"""

import os
from pydantic import BaseModel
from pydantic_ai import Agent
from dotenv import load_dotenv

load_dotenv()

# Verify API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")


class ContentContext(BaseModel):
    """Model representing content generation context"""

    audience: str  # 'technical' or 'general'
    length: str  # 'short', 'medium', 'long'
    tone: str  # 'formal', 'casual'


def build_dynamic_prompt(ctx: ContentContext) -> str:
    """Build a system prompt based on context"""
    base = """You are a content strategist for TechWrite."""

    # Customize based on audience
    if ctx.audience == "technical":
        base += "\n\nAudience: Technical professionals. Use industry terminology and assume deep technical knowledge."
    else:
        base += "\n\nAudience: General business readers. Explain technical concepts clearly without jargon."

    # Customize based on length
    length_guidance = {
        "short": "Create concise outlines with 3 main sections.",
        "medium": "Create detailed outlines with 4-5 main sections.",
        "long": "Create comprehensive outlines with 6-7 main sections.",
    }
    base += f"\n\nLength: {length_guidance[ctx.length]}"

    # Customize based on tone
    if ctx.tone == "formal":
        base += "\n\nTone: Professional and formal. Avoid colloquialisms."
    else:
        base += "\n\nTone: Conversational and approachable. Use friendly language."

    return base


if __name__ == "__main__":
    # YOUR CODE HERE
    # [SOLUTION]
    # Get model from environment variable
    model = os.getenv("AI_MODEL", "openai:gpt-5.4-mini")
    print(f"Using model: {model}")

    print("\n" + "=" * 60)
    print("Testing Dynamic Context Injection")
    print("=" * 60)

    # Test different context configurations
    contexts = [
        ContentContext(audience="technical", length="medium", tone="casual"),
        ContentContext(audience="general", length="short", tone="formal"),
        ContentContext(audience="technical", length="long", tone="formal"),
    ]

    query = "Create a blog outline about microservices architecture"

    for i, context in enumerate(contexts, 1):
        print(f"\n--- Configuration {i} ---")
        print(f"Audience: {context.audience}")
        print(f"Length: {context.length}")
        print(f"Tone: {context.tone}")
        print()

        agent = Agent(model, system_prompt=build_dynamic_prompt(context))

        result = agent.run_sync(query)
        print(result.output)
        print(f"\nTokens: {result.usage().total_tokens if result.usage() else 'N/A'}")
    # [/SOLUTION]
