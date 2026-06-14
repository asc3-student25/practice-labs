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

        # Normalize user_input (case-insensitive compare) and recognize four commands: quit, history, clear, save
        command = user_input.lower()

        if command == "quit":
            print("\n\nGoodbye! Happy writing!")
            break
        elif command == "history":
            show_history(history)
            continue
        elif command == "clear":
            history.clear()
            turn_count = 0
            print("\nConversation history cleared.\n")
            continue
        elif command == "save":
            save_conversation(history, session_start)
            continue

        if not user_input:
            continue

        turn_count += 1
        print("\033[1;32mAssistant: \033[0m", end="", flush=True)

        try:
            async with agent.run_stream(user_input, message_history=history) as response:
                async for chunk in response.stream_text(delta=True):
                    print(chunk, end="", flush=True)

                history = response.all_messages()

            print()
        except Exception as e:
            print(f"\n[stream error] {e}")
            continue


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
    if not history:
        print("[No conversation to save]")
        return

    filename = f"conversation_{session_start.strftime('%Y%m%d_%H%M%S')}.txt"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            for msg in history:
                if isinstance(msg, ModelRequest):
                    role = "USER"
                elif isinstance(msg, ModelResponse):
                    role = "ASSISTANT"
                else:
                    role = "SYSTEM"

                if hasattr(msg, "parts") and msg.parts:
                    content = ""
                    for part in msg.parts:
                        if hasattr(part, "content"):
                            content += str(part.content)
                        elif isinstance(part, str):
                            content += part
                else:
                    content = str(msg)

                f.write(f"{role}:\n{content}\n\n")
                f.write("-" * 60 + "\n")

        print(f"Conversation saved to {filename}")
    except OSError as e:
        print(f"Could not save conversation: {e}")


async def guided_story_development():
    """
    Guided multi-turn story development session.

    Demonstrates structured conversation flow with streaming.
    """
    print("=" * 60)
    print("  Guided Story Development")
    print("=" * 60)
    print("\nLet's develop a story together!\n")

    history: list[ModelMessage] = []

    genre = input("Choose a genre: ").strip()
    prompt_1 = (
        f"The user chose the genre: '{genre or 'unspecified'}'. "
        "Suggest 3 strong high-level story concepts for this genre."
    )
    print("\033[1;32mAssistant: \033[0m", end="", flush=True)
    async with agent.run_stream(prompt_1, message_history=history) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)
        history = response.all_messages()
    print()

    concept_choice = input("Pick one concept (or describe your own): ").strip()
    prompt_2 = (
        f"Genre: '{genre or 'unspecified'}'. "
        f"Selected concept: '{concept_choice or 'unspecified'}'. "
        "Now propose a compelling protagonist with motivations, flaws, and goals."
    )
    print("\033[1;32mAssistant: \033[0m", end="", flush=True)
    async with agent.run_stream(prompt_2, message_history=history) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)
        history = response.all_messages()
    print()

    protagonist = input("Describe the protagonist you want: ").strip()
    prompt_3 = (
        f"Genre: '{genre or 'unspecified'}'. "
        f"Concept: '{concept_choice or 'unspecified'}'. "
        f"Protagonist details: '{protagonist or 'unspecified'}'. "
        "Develop this protagonist further with a concise character arc and key supporting character ideas."
    )
    print("\033[1;32mAssistant: \033[0m", end="", flush=True)
    async with agent.run_stream(prompt_3, message_history=history) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)
        history = response.all_messages()
    print()

    main_conflict = input("What's the main conflict? ").strip()
    prompt_4 = (
        f"Genre: '{genre or 'unspecified'}'. "
        f"Concept: '{concept_choice or 'unspecified'}'. "
        f"Protagonist: '{protagonist or 'unspecified'}'. "
        f"Main conflict: '{main_conflict or 'unspecified'}'. "
        "Create a brief story framework: setup, rising action, climax, and resolution."
    )
    print("\033[1;32mAssistant: \033[0m", end="", flush=True)
    async with agent.run_stream(prompt_4, message_history=history) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)
        history = response.all_messages()
    print()

    print("\nGuided story framework complete.")


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
