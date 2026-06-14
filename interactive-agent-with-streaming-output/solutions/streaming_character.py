"""
Lab Solution: Structured Streaming with CharacterProfile

Exercises the structured-streaming pattern — combining `output_type=` with
`agent.run_stream(...)`, `response.stream_output(...)`, and
`await response.get_output()`. The rest of the Core Lab streams plain
text; this file adds the typed-output dimension.

Key API distinction in pydantic-ai 1.x:
- `response.stream_text(delta=True)` is for text-only responses (no
  `output_type=`). It raises `UserError` if `output_type` is set.
- `response.stream_output(debounce_by=...)` is for structured outputs.
  It yields partial Pydantic model instances as the model produces
  enough JSON to parse them — letting you surface progress before the
  final validated output is ready.
- `await response.get_output()` returns the final validated model.
"""

import asyncio
import os
from dotenv import load_dotenv
from pydantic_ai import Agent

# Reuse the CharacterProfile schema defined in structured_streaming.py
# rather than redefining it — the schema is the contract this lab
# teaches students to validate against.
from structured_streaming import CharacterProfile

load_dotenv()


# Build an agent with output_type=CharacterProfile and a short creative
# system prompt. Pydantic AI uses the output_type to constrain the
# model's response and validate it before handing it back.
character_agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    output_type=CharacterProfile,
    system_prompt=(
        "Create vivid, well-rounded character profiles for stories. "
        "Return a CharacterProfile populated with all required fields."
    ),
)


async def stream_character(description: str) -> CharacterProfile:
    """Stream a character creation while surfacing partial parses, then
    await the validated CharacterProfile output and return it.

    The two patterns combined here:
      1. Streaming partial structured outputs via
         `response.stream_output(debounce_by=...)`. Each yield is a
         (possibly partial) `CharacterProfile` — fields appear as the
         model produces enough JSON to parse them. Surfacing these
         partials gives the user feedback that work is happening.
      2. Awaiting `response.get_output()` *inside the async-with block*
         to obtain the *final* validated Pydantic model. Once
         `async with` exits, the streamed result is finalized and the
         model can no longer be retrieved through that response handle.
    """
    print(f"Creating character: {description}\n")
    print("Generating: ", end="", flush=True)

    # YOUR CODE HERE
    # [SOLUTION]
    async with character_agent.run_stream(description) as response:
        # Surface partial structured outputs as fields arrive. Each
        # yield is a (possibly partial) CharacterProfile instance.
        last_seen_name = None
        async for partial in response.stream_output(debounce_by=0.1):
            # Print a small progress marker as fields fill in. The
            # name field tends to arrive first; once we have it, show
            # how many other fields are populated.
            if partial.name and partial.name != last_seen_name:
                last_seen_name = partial.name
                print(f"[{partial.name}] ", end="", flush=True)
            else:
                print(".", end="", flush=True)
        print()  # newline after streaming finishes

        # Pull the validated CharacterProfile from the same async-with
        # block — get_output() is awaitable on a StreamedRunResult.
        return await response.get_output()
    # [/SOLUTION]


async def main():
    character = await stream_character(
        "An elderly clockmaker who guards an ancient secret"
    )
    print()
    character.display()


if __name__ == "__main__":
    asyncio.run(main())
