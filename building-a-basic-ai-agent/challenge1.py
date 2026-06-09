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
    departments = [
        Department(name="Customer Support", expertise="resolving product and account issues"),
        Department(name="Sales", expertise="product recommendations and pricing options"),
        Department(name="Billing", expertise="invoices, payments, and refunds"),
    ]

    # Run different queries for each department to see how responses change.
    queries = {
        "Customer Support": "Can you help me recover access to my account?",
        "Sales": "Which plan would you recommend for a small team?",
        "Billing": "I need help understanding a recent charge and refund status.",
    }

    for department in departments:
        query = queries.get(department.name, "Can you help me with my account?")
        result = agent.run_sync(query, deps=department)
        # Print department name, query, and the response so we can see how the system prompt influenced the output
        print(f"\n[{department.name}]\nQuery: {query}\nResponse: {result.output}")
