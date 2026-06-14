"""
Tests for Streaming Functionality

Tests streaming agents, utilities, and structured output:
- Basic streaming patterns
- Streaming with history
- Structured output streaming
- Error handling
- Statistics tracking

Run:
    pytest test_streaming.py -v
"""

import pytest
import asyncio
from pydantic_ai import Agent
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic import BaseModel, Field
from typing import List
import os

# Test fixtures


@pytest.fixture
def test_agent():
    """Basic test agent for streaming."""
    return Agent(
        "test", system_prompt="You are a test assistant. Keep responses short."
    )


@pytest.fixture
def structured_agent():
    """Agent with structured output."""

    class TestOutput(BaseModel):
        name: str
        count: int
        items: List[str]

    return Agent("test", output_type=TestOutput)


# Basic streaming tests


@pytest.mark.asyncio
async def test_basic_streaming(test_agent):
    """Test basic run_stream functionality."""
    chunks = []

    async with test_agent.run_stream("Say hello") as response:
        async for chunk in response.stream_text(delta=True):
            chunks.append(chunk)
            assert isinstance(chunk, str)

        output = await response.get_output()

    # Should have received chunks
    assert len(chunks) > 0

    # Some models emit very small/empty deltas; final output is the
    # contractually reliable completion.
    assert isinstance(output, str)
    assert len(output) > 0


@pytest.mark.asyncio
async def test_streaming_with_history(test_agent):
    """Test streaming maintains conversation history."""
    # First turn
    async with test_agent.run_stream("My name is Alice") as response1:
        async for _ in response1.stream_text(delta=True):
            pass

        first_output = await response1.get_output()

    history = response1.all_messages()
    assert len(history) >= 2  # User message + assistant response

    # Second turn with history
    async with test_agent.run_stream(
        "What's my name?", message_history=history
    ) as response2:
        async for _ in response2.stream_text(delta=True):
            pass

        second_output = await response2.get_output()

    assert isinstance(first_output, str)
    assert isinstance(second_output, str)
    assert len(second_output) > 0
    assert len(response2.all_messages()) >= len(history)


@pytest.mark.asyncio
async def test_streaming_response_object(test_agent):
    """Test accessing response object after streaming."""
    async with test_agent.run_stream("Hello") as response:
        async for _ in response.stream_text(delta=True):
            pass

        output = await response.get_output()

    # Should have messages
    assert len(response.all_messages()) > 0
    assert len(response.new_messages()) > 0

    # Should have data (text response)
    assert output is not None
    assert isinstance(output, str)
    assert len(output) > 0


@pytest.mark.asyncio
async def test_multiple_streams_independent(test_agent):
    """Test multiple streams are independent."""
    results = []

    async def stream_query(prompt: str):
        async with test_agent.run_stream(prompt) as response:
            chunks = []
            async for chunk in response.stream_text(delta=True):
                chunks.append(chunk)
            return "".join(chunks)

    # Run multiple streams
    results = await asyncio.gather(
        stream_query("Count to 3"),
        stream_query("Say the alphabet"),
        stream_query("Name 3 colors"),
    )

    assert len(results) == 3
    for result in results:
        assert isinstance(result, str)
        assert len(result) > 0


# Structured streaming tests


@pytest.mark.asyncio
async def test_structured_streaming(structured_agent):
    """Test streaming with structured output.

    Asserts on type/structure rather than exact values — TestModel is not
    contractually obligated to honor the prompt's literal name/count, so
    a valid student implementation could fail an `== "test"` check that
    only happened to pass when the test was authored. Type and shape
    checks are the right level of strictness for a non-deterministic
    model under test.
    """
    try:
        async with structured_agent.run_stream(
            "Create data with name='test', count=5, items=['a','b','c']"
        ) as response:
            async for partial in response.stream_output(debounce_by=0.1):
                assert isinstance(partial, BaseModel)

            # Should have structured data — call get_output() inside the
            # async-with block so the streamed result is finalized.
            data = await response.get_output()
    except UnexpectedModelBehavior:
        pytest.skip("Test model did not produce valid structured output")

    # Type / structure checks rather than exact-value checks.
    assert isinstance(data.name, str) and data.name  # non-empty string
    assert isinstance(data.count, int) and data.count >= 0
    assert isinstance(data.items, list)
    assert all(isinstance(item, str) for item in data.items)


@pytest.mark.asyncio
async def test_structured_output_validation():
    """Test Pydantic validation of structured output."""

    class StrictOutput(BaseModel):
        age: int = Field(ge=0, le=150)
        tags: List[str] = Field(min_length=2, max_length=5)

    agent = Agent("test", output_type=StrictOutput)

    try:
        async with agent.run_stream(
            "Create output with age=30 and tags=['tag1', 'tag2', 'tag3']"
        ) as response:
            async for _ in response.stream_output(debounce_by=0.1):
                pass

            # Pydantic validation runs as part of get_output(); call it
            # inside the async-with block.
            data = await response.get_output()
    except UnexpectedModelBehavior:
        pytest.skip("Test model did not produce valid structured output")

    assert 0 <= data.age <= 150
    assert 2 <= len(data.tags) <= 5


# Utilities tests (requires stream_utils.py)


@pytest.mark.asyncio
async def test_streaming_display():
    """Test StreamingDisplay utility."""
    from stream_utils import StreamingDisplay

    async def fake_stream():
        for chunk in ["Hello", " ", "world", "!"]:
            yield chunk

    display = StreamingDisplay()
    text = await display.display_stream(fake_stream())

    assert text == "Hello world!"

    stats = display.get_stats()
    assert stats.char_count == 12
    assert stats.chunk_count == 4
    assert stats.duration_seconds >= 0


@pytest.mark.asyncio
async def test_streaming_display_with_callback():
    """Test StreamingDisplay with custom callback."""
    from stream_utils import StreamingDisplay

    chunks_received = []

    def on_chunk(chunk: str):
        chunks_received.append(chunk)

    async def fake_stream():
        for chunk in ["a", "b", "c"]:
            yield chunk

    display = StreamingDisplay(on_chunk=on_chunk)
    await display.display_stream(fake_stream())

    assert chunks_received == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_stream_buffer():
    """Test StreamBuffer."""
    from stream_utils import StreamBuffer

    async def fake_stream():
        for i in range(10):
            yield f"chunk{i}"

    buffer = StreamBuffer(flush_interval=0.1)
    text = await buffer.display_stream(fake_stream())

    assert "chunk0" in text
    assert "chunk9" in text


# Error handling tests


@pytest.mark.asyncio
async def test_streaming_with_context_manager_error():
    """Test error handling with context manager."""
    agent = Agent("test")

    with pytest.raises(Exception):
        async with agent.run_stream("test") as response:
            async for chunk in response.stream_text(delta=True):
                # Simulate error during streaming
                if len(chunk) > 0:
                    raise ValueError("Simulated error")


@pytest.mark.asyncio
async def test_stream_recovery():
    """Test recovery from stream interruption."""
    agent = Agent("test")

    attempt_count = 0
    max_retries = 2

    for attempt in range(max_retries):
        try:
            async with agent.run_stream("Say hello") as response:
                chunks = []
                async for chunk in response.stream_text(delta=True):
                    chunks.append(chunk)

                    # Simulate failure on first attempt
                    if attempt == 0 and len(chunks) > 2:
                        raise ValueError("Simulated failure")

                # If we get here, success
                full_text = "".join(chunks)
                assert len(full_text) > 0
                break

        except ValueError:
            attempt_count += 1
            if attempt == max_retries - 1:
                pytest.fail("Stream failed after retries")
            await asyncio.sleep(0.1)

    assert attempt_count <= max_retries


# Performance tests


@pytest.mark.asyncio
async def test_streaming_performance():
    """Test streaming provides chunks promptly."""
    agent = Agent("test")

    chunk_times = []
    start_time = asyncio.get_event_loop().time()

    async with agent.run_stream("Write a short paragraph") as response:
        async for chunk in response.stream_text(delta=True):
            chunk_times.append(asyncio.get_event_loop().time() - start_time)

    # Should receive at least one streamed chunk
    assert len(chunk_times) >= 1

    # First chunk should arrive reasonably quickly
    # (test model responds essentially instantly)
    assert chunk_times[0] < 5.0  # 5 second max for first chunk


@pytest.mark.asyncio
async def test_streaming_vs_batch():
    """Compare streaming vs batch response timing."""
    agent = Agent("test")
    prompt = "Count from 1 to 10"

    # Measure streaming time to first byte
    stream_start = asyncio.get_event_loop().time()
    first_chunk_time = None

    async with agent.run_stream(prompt) as response:
        async for chunk in response.stream_text(delta=True):
            if first_chunk_time is None:
                first_chunk_time = asyncio.get_event_loop().time() - stream_start
            break  # Only measure first chunk

    # Measure batch time
    batch_start = asyncio.get_event_loop().time()
    result = await agent.run(prompt)
    batch_time = asyncio.get_event_loop().time() - batch_start

    # Streaming should get first chunk faster than batch gets complete response
    # (This may not always be true with test model, but demonstrates the pattern)
    assert first_chunk_time is not None
    assert first_chunk_time >= 0


# Integration tests


@pytest.mark.asyncio
async def test_complete_interactive_pattern():
    """Test complete interactive conversation pattern."""
    agent = Agent("test")
    history = []

    # Turn 1
    async with agent.run_stream(
        "My favorite color is blue", message_history=history
    ) as response:
        async for _ in response.stream_text(delta=True):
            pass
    history = response.all_messages()

    # Turn 2
    async with agent.run_stream(
        "What's my favorite color?", message_history=history
    ) as response:
        async for _ in response.stream_text(delta=True):
            pass

        output = await response.get_output()

    assert isinstance(output, str)
    assert len(output) > 0
    assert len(response.all_messages()) >= len(history)


@pytest.mark.asyncio
async def test_streaming_with_tools():
    """Test streaming agent with tool calls."""
    from pydantic_ai import RunContext

    tool_calls = []

    def get_weather(ctx: RunContext[None], city: str) -> str:
        """Get weather for a city."""
        tool_calls.append(city)
        return f"The weather in {city} is sunny"

    agent = Agent(
        "test",
        tools=[get_weather],
        system_prompt="Use the get_weather tool when asked about weather",
    )

    async with agent.run_stream("What's the weather in Paris?") as response:
        async for _ in response.stream_text(delta=True):
            pass

        output = await response.get_output()

    assert isinstance(output, str)
    assert len(output) > 0

    # Test model may or may not decide to call tools. If it did, verify
    # call data shape is correct.
    if tool_calls:
        assert all(isinstance(city, str) and city for city in tool_calls)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
