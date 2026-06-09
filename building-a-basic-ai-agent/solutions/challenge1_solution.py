"""
Challenge 1 Solution: Dynamic System Prompts
Demonstrates using dependency injection to customize agent behavior at runtime.

Key pattern: Pydantic AI does not f-string-interpolate values into a static
system_prompt= string. To build a system prompt from runtime dependencies,
register a function with @agent.system_prompt and read the values from
ctx.deps. Pydantic AI calls that function on every run, with the deps=
argument bound into ctx.deps.
"""

import os
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv

load_dotenv()

# Verify API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")


class Department(BaseModel):
    """Model representing a department with specific expertise"""

    name: str
    expertise: str


model = os.getenv("AI_MODEL", "openai:gpt-5.4-mini")
print(f"Using model: {model}")

# Create the agent and declare the dependency type. The system prompt is
# registered as a function below, so the agent can read the current
# Department off ctx.deps each time it runs.
agent = Agent(
    model,
    deps_type=Department,
)


@agent.system_prompt
def department_system_prompt(ctx: RunContext[Department]) -> str:
    """Build the system prompt from the Department passed via deps=."""
    return (
        f"You are a representative for the {ctx.deps.name} department. "
        f"Your expertise is in {ctx.deps.expertise}. Provide helpful, "
        f"accurate information relevant to your role."
    )


if __name__ == "__main__":
    # YOUR CODE HERE
    # [SOLUTION]
    # Create different department contexts
    support_dept = Department(
        name="Customer Support", expertise="troubleshooting and technical assistance"
    )

    sales_dept = Department(name="Sales", expertise="product information and pricing")

    billing_dept = Department(
        name="Billing", expertise="invoices, payments, and account management"
    )

    # Test query
    query = "Can you help me?"

    # Run with different contexts
    print("\n" + "=" * 60)
    print("Testing Dynamic System Prompts")
    print("=" * 60)

    print(f"\nQuery: {query}")

    print(f"\n--- {support_dept.name} Response ---")
    result = agent.run_sync(query, deps=support_dept)
    print(result.output)

    print(f"\n--- {sales_dept.name} Response ---")
    result = agent.run_sync(query, deps=sales_dept)
    print(result.output)

    print(f"\n--- {billing_dept.name} Response ---")
    result = agent.run_sync(query, deps=billing_dept)
    print(result.output)
    # [/SOLUTION]
