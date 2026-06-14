"""
Challenge 2: Parallel Streaming from Multiple Agents

Coordinate streaming from multiple specialist agents simultaneously:
- Multiple agents with different expertise
- Parallel streaming execution
- Coordinated output display
- Result aggregation

Features:
- Stream from plot, character, and  setting agents simultaneously
- Display interleaved output organized by agent
- Collect all results for complete story framework
- Performance comparison vs sequential

Run:
    python challenge2_parallel.py
"""

import os
import asyncio
from typing import Dict, List, Any
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


# Specialist agents

plot_agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    system_prompt="""You are a plot development specialist.
    Create compelling story outlines with strong narrative arcs.
    Focus on conflict, tension, and satisfying resolutions.""",
)

character_agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    system_prompt="""You are a character development specialist.
    Create rich, multi-dimensional characters with depth.
    Focus on motivations, flaws, and growth arcs.""",
)

setting_agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    system_prompt="""You are a setting and world-building specialist.
    Create immersive, detailed environments.
    Focus on atmosphere, sensory details, and cultural context.""",
)

theme_agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    system_prompt="""You are a theme and symbolism specialist.
    Identify and develop meaningful themes and motifs.
    Focus on deeper meanings and emotional resonance.""",
)


class ParallelStreamCoordinator:
    """
    Coordinates parallel streaming from multiple agents.

    Features:
    - Simultaneous streaming from multiple agents
    - Organized output display
    - Performance tracking
    - Result aggregation
    """

    def __init__(self):
        """Initialize coordinator."""
        self.results: Dict[str, str] = {}
        self.start_times: Dict[str, float] = {}
        self.end_times: Dict[str, float] = {}

    async def stream_section(
        self, agent: Agent, title: str, prompt: str, color_code: str = ""
    ) -> str:
        """
        Stream one section from an agent.

        Args:
            agent: Agent to use
            title: Section title for display
            prompt: Prompt for agent
            color_code: ANSI color code for output

        Returns:
            Complete streamed text
        """
        header = f"─── {title.upper()} ───"
        if color_code:
            print(f"\n{color_code}{header}\033[0m\n")
        else:
            print(f"\n{header}\n")

        self.start_times[title] = asyncio.get_event_loop().time()

        chunks: List[str] = []
        async with agent.run_stream(prompt) as response:
            async for chunk in response.stream_text(delta=True):
                print(chunk, end="", flush=True)
                chunks.append(chunk)

        print()
        full_text = "".join(chunks)
        self.end_times[title] = asyncio.get_event_loop().time()
        self.results[title] = full_text
        return full_text

    async def parallel_streaming(
        self, concept: str, show_performance: bool = True
    ) -> Dict[str, str]:
        """
        Stream from multiple agents in parallel.

        Args:
            concept: Story concept to develop
            show_performance: Show performance statistics

        Returns:
            Dictionary of section results
        """
        print("=" * 60)
        print(f"  Parallel Streaming: {concept}")
        print("=" * 60)

        plot_coro = self.stream_section(
            plot_agent,
            "plot",
            f"Create a plot outline for: {concept}",
            "\033[1;34m",
        )
        characters_coro = self.stream_section(
            character_agent,
            "characters",
            f"Describe main characters for: {concept}",
            "\033[1;32m",
        )
        setting_coro = self.stream_section(
            setting_agent,
            "setting",
            f"Describe the setting for: {concept}",
            "\033[1;33m",
        )
        themes_coro = self.stream_section(
            theme_agent,
            "themes",
            f"Identify themes for: {concept}",
            "\033[1;36m",
        )

        plot_text, characters_text, setting_text, themes_text = await asyncio.gather(
            plot_coro,
            characters_coro,
            setting_coro,
            themes_coro,
        )

        if show_performance:
            self._show_performance_stats()

        return {
            "plot": plot_text,
            "characters": characters_text,
            "setting": setting_text,
            "themes": themes_text,
        }

    def _show_performance_stats(self):
        """Display performance statistics."""
        print("\n" + "=" * 60)
        print("  Performance Statistics")
        print("=" * 60 + "\n")

        for title in self.start_times.keys():
            duration = self.end_times[title] - self.start_times[title]
            char_count = len(self.results[title])
            chars_per_sec = char_count / duration if duration > 0 else 0

            print(f"{title}:")
            print(f"  Duration: {duration:.2f}s")
            print(f"  Characters: {char_count:,}")
            print(f"  Speed: {chars_per_sec:.1f} chars/sec")
            print()

        # Overall stats
        if self.start_times:
            earliest_start = min(self.start_times.values())
            latest_end = max(self.end_times.values())
            total_parallel_time = latest_end - earliest_start

            total_chars = sum(len(text) for text in self.results.values())

            print(f"Overall:")
            print(f"  Total time (parallel): {total_parallel_time:.2f}s")
            print(f"  Total characters: {total_chars:,}")
            print(
                f"  Effective throughput: {total_chars/total_parallel_time:.1f} chars/sec"
            )
            print("=" * 60 + "\n")


async def sequential_streaming(concept: str) -> Dict[str, str]:
    """
    Stream from agents sequentially for comparison.

    Args:
        concept: Story concept

    Returns:
        Dictionary of results
    """
    print("=" * 60)
    print(f"  Sequential Streaming: {concept}")
    print("=" * 60)

    start_time = asyncio.get_event_loop().time()
    results = {}

    # Plot
    print("\n\033[1;34m─── PLOT ───\033[0m\n")
    async with plot_agent.run_stream(
        f"Create a plot outline for: {concept}"
    ) as response:
        chunks = []
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)
            chunks.append(chunk)
        results["plot"] = "".join(chunks)
    print()

    # Characters
    print("\n\033[1;32m─── CHARACTERS ───\033[0m\n")
    async with character_agent.run_stream(
        f"Describe main characters for: {concept}"
    ) as response:
        chunks = []
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)
            chunks.append(chunk)
        results["characters"] = "".join(chunks)
    print()

    # Setting
    print("\n\033[1;33m─── SETTING ───\033[0m\n")
    async with setting_agent.run_stream(
        f"Describe the setting for: {concept}"
    ) as response:
        chunks = []
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)
            chunks.append(chunk)
        results["setting"] = "".join(chunks)
    print()

    # Themes
    print("\n\033[1;36m─── THEMES ───\033[0m\n")
    async with theme_agent.run_stream(f"Identify themes for: {concept}") as response:
        chunks = []
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)
            chunks.append(chunk)
        results["themes"] = "".join(chunks)
    print()

    end_time = asyncio.get_event_loop().time()
    duration = end_time - start_time

    total_chars = sum(len(text) for text in results.values())

    print("\n" + "=" * 60)
    print("  Sequential Performance")
    print("=" * 60)
    print(f"Total time: {duration:.2f}s")
    print(f"Total characters: {total_chars:,}")
    print(f"Throughput: {total_chars/duration:.1f} chars/sec")
    print("=" * 60 + "\n")

    return results


async def compare_parallel_vs_sequential():
    """
    Compare parallel vs sequential streaming performance.

    Demonstrates the speed advantage of parallel execution.
    """
    concept = "A lighthouse keeper discovers messages from the future"

    coordinator = ParallelStreamCoordinator()

    parallel_start = datetime.now()
    await coordinator.parallel_streaming(concept)
    parallel_duration = (datetime.now() - parallel_start).total_seconds()

    sequential_start = datetime.now()
    await sequential_streaming(concept)
    sequential_duration = (datetime.now() - sequential_start).total_seconds()

    print("\n" + "=" * 60)
    print("  Parallel vs Sequential")
    print("=" * 60)
    print(f"Parallel:   {parallel_duration:.2f}s")
    print(f"Sequential: {sequential_duration:.2f}s")

    if parallel_duration < sequential_duration:
        factor = sequential_duration / parallel_duration if parallel_duration > 0 else float("inf")
        print(f"Result: Parallel was faster by {factor:.2f}x")
    elif sequential_duration < parallel_duration:
        factor = parallel_duration / sequential_duration if sequential_duration > 0 else float("inf")
        print(f"Result: Sequential was faster by {factor:.2f}x")
    else:
        print("Result: Same duration")

    print("=" * 60 + "\n")


class StructuredParallelStreaming:
    """
    Advanced parallel streaming with structured outputs.

    Combines parallel execution with Pydantic models.
    """

    class StoryFramework(BaseModel):
        """Complete story framework."""

        plot: str
        characters: str
        setting: str
        themes: str
        concept: str
        generated_at: datetime

        def save_to_file(self, filename: str = "story_framework.txt"):
            """Save framework to file."""
            with open(filename, "w") as f:
                f.write("=" * 60 + "\n")
                f.write(f"Story Framework\n")
                f.write(f"Generated: {self.generated_at}\n")
                f.write("=" * 60 + "\n\n")

                f.write(f"CONCEPT:\n{self.concept}\n\n")
                f.write(f"PLOT:\n{self.plot}\n\n")
                f.write(f"CHARACTERS:\n{self.characters}\n\n")
                f.write(f"SETTING:\n{self.setting}\n\n")
                f.write(f"THEMES:\n{self.themes}\n")

            print(f"\n\033[1;32m✓ Framework saved to {filename}\033[0m")

    async def generate_framework(self, concept: str) -> StoryFramework:
        """
        Generate complete story framework.

        Args:
            concept: Story concept

        Returns:
            StoryFramework with all elements
        """
        # YOUR CODE HERE
        coordinator = ParallelStreamCoordinator()
        results = await coordinator.parallel_streaming(concept, show_performance=False)

        return self.StoryFramework(
            plot=results.get("plot", ""),
            characters=results.get("characters", ""),
            setting=results.get("setting", ""),
            themes=results.get("themes", ""),
            concept=concept,
            generated_at=datetime.now()
        )


async def demo_basic_parallel():
    """Basic parallel streaming demo."""
    print("=" * 60)
    print("  Demo: Basic Parallel Streaming")
    print("=" * 60)

    concept = input("\nEnter a story concept: ").strip()
    if not concept:
        concept = "A mystery in Victorian London"

    coordinator = ParallelStreamCoordinator()
    results = await coordinator.parallel_streaming(concept)

    print("\n\033[1;32m✓ All agents completed!\033[0m")


async def demo_structured_parallel():
    """Structured parallel streaming demo."""
    print("=" * 60)
    print("  Demo: Structured Parallel Streaming")
    print("=" * 60)

    concept = input("\nEnter a story concept: ").strip()
    if not concept:
        concept = "A cyberpunk adventure in Neo Tokyo"

    generator = StructuredParallelStreaming()
    framework = await generator.generate_framework(concept)

    # Offer to save
    save = input("\nSave framework to file? (y/n): ").strip().lower()
    if save == "y":
        filename = input("Filename (Enter for default): ").strip()
        if not filename:
            filename = "story_framework.txt"
        framework.save_to_file(filename)


async def main():
    """Main entry point."""
    while True:
        print("\nSelect a demo:")
        print("1. Basic Parallel Streaming")
        print("2. Structured Parallel Streaming")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ").strip()
        if choice == "1":
            await demo_basic_parallel()
        elif choice == "2":
            await demo_structured_parallel()
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    asyncio.run(main())
