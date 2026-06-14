"""
Interactive Streaming Conversation Loop

Demonstrates multi-turn streaming conversations with:
- Message history persistence across turns
- Real-time streaming display
- Interactive commands (quit, history, clear)
- Conversation context management

Run:
    python interactive_loop.py
"""

import os
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse
from dotenv import load_dotenv
import asyncio
from datetime import datetime

# Load environment variables
load_dotenv()

# Create creative writing assistant
agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    system_prompt="""You are a creative writing assistant.
    Help develop story elements through collaborative conversation.
    Remember previous context and build upon it naturally.
    Be encouraging and offer creative suggestions.""",
)


async def interactive_session():
    """
    Run interactive streaming conversation.

    Features:
    - Multi-turn conversations with history
    - Real-time streaming responses
    - Special commands: quit, history, clear, save
    - Automatic history management
    """
    print("=" * 60)
    print("  Creative Writing Assistant - Interactive Mode")
    print("=" * 60)
    print("\nCommands:")
    print("  quit    - Exit the session")
    print("  history - Show conversation history")
    print("  clear   - Clear conversation history")
    print("  save    - Save conversation to file")
    print()

    # Track conversation history
    history: list[ModelMessage] = []
    session_start = datetime.now()
    turn_count = 0

    while True:
        # Get user input
        try:
            user_input = input("\n\033[1;34mYou: \033[0m").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! Happy writing!")
            break

        # YOUR CODE HERE
        # [SOLUTION]
        # Handle special commands
        if user_input.lower() == "quit":
            print("\n\033[1;32mGoodbye! Happy writing!\033[0m")
            break

        if user_input.lower() == "history":
            show_history(history)
            continue

        if user_input.lower() == "clear":
            history = []
            turn_count = 0
            print("\n\033[1;33m[History cleared]\033[0m")
            continue

        if user_input.lower() == "save":
            save_conversation(history, session_start)
            continue
        # [/SOLUTION]

        if not user_input:
            continue

        # YOUR CODE HERE
        # [SOLUTION]
        # Increment turn counter
        turn_count += 1

        # Stream response with history
        print("\n\033[1;32mAssistant: \033[0m", end="", flush=True)

        try:
            async with agent.run_stream(
                user_input, message_history=history
            ) as response:
                # Stream chunks as they arrive
                async for chunk in response.stream_text(delta=True):
                    print(chunk, end="", flush=True)

            print()  # Newline after response

            # Update history with all messages from this turn
            history = response.all_messages()

        except Exception as e:
            print(f"\n\n\033[1;31m[Error: {e}]\033[0m")
            print("Please try again or type 'quit' to exit.")
        # [/SOLUTION]


def show_history(history: list[ModelMessage]):
    """Display conversation history with formatting."""
    print(f"\n{'='*60}")
    print(f"  Conversation History ({len(history)} messages)")
    print(f"{'='*60}\n")

    if not history:
        print("  (No messages yet)")
        print()
        return

    for i, msg in enumerate(history, 1):
        # Determine message type and format accordingly
        if isinstance(msg, ModelRequest):
            role = "USER"
            color = "\033[1;34m"  # Blue

            # Extract content from parts
            if hasattr(msg, "parts") and msg.parts:
                content = ""
                for part in msg.parts:
                    if hasattr(part, "content"):
                        content += str(part.content)
                    elif isinstance(part, str):
                        content += part
            else:
                content = str(msg)

        elif isinstance(msg, ModelResponse):
            role = "ASSISTANT"
            color = "\033[1;32m"  # Green

            # Extract content from parts
            if hasattr(msg, "parts") and msg.parts:
                content = ""
                for part in msg.parts:
                    if hasattr(part, "content"):
                        content += str(part.content)
                    elif isinstance(part, str):
                        content += part
            else:
                content = str(msg)
        else:
            role = "SYSTEM"
            color = "\033[1;33m"  # Yellow
            content = str(msg)

        # Truncate long messages
        max_length = 100
        if len(content) > max_length:
            content = content[:max_length] + "..."

        print(f"{color}[{i}] {role}\033[0m: {content}")

    print()


def save_conversation(history: list[ModelMessage], session_start: datetime):
    """Save conversation to a file."""
    # YOUR CODE HERE
    # [SOLUTION]
    if not history:
        print("\n\033[1;33m[No conversation to save]\033[0m")
        return

    # Generate filename
    timestamp = session_start.strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.txt"

    try:
        with open(filename, "w") as f:
            f.write("=" * 60 + "\n")
            f.write(
                f"Creative Writing Session - {session_start.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write("=" * 60 + "\n\n")

            for msg in history:
                if isinstance(msg, ModelRequest):
                    role = "USER"
                    # Extract content
                    if hasattr(msg, "parts") and msg.parts:
                        content = ""
                        for part in msg.parts:
                            if hasattr(part, "content"):
                                content += str(part.content)
                    else:
                        content = str(msg)

                elif isinstance(msg, ModelResponse):
                    role = "ASSISTANT"
                    if hasattr(msg, "parts") and msg.parts:
                        content = ""
                        for part in msg.parts:
                            if hasattr(part, "content"):
                                content += str(part.content)
                    else:
                        content = str(msg)
                else:
                    role = "SYSTEM"
                    content = str(msg)

                f.write(f"{role}:\n{content}\n\n")
                f.write("-" * 60 + "\n\n")

        print(f"\n\033[1;32m[Conversation saved to {filename}]\033[0m")

    except Exception as e:
        print(f"\n\033[1;31m[Error saving: {e}]\033[0m")
    # [/SOLUTION]


async def guided_story_development():
    """
    Guided multi-turn story development session.

    Demonstrates structured conversation flow with streaming.
    """
    print("=" * 60)
    print("  Guided Story Development")
    print("=" * 60)
    print("\nLet's develop a story together!\n")

    # YOUR CODE HERE
    # [SOLUTION]
    history: list[ModelMessage] = []

    # Step 1: Genre
    print("\033[1;34mWhat genre would you like to write?\033[0m")
    genre = input("> ").strip()

    print("\n\033[1;32mAssistant: \033[0m", end="", flush=True)
    async with agent.run_stream(
        f"Suggest 3 compelling story concepts for a {genre} story",
        message_history=history,
    ) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)
    print()
    history = response.all_messages()

    # Step 2: Concept selection
    print("\n\033[1;34mWhich concept interests you, or describe your own:\033[0m")
    concept = input("> ").strip()

    print("\n\033[1;32mAssistant: \033[0m", end="", flush=True)
    async with agent.run_stream(
        f"Great choice! Let's develop '{concept}'. Suggest main characters.",
        message_history=history,
    ) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)
    print()
    history = response.all_messages()

    # Step 3: Characters
    print("\n\033[1;34mWho would you like as the protagonist?\033[0m")
    protagonist = input("> ").strip()

    print("\n\033[1;32mAssistant: \033[0m", end="", flush=True)
    async with agent.run_stream(
        f"Perfect! Now let's create a detailed profile for {protagonist}",
        message_history=history,
    ) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)
    print()
    history = response.all_messages()

    # Step 4: Plot
    print("\n\033[1;34mWhat's the main conflict or challenge?\033[0m")
    conflict = input("> ").strip()

    print("\n\033[1;32mAssistant: \033[0m", end="", flush=True)
    async with agent.run_stream(
        f"Excellent! Create a story outline with {protagonist} facing {conflict}",
        message_history=history,
    ) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)
    print()

    print("\n\033[1;32m✓ Story framework complete!\033[0m")
    print(f"Total conversation turns: {len(response.all_messages())}")
    # [/SOLUTION]


async def main():
    """Main entry point with mode selection."""
    print("\n\033[1;35mSelect mode:\033[0m")
    print("  1 - Interactive conversation (free-form)")
    print("  2 - Guided story development (structured)")
    print()

    choice = input("Choice (1 or 2): ").strip()

    if choice == "2":
        await guided_story_development()
    else:
        await interactive_session()


if __name__ == "__main__":
    asyncio.run(main())
