"""
Basic Streaming Agent

Demonstrates fundamental streaming patterns with Pydantic AI:
- Token-by-token streaming with run_stream()
- Async iteration of response chunks
- Real-time display of generated content
- Access to complete response after streaming

Run:
    python writer_agent.py
"""

import os
from pydantic_ai import Agent
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Create creative writing assistant agent
agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    system_prompt="""You are a creative writing assistant.
    Help authors develop characters, plots, and story ideas.
    Be detailed and imaginative in your responses.
    Use vivid descriptions and engaging language.""",
)


async def stream_response(prompt: str):
    """
    Stream a response token-by-token.

    Args:
        prompt: User's question or request

    Returns:
        Complete RunResult after streaming finishes

    The pattern:
    1. Use async context manager for run_stream()
    2. Iterate chunks with async for
    3. Print immediately with flush=True for real-time display
    4. Return complete response after streaming
    """
    print("Assistant: ", end="", flush=True)

    # Context manager automatically handles stream lifecycle
    async with agent.run_stream(prompt) as response:
        # Iterate chunks as they arrive
        async for chunk in response.stream_text(delta=True):
            # Print immediately without buffering
            print(chunk, end="", flush=True)

    print("\n")  # Newline after complete response

    # response is complete RunResult with all data
    return response


async def stream_with_metadata(prompt: str):
    """
    Stream response and display metadata.

    Demonstrates accessing response metadata after streaming completes:
    - Message history
    - Usage information
    - Model name
    """
    print(f"\n{'='*60}")
    print(f"Prompt: {prompt}")
    print(f"{'='*60}\n")

    print("Assistant: ", end="", flush=True)

    async with agent.run_stream(prompt) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)

    print("\n")

    # Access metadata
    print(f"\n{'─'*60}")
    print(f"Messages in conversation: {len(response.all_messages())}")
    print(f"New messages added: {len(response.new_messages())}")

    # Usage information (if available)
    if hasattr(response, "usage") and response.usage:
        print(f"Tokens used: {response.usage}")

    print(f"{'─'*60}\n")

    return response


async def main():
    """
    Main async entry point.

    Demonstrates different streaming scenarios:
    1. Simple character description
    2. Plot development with metadata
    3. Setting description
    """
    print("=== Creative Writing Assistant - Streaming Demo ===\n")

    # Example 1: Simple streaming
    print("Example 1: Character Description\n")
    await stream_response("Describe a mysterious character for a detective novel")

    # Example 2: Streaming with metadata
    print("\nExample 2: Plot Development (with metadata)\n")
    await stream_with_metadata("Create a compelling plot twist for a mystery story")

    # Example 3: Longer response to see streaming effect
    print("\nExample 3: Setting Description\n")
    await stream_response(
        "Describe a haunted mansion in vivid detail, including "
        "its exterior, interior rooms, and mysterious atmosphere"
    )

    print("=== Streaming Demo Complete ===")


if __name__ == "__main__":
    # Run async main function
    asyncio.run(main())


# Additional utility functions for reference


async def stream_single(prompt: str) -> str:
    """
    Stream and return just the text content.

    Useful when you only need the response text,
    not the full RunResult metadata.
    """
    chunks = []

    async with agent.run_stream(prompt) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)
            chunks.append(chunk)

    print()
    return "".join(chunks)


async def stream_silent(prompt: str) -> str:
    """
    Stream without displaying, just collect text.

    Useful for processing responses programmatically
    while still using streaming API.
    """
    chunks = []

    async with agent.run_stream(prompt) as response:
        async for chunk in response.stream_text(delta=True):
            chunks.append(chunk)

    return "".join(chunks)


async def stream_with_callback(prompt: str, callback=None):
    """
    Stream with custom callback for each chunk.

    Args:
        prompt: User's question
        callback: Optional function called for each chunk

    Example:
        await stream_with_callback(
            "Write a story",
            callback=lambda chunk: logger.debug(f"Chunk: {chunk}")
        )
    """
    async with agent.run_stream(prompt) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)

            # Call custom callback if provided
            if callback:
                callback(chunk)

    print()
    return response
