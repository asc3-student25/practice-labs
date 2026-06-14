"""
Challenge 1: Interruptible Streaming

Implement streaming with user interrupt capability:
- Non-blocking keyboard input detection
- Graceful stream interruption
- Feedback collection and correction
- Restart with refinement

Features:
- Press 's' during streaming to stop
- Provide correction/feedback
- Agent restarts with your guidance
- Maintains conversation context

Run:
    python challenge1_interruptible.py

Note: Requires terminal with non-blocking input support.
For Windows, use alternative approach with threading.
"""

import os
import sys
import asyncio
import select
from typing import Optional, List
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage
from dotenv import load_dotenv

load_dotenv()


class StreamInterrupt(Exception):
    """Raised when user interrupts stream."""

    pass


class InterruptibleStreamer:
    """
    Manages interruptible streaming.

    Allows users to stop generation mid-stream
    and provide corrections or refinements.
    """

    def __init__(self, agent: Agent):
        """
        Initialize interruptible streamer.

        Args:
            agent: Pydantic AI agent for streaming
        """
        self.agent = agent
        self.is_unix = sys.platform != "win32"

    def _check_interrupt(self) -> Optional[str]:
        """
        Check for keyboard interrupt (non-blocking).

        Returns:
            Character pressed or None

        Platform-specific implementation:
        - Unix/Mac: Use select for non-blocking input
        - Windows: Would need threading approach (not shown)
        """
        if not self.is_unix:
            # Windows needs different approach
            # For now, return None (no interrupt support on Windows in this demo)
            return None

        # Unix/Mac: Use select
        if select.select([sys.stdin], [], [], 0)[0]:
            char = sys.stdin.read(1)
            return char

        return None

    async def stream_with_interrupt(
        self,
        prompt: str,
        message_history: Optional[List[ModelMessage]] = None,
        interrupt_key: str = "s",
    ) -> tuple[str, List[ModelMessage], bool]:
        """
        Stream with interrupt capability.

        Args:
            prompt: User prompt
            message_history: Conversation history
            interrupt_key: Key to press for interrupt (default 's')

        Returns:
            Tuple of (response_text, updated_history, was_interrupted)
        """
        history = message_history or []
        chunks: List[str] = []

        print(f"\nPress '{interrupt_key}' to stop streaming.\n")

        try:
            async with self.agent.run_stream(prompt, message_history=history) as response:
                async for chunk in response.stream_text(delta=True):
                    key = self._check_interrupt()
                    if key == interrupt_key:
                        raise StreamInterrupt()

                    chunks.append(chunk)
                    print(chunk, end="", flush=True)

                updated_history = response.all_messages()
                return "".join(chunks), updated_history, False
        except StreamInterrupt:
            return "".join(chunks), history, True

    async def interactive_with_corrections(
        self, initial_prompt: str, max_retries: int = 3
    ) -> str:
        """
        Interactive streaming with correction loop.

        Allows user to interrupt and provide feedback,
        then restarts with refinement.

        Args:
            initial_prompt: Starting prompt
            max_retries: Maximum correction attempts

        Returns:
            Final accepted response
        """
        current_prompt = initial_prompt
        history: List[ModelMessage] = []
        last_response = ""

        for _ in range(max_retries + 1):
            response, history, interrupted = await self.stream_with_interrupt(
                current_prompt, message_history=history
            )
            last_response = response

            if not interrupted:
                return response

            correction = input("\n\nProvide correction (or press Enter to accept partial): ").strip()
            if not correction:
                return response

            current_prompt = (
                f"{initial_prompt}\n\n"
                f"User correction/refinement: {correction}"
            )

        return last_response


async def demo_basic_interrupt():
    """Demonstrate basic interrupt functionality."""
    print("=" * 60)
    print("  Demo: Basic Interrupt")
    print("=" * 60)
    print("\nThis will generate a long response.")
    print("Press 's' at any time to stop it.\n")

    agent = Agent(
        os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
        system_prompt="You are a creative writer. Write detailed content.",
    )

    streamer = InterruptibleStreamer(agent)

    response, _, interrupted = await streamer.stream_with_interrupt(
        "Write a detailed description of a fantasy castle, "
        "including its towers, walls, gates, and surrounding landscape. "
        "Make it at least 200 words."
    )

    if interrupted:
        print(
            f"\n\n\033[1;33mYou stopped the generation after {len(response)} characters.\033[0m"
        )
    else:
        print(f"\n\n\033[1;32mGeneration completed: {len(response)} characters.\033[0m")


async def demo_interactive_corrections():
    """Demonstrate interactive corrections."""
    print("\n" + "=" * 60)
    print("  Demo: Interactive Corrections")
    print("=" * 60)
    print("\nThe agent will generate content.")
    print("If you don't like the direction, press 's' to stop")
    print("and provide feedback for refinement.\n")

    agent = Agent(
        os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
        system_prompt="You are a creative writing assistant.",
    )

    streamer = InterruptibleStreamer(agent)

    input("Press Enter to start...")

    final_response = await streamer.interactive_with_corrections(
        "Describe a mysterious character for a detective story", max_retries=3
    )

    print("\n\n" + "=" * 60)
    print("  Final Response")
    print("=" * 60)
    print(final_response)
    print("=" * 60 + "\n")


async def demo_conversation_with_interrupts():
    """Demonstrate multi-turn conversation with interrupts."""
    print("\n" + "=" * 60)
    print("  Demo: Conversation with Interrupts")
    print("=" * 60)
    print("\nHave a conversation where you can interrupt responses.\n")

    agent = Agent(
        os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
        system_prompt="You are a helpful creative writing assistant.",
    )

    streamer = InterruptibleStreamer(agent)
    history = []

    print("Type 'quit' to exit, or enter questions.\n")

    while True:
        user_input = input("\n\033[1;34mYou: \033[0m").strip()

        if user_input.lower() == "quit":
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        response, history, interrupted = await streamer.stream_with_interrupt(
            user_input, message_history=history
        )

        if interrupted:
            # Get refinement
            feedback = input("\nWhat would you like instead? ").strip()
            if feedback:
                # Try again with feedback
                refined_prompt = f"{user_input}. {feedback}"
                response, history, _ = await streamer.stream_with_interrupt(
                    refined_prompt, message_history=history
                )


class ThreadedInterruptibleStreamer:
    """
    Alternative implementation using threading for Windows compatibility.

    This version works on all platforms by using a separate thread
    for keyboard input monitoring.
    """

    def __init__(self, agent: Agent):
        """
        Initialize threaded interruptible streamer.

        Args:
            agent: Pydantic AI agent
        """
        self.agent = agent
        self.interrupted = False
        self.input_thread = None

    def _input_thread_func(self):
        """Thread function to wait for input."""
        input()  # Wait for any key
        self.interrupted = True

    async def stream_with_interrupt_threaded(
        self, prompt: str, message_history: Optional[List[ModelMessage]] = None
    ) -> tuple[str, List[ModelMessage], bool]:
        """
        Stream with interrupt using threading (cross-platform).

        Args:
            prompt: User prompt
            message_history: Conversation history

        Returns:
            Tuple of (response, history, was_interrupted)
        """
        import threading
        history = message_history or []
        chunks: List[str] = []

        self.interrupted = False
        self.input_thread = threading.Thread(target=self._input_thread_func, daemon=True)
        self.input_thread.start()

        print("\nPress Enter to stop streaming.\n")

        async with self.agent.run_stream(prompt, message_history=history) as response:
            async for chunk in response.stream_text(delta=True):
                if self.interrupted:
                    return "".join(chunks), history, True

                chunks.append(chunk)
                print(chunk, end="", flush=True)
                await asyncio.sleep(0.01)

            updated_history = response.all_messages()
            return "".join(chunks), updated_history, False


async def main():
    """Main entry point."""
    await demo_basic_interrupt()
    await demo_interactive_corrections()
    await demo_conversation_with_interrupts()


if __name__ == "__main__":
    asyncio.run(main())
