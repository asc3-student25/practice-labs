"""
Lab Solution: Enhancing a Basic Agent with Prompts and Configurations
Demonstrates advanced prompt engineering and model configuration
"""

import os
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from dotenv import load_dotenv

load_dotenv()

# Verify API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. "
        "Make sure .env file exists in the same directory as this script."
    )

# Module-level model binding — read once, reused everywhere.
MODEL = os.getenv("AI_MODEL", "openai:gpt-5.4-mini")
print(f"Using model: {MODEL}")

# Detailed system prompt
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

# Configure model with specific parameters
agent = Agent(
    MODEL,
    system_prompt=DETAILED_SYSTEM_PROMPT,
    model_settings=ModelSettings(
        temperature=0.7, max_tokens=1000  # Moderate creativity  # Control length
    ),
)


def _format_token_count(usage) -> str:
    """Format the token count for a usage object that may be None."""
    return str(usage.total_tokens) if usage is not None else "N/A"


def test_temperature(temperature: float, query: str):
    """Test different temperature settings."""
    agent = Agent(
        MODEL,
        system_prompt=DETAILED_SYSTEM_PROMPT,
        model_settings=ModelSettings(temperature=temperature),
    )
    result = agent.run_sync(query)
    usage = result.usage()  # call once, reuse
    print(f"\n{'='*60}")
    print(f"Temperature: {temperature}")
    print(f"{'='*60}")
    print(result.output)
    print(f"Tokens: {_format_token_count(usage)}")


def compare_models(query: str):
    """Compare different model tiers.

    Tier identifiers come from environment variables so the lab works
    against any provider that supports three capability levels. Override
    in `.env` to compare other providers' tiers (for example, swap to
    Anthropic by setting `AI_MODEL_FAST=anthropic:claude-haiku-4-5`,
    `AI_MODEL=anthropic:claude-sonnet-4-5`,
    `AI_MODEL_CAPABLE=anthropic:claude-opus-4-5`).
    """
    tiers = [
        (os.getenv("AI_MODEL_FAST", "openai:gpt-5.4-nano"),
         "Fast and economical for simple tasks"),
        (os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
         "Strong performance, cost-effective"),
        (os.getenv("AI_MODEL_CAPABLE", "openai:gpt-5.4"),
         "Most capable, for complex tasks"),
    ]

    for model_id, description in tiers:
        # No more `f"openai:{name}"` concatenation — model_id already
        # carries its provider prefix.
        agent = Agent(model_id, system_prompt=DETAILED_SYSTEM_PROMPT)
        result = agent.run_sync(query)
        usage = result.usage()

        print(f"\n{'='*60}")
        print(f"Model: {model_id} ({description})")
        print(f"Tokens: {_format_token_count(usage)}")
        print(f"{'='*60}")
        print(result.output)


if __name__ == "__main__":
    # YOUR CODE HERE
    # [SOLUTION]
    # Step 6: Basic agent with model settings
    print("\n" + "=" * 60)
    print("Step 6: Agent with Model Settings")
    print("=" * 60)
    result = agent.run_sync("Write a blog outline about AI agents")
    usage = result.usage()
    print(result.output)
    print(f"\nTokens used: {_format_token_count(usage)}")

    # Step 7: Compare temperature settings
    print("\n" + "=" * 60)
    print("Step 7: Comparing Temperature Settings")
    print("=" * 60)
    query = "Write a blog outline about AI agents"
    test_temperature(0.0, query)  # Very deterministic
    test_temperature(0.7, query)  # Balanced
    test_temperature(1.5, query)  # More creative

    # Step 8: Compare model tiers
    print("\n" + "=" * 60)
    print("Step 8: Comparing Model Tiers")
    print("=" * 60)
    compare_models("Write a blog outline about AI agents")
    # [/SOLUTION]
