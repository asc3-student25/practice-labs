"""
Lab Starter: Building a Basic AI Agent
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

    support_questions = [
        "What are your support hours?",
        "How do I reset my password?",
        "I'm unable to log in after updating the app. What should I do?",
        "Which plan includes team collaboration features?",
    ]

    for question in support_questions:
        result = agent.run_sync(question)
        print(f"Query: {question}")
        print(f"Response: {result.output}\n")

    result = agent.run_sync("What payment methods do you accept?")
    print(f"Query: What payment methods do you accept?")
    print(f"Response: {result.output}")

    usage = result.usage()
    total_tokens = usage.total_tokens if usage is not None else "N/A"
    print(f"Total tokens used: {total_tokens}")
