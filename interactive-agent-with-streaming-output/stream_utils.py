"""
Streaming Utilities

Provides utilities for enhanced streaming display:
- Progress indicators and statistics
- Streaming performance metrics
- Visual feedback during generation
- Custom stream processors

Usage:
    from stream_utils import StreamingDisplay, stream_with_stats
"""

import asyncio
import sys
from datetime import datetime
from typing import AsyncIterator, Optional, Callable
from dataclasses import dataclass


@dataclass
class StreamStats:
    """Statistics about a streaming session."""

    char_count: int
    word_count: int
    duration_seconds: float
    chars_per_second: float
    words_per_second: float
    chunk_count: int

    def __str__(self) -> str:
        return (
            f"Streamed {self.char_count} chars, {self.word_count} words "
            f"in {self.duration_seconds:.1f}s "
            f"({self.chars_per_second:.1f} chars/sec, "
            f"{self.words_per_second:.1f} words/sec)"
        )


class StreamingDisplay:
    """
    Manages streaming output with progress indicators.

    Features:
    - Character and word counting
    - Performance metrics
    - Custom visual indicators
    - Progress callbacks

    Example:
        display = StreamingDisplay()
        text = await display.display_stream(response.stream_text(delta=True))
        display.show_stats()
    """

    def __init__(
        self,
        show_dots: bool = False,
        dot_interval: int = 50,
        on_chunk: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize streaming display.

        Args:
            show_dots: Show dots as progress indicators
            dot_interval: Characters between dots
            on_chunk: Callback function for each chunk
        """
        self.char_count = 0
        self.word_count = 0
        self.chunk_count = 0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.show_dots = show_dots
        self.dot_interval = dot_interval
        self.on_chunk = on_chunk
        self._chars_since_dot = 0

    async def display_stream(self, stream: AsyncIterator[str]) -> str:
        """
        Display stream with progress indicators.

        Args:
            stream: Async iterator of text chunks

        Returns:
            Complete streamed text
        """
        self.start_time = datetime.now()
        self.char_count = 0
        self.word_count = 0
        self.chunk_count = 0
        self._chars_since_dot = 0

        full_text = []

        async for chunk in stream:
            # Update counters
            self.char_count += len(chunk)
            self.word_count += len(chunk.split())
            self.chunk_count += 1

            # Display chunk
            print(chunk, end="", flush=True)
            full_text.append(chunk)

            # Show progress dots if enabled
            if self.show_dots:
                self._chars_since_dot += len(chunk)
                if self._chars_since_dot >= self.dot_interval:
                    print(".", end="", flush=True)
                    self._chars_since_dot = 0

            # Call custom callback
            if self.on_chunk:
                self.on_chunk(chunk)

        self.end_time = datetime.now()
        return "".join(full_text)

    def get_stats(self) -> StreamStats:
        """Get streaming statistics."""
        if not self.start_time or not self.end_time:
            raise ValueError("Stream not completed")

        duration = (self.end_time - self.start_time).total_seconds()

        # Avoid division by zero
        duration = max(duration, 0.001)

        return StreamStats(
            char_count=self.char_count,
            word_count=self.word_count,
            duration_seconds=duration,
            chars_per_second=self.char_count / duration,
            words_per_second=self.word_count / duration,
            chunk_count=self.chunk_count,
        )

    def show_stats(self, verbose: bool = False):
        """
        Show streaming statistics.

        Args:
            verbose: Show detailed statistics
        """
        stats = self.get_stats()

        if verbose:
            print(f"\n\n{'─'*60}")
            print(f"Streaming Statistics:")
            print(f"  Characters: {stats.char_count:,}")
            print(f"  Words: {stats.word_count:,}")
            print(f"  Chunks: {stats.chunk_count:,}")
            print(f"  Duration: {stats.duration_seconds:.2f}s")
            print(f"  Speed: {stats.chars_per_second:.1f} chars/sec")
            print(f"  Speed: {stats.words_per_second:.1f} words/sec")
            print(f"{'─'*60}")
        else:
            print(f"\n\n[{stats}]")


class StreamingProgressBar:
    """
    Animated progress bar for streaming.

    Shows spinning indicator while streaming is active.
    """

    def __init__(self):
        self.active = False
        self._spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._current_idx = 0

    async def show(self):
        """Show animated progress indicator."""
        self.active = True

        while self.active:
            char = self._spinner_chars[self._current_idx]
            print(f"\r{char} Generating...", end="", flush=True)
            self._current_idx = (self._current_idx + 1) % len(self._spinner_chars)
            await asyncio.sleep(0.1)

        print("\r              \r", end="", flush=True)  # Clear spinner

    def stop(self):
        """Stop progress indicator."""
        self.active = False


class StreamBuffer:
    """
    Buffer stream chunks with controlled flushing.

    Useful for reducing terminal flicker with very fast streams.
    """

    def __init__(self, flush_interval: float = 0.05):
        """
        Initialize stream buffer.

        Args:
            flush_interval: Seconds between flushes
        """
        self.buffer = []
        self.flush_interval = flush_interval
        self.last_flush = datetime.now()

    async def add_chunk(self, chunk: str):
        """
        Add chunk to buffer and flush if needed.

        Args:
            chunk: Text chunk to buffer
        """
        self.buffer.append(chunk)

        now = datetime.now()
        elapsed = (now - self.last_flush).total_seconds()

        if elapsed >= self.flush_interval:
            self.flush()

    def flush(self):
        """Flush buffer to stdout."""
        if self.buffer:
            print("".join(self.buffer), end="", flush=True)
            self.buffer = []
            self.last_flush = datetime.now()

    async def display_stream(self, stream: AsyncIterator[str]) -> str:
        """
        Display buffered stream.

        Args:
            stream: Async iterator of chunks

        Returns:
            Complete text
        """
        full_text = []

        async for chunk in stream:
            await self.add_chunk(chunk)
            full_text.append(chunk)

        # Final flush
        self.flush()

        return "".join(full_text)


# Convenience functions


async def stream_with_stats(agent, prompt, verbose: bool = False):
    """
    Stream response with automatically displayed statistics.

    Args:
        agent: Pydantic AI agent
        prompt: User prompt
        verbose: Show detailed statistics

    Returns:
        Complete RunResult

    Example:
        result = await stream_with_stats(agent, "Write a story")
    """
    display = StreamingDisplay()

    print("Assistant: ", end="", flush=True)

    async with agent.run_stream(prompt) as response:
        await display.display_stream(response.stream_text(delta=True))

    display.show_stats(verbose=verbose)
    return response


async def stream_with_progress(agent, prompt):
    """
    Stream response with animated progress indicator.

    Args:
        agent: Pydantic AI agent
        prompt: User prompt

    Returns:
        Complete RunResult

    Example:
        result = await stream_with_progress(agent, "Generate content")
    """
    progress = StreamingProgressBar()

    # Start progress indicator
    progress_task = asyncio.create_task(progress.show())

    try:
        async with agent.run_stream(prompt) as response:
            # Stop progress, start displaying content
            progress.stop()
            await progress_task

            print("Assistant: ", end="", flush=True)
            async for chunk in response.stream_text(delta=True):
                print(chunk, end="", flush=True)

        print()
        return response

    except Exception as e:
        progress.stop()
        raise


async def stream_buffered(agent, prompt, flush_interval: float = 0.05):
    """
    Stream response with buffering to reduce flicker.

    Args:
        agent: Pydantic AI agent
        prompt: User prompt
        flush_interval: Seconds between buffer flushes

    Returns:
        Complete RunResult

    Example:
        result = await stream_buffered(agent, "Write content", flush_interval=0.1)
    """
    buffer = StreamBuffer(flush_interval=flush_interval)

    print("Assistant: ", end="", flush=True)

    async with agent.run_stream(prompt) as response:
        await buffer.display_stream(response.stream_text(delta=True))

    print()
    return response


class StreamLogger:
    """
    Log streaming activity for debugging.

    Useful for monitoring streaming behavior without
    affecting the user-facing display.
    """

    def __init__(self, log_file: str = "stream.log"):
        """
        Initialize stream logger.

        Args:
            log_file: Path to log file
        """
        self.log_file = log_file
        self.chunk_times = []

    def log_chunk(self, chunk: str):
        """Log individual chunk with timestamp."""
        timestamp = datetime.now()

        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp.isoformat()}] {len(chunk)} chars: {repr(chunk)}\n")

        self.chunk_times.append(timestamp)

    def log_stats(self):
        """Log streaming statistics."""
        if len(self.chunk_times) < 2:
            return

        intervals = [
            (self.chunk_times[i + 1] - self.chunk_times[i]).total_seconds()
            for i in range(len(self.chunk_times) - 1)
        ]

        with open(self.log_file, "a") as f:
            f.write(f"\nStreaming Statistics:\n")
            f.write(f"  Total chunks: {len(self.chunk_times)}\n")
            f.write(f"  Avg interval: {sum(intervals)/len(intervals):.3f}s\n")
            f.write(f"  Min interval: {min(intervals):.3f}s\n")
            f.write(f"  Max interval: {max(intervals):.3f}s\n")
            f.write(f"\n{'='*60}\n\n")


# Example usage
async def demo():
    """Demonstrate streaming utilities."""
    from pydantic_ai import Agent
    import os
    from dotenv import load_dotenv

    load_dotenv()

    agent = Agent(
        os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
        system_prompt="You are a helpful assistant.",
    )

    print("=== Demo 1: Basic stats ===\n")
    await stream_with_stats(agent, "Write a short poem", verbose=True)

    print("\n\n=== Demo 2: Progress indicator ===\n")
    await stream_with_progress(agent, "Describe a sunset")

    print("\n\n=== Demo 3: Buffered streaming ===\n")
    await stream_buffered(agent, "Write a short story opening", flush_interval=0.1)


if __name__ == "__main__":
    asyncio.run(demo())
