"""
Structured Streaming

Demonstrates streaming responses with structured output:
- Streaming text while building typed data
- Combining real-time display with data extraction
- Validating structured results after streaming
- Type-safe character profiles and story elements

Run:
    python structured_streaming.py
"""

import os
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from typing import List, Literal
from dotenv import load_dotenv
import asyncio
import json

# Load environment
load_dotenv()


# Structured output models


class CharacterProfile(BaseModel):
    """Structured character information."""

    name: str = Field(description="Character's full name")
    age: int = Field(description="Character's age", ge=0, le=150)
    occupation: str = Field(description="Character's job or role")
    personality_traits: List[str] = Field(
        description="Key personality traits", min_length=3, max_length=5
    )
    backstory: str = Field(description="Character's background story")
    motivation: str = Field(description="What drives the character")

    def display(self):
        """Pretty print character profile."""
        print(f"\n{'='*60}")
        print(f"  Character Profile: {self.name}")
        print(f"{'='*60}")
        print(f"Age: {self.age}")
        print(f"Occupation: {self.occupation}")
        print(f"\nPersonality:")
        for trait in self.personality_traits:
            print(f"  • {trait}")
        print(f"\nMotivation: {self.motivation}")
        print(f"\nBackstory:")
        print(f"  {self.backstory}")
        print(f"{'='*60}\n")


class PlotOutline(BaseModel):
    """Structured plot outline."""

    title: str = Field(description="Story title")
    genre: str = Field(description="Story genre")
    premise: str = Field(description="One-sentence premise")
    acts: List[str] = Field(
        description="Main acts/sections of the story", min_length=3, max_length=5
    )
    climax: str = Field(description="The story's climax")
    resolution: str = Field(description="How the story resolves")
    themes: List[str] = Field(description="Major themes explored")

    def display(self):
        """Pretty print plot outline."""
        print(f"\n{'='*60}")
        print(f"  {self.title}")
        print(f"  Genre: {self.genre}")
        print(f"{'='*60}")
        print(f"\nPremise: {self.premise}")
        print(f"\nThemes: {', '.join(self.themes)}")
        print(f"\nActs:")
        for i, act in enumerate(self.acts, 1):
            print(f"  {i}. {act}")
        print(f"\nClimax: {self.climax}")
        print(f"Resolution: {self.resolution}")
        print(f"{'='*60}\n")


class SceneSetting(BaseModel):
    """Structured scene setting description."""

    location_name: str = Field(description="Name of the location")
    time_period: str = Field(description="When the scene takes place")
    atmosphere: Literal["tense", "peaceful", "mysterious", "joyful", "ominous"] = Field(
        description="Overall mood/atmosphere"
    )
    sensory_details: dict[str, str] = Field(
        description="Sensory descriptions (sight, sound, smell, etc.)"
    )
    notable_features: List[str] = Field(
        description="Distinctive features of the setting", min_length=2
    )
    full_description: str = Field(
        description="Complete prose description of the setting"
    )

    def display(self):
        """Pretty print scene setting."""
        print(f"\n{'='*60}")
        print(f"  Setting: {self.location_name}")
        print(f"  Period: {self.time_period}")
        print(f"  Atmosphere: {self.atmosphere}")
        print(f"{'='*60}")
        print(f"\nSensory Details:")
        for sense, detail in self.sensory_details.items():
            print(f"  {sense.capitalize()}: {detail}")
        print(f"\nNotable Features:")
        for feature in self.notable_features:
            print(f"  • {feature}")
        print(f"\nDescription:")
        print(f"  {self.full_description}")
        print(f"{'='*60}\n")


# Agents with structured output

character_agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    output_type=CharacterProfile,
    system_prompt="""Create detailed character profiles for stories.
    Return structured information matching the CharacterProfile schema.
    Be creative and ensure characters are compelling and well-rounded.""",
)

plot_agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    output_type=PlotOutline,
    system_prompt="""Create compelling plot outlines for stories.
    Structure the plot with clear acts, climax, and resolution.
    Ensure the story has strong themes and narrative arc.""",
)

setting_agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    output_type=SceneSetting,
    system_prompt="""Create vivid scene settings with rich sensory details.
    Include atmosphere, time period, and distinctive features.
    Make settings come alive through detailed description.""",
)


async def stream_structured_character(description: str) -> CharacterProfile:
    """
    Stream character creation with structured output.

    Args:
        description: Character description prompt

    Returns:
        Validated CharacterProfile

    Demonstrates:
    - Streaming the generation process
    - Extracting structured data after completion
    - Type validation with Pydantic
    """
    print(f"Creating character: {description}\n")
    print("Generating: ", end="", flush=True)

    async with character_agent.run_stream(description) as response:
        # Stream text representation
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)

    print("\n\n--- Structured Output ---")

    # Access validated structured data
    character = response.output
    character.display()

    return character


async def stream_structured_plot(premise: str) -> PlotOutline:
    """
    Stream plot creation with structured output.

    Args:
        premise: Plot premise or concept

    Returns:
        Validated PlotOutline
    """
    print(f"Creating plot: {premise}\n")
    print("Generating: ", end="", flush=True)

    async with plot_agent.run_stream(premise) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)

    print("\n\n--- Structured Output ---")

    plot = response.output
    plot.display()

    return plot


async def stream_structured_setting(location: str) -> SceneSetting:
    """
    Stream setting creation with structured output.

    Args:
        location: Location description

    Returns:
        Validated SceneSetting
    """
    print(f"Creating setting: {location}\n")
    print("Generating: ", end="", flush=True)

    async with setting_agent.run_stream(location) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end="", flush=True)

    print("\n\n--- Structured Output ---")

    setting = response.output
    setting.display()

    return setting


async def create_complete_story_framework():
    """
    Create a complete story with structured elements.

    Demonstrates combining multiple structured streaming calls
    to build a comprehensive story framework.
    """
    print("=" * 60)
    print("  Complete Story Framework Generator")
    print("=" * 60)
    print("\nGenerating a complete story framework with:")
    print("  • Main character")
    print("  • Plot outline")
    print("  • Primary setting")
    print()

    # Create character
    print("\n" + "─" * 60)
    print("STEP 1: Creating protagonist")
    print("─" * 60 + "\n")

    character = await stream_structured_character(
        "A brilliant but troubled detective in Victorian London"
    )

    # Create plot
    print("\n" + "─" * 60)
    print("STEP 2: Creating plot outline")
    print("─" * 60 + "\n")

    plot = await stream_structured_plot(
        f"A mystery story featuring {character.name}, "
        f"a {character.occupation} who must solve a complex case"
    )

    # Create setting
    print("\n" + "─" * 60)
    print("STEP 3: Creating primary setting")
    print("─" * 60 + "\n")

    setting = await stream_structured_setting(
        "An old manor house on the outskirts of Victorian London, "
        "where the mystery unfolds"
    )

    # Summary
    print("\n" + "=" * 60)
    print("  Story Framework Complete!")
    print("=" * 60)
    print(f"\nProtagonist: {character.name}, age {character.age}")
    print(f"Story: {plot.title} ({plot.genre})")
    print(f"Setting: {setting.location_name}")
    print(f"Atmosphere: {setting.atmosphere}")
    print()

    # Return all elements
    return {"character": character, "plot": plot, "setting": setting}


async def save_story_framework(framework: dict, filename: str = "story_framework.json"):
    """
    Save story framework to JSON file.

    Args:
        framework: Dictionary with character, plot, setting
        filename: Output filename
    """
    data = {
        "character": framework["character"].model_dump(),
        "plot": framework["plot"].model_dump(),
        "setting": framework["setting"].model_dump(),
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✓ Story framework saved to {filename}")


async def load_and_display_framework(filename: str = "story_framework.json"):
    """
    Load and display saved story framework.

    Args:
        filename: JSON file to load
    """
    with open(filename, "r") as f:
        data = json.load(f)

    # Reconstruct Pydantic models
    character = CharacterProfile(**data["character"])
    plot = PlotOutline(**data["plot"])
    setting = SceneSetting(**data["setting"])

    print("=" * 60)
    print("  Loaded Story Framework")
    print("=" * 60)

    character.display()
    plot.display()
    setting.display()


async def interactive_story_builder():
    """
    Interactive builder for story elements.

    Allows users to create individual elements or complete frameworks.
    """
    print("=" * 60)
    print("  Interactive Story Builder")
    print("=" * 60)
    print("\nWhat would you like to create?")
    print("  1 - Character")
    print("  2 - Plot outline")
    print("  3 - Setting")
    print("  4 - Complete story framework")
    print("  q - Quit")
    print()

    while True:
        choice = input("Choice: ").strip().lower()

        if choice == "q":
            print("\nGoodbye!")
            break

        elif choice == "1":
            desc = input("\nDescribe the character: ")
            await stream_structured_character(desc)

        elif choice == "2":
            premise = input("\nDescribe the plot: ")
            await stream_structured_plot(premise)

        elif choice == "3":
            location = input("\nDescribe the setting: ")
            await stream_structured_setting(location)

        elif choice == "4":
            framework = await create_complete_story_framework()

            save = input("\nSave framework? (y/n): ").strip().lower()
            if save == "y":
                filename = input("Filename (Enter for default): ").strip()
                if not filename:
                    filename = "story_framework.json"
                await save_story_framework(framework, filename)

        else:
            print("Invalid choice")

        print("\n" + "─" * 60 + "\n")


async def main():
    """Main entry point - demonstrate all features."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        await interactive_story_builder()
    else:
        # Run demonstrations
        print("=== Structured Streaming Demonstrations ===\n")

        # Demo 1: Character
        print("\n" + "=" * 60)
        print("DEMO 1: Structured Character Creation")
        print("=" * 60 + "\n")

        await stream_structured_character(
            "A mysterious librarian who knows ancient secrets"
        )

        # Demo 2: Plot
        print("\n" + "=" * 60)
        print("DEMO 2: Structured Plot Outline")
        print("=" * 60 + "\n")

        await stream_structured_plot(
            "A thriller about uncovering a conspiracy in a small town"
        )

        # Demo 3: Setting
        print("\n" + "=" * 60)
        print("DEMO 3: Structured Setting Description")
        print("=" * 60 + "\n")

        await stream_structured_setting("An abandoned theater with a dark history")

        # Demo 4: Complete framework
        print("\n" + "=" * 60)
        print("DEMO 4: Complete Story Framework")
        print("=" * 60 + "\n")

        framework = await create_complete_story_framework()

        # Optionally save
        print(f"\nRun with --interactive flag for interactive mode")


if __name__ == "__main__":
    asyncio.run(main())
