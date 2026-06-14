# Interactive Agent with Streaming Output - Solution

Complete reference implementation demonstrating streaming AI responses with Pydantic AI.

## Features

- ✅ **Token-by-token streaming** with real-time display
- ✅ **Interactive conversation loops** with history management
- ✅ **Progress indicators** and performance statistics
- ✅ **Structured output** while streaming
- ✅ **Interruptible streaming** with user corrections
- ✅ **Parallel streaming** from multiple agents
- ✅ **Cross-platform support** (Unix, Mac, Windows)

## Project Structure

```
.
├── writer_agent.py              # Basic streaming patterns
├── interactive_loop.py          # Multi-turn conversations
├── stream_utils.py              # Streaming utilities
├── structured_streaming.py      # Streaming with Pydantic models
├── test_streaming.py            # Comprehensive tests
├── challenge1_interruptible.py  # Interrupt mechanism
├── challenge2_parallel.py       # Parallel streaming
├── pyproject.toml              # UV dependencies
└── .env.example                # Environment template
```

## Quick Start

### 1. Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
```

### 2. Install Dependencies

```bash
# Using UV
uv sync

# Or with pip
pip install pydantic-ai pydantic python-dotenv openai pytest pytest-asyncio
```

### 3. Run Examples

```bash
# Basic streaming
uv run python writer_agent.py

# Interactive conversation
uv run python interactive_loop.py

# Streaming utilities demo
uv run python stream_utils.py

# Structured output
uv run python structured_streaming.py

# Challenge 1: Interruptible
uv run python challenge1_interruptible.py

# Challenge 2: Parallel
uv run python challenge2_parallel.py

# Run tests
uv run pytest test_streaming.py -v
```

## Core Concepts

### Basic Streaming

The fundamental streaming pattern:

```python
from pydantic_ai import Agent
import asyncio

agent = Agent('openai:gpt-5.4-mini')

async def stream_response(prompt: str):
    print("Assistant: ", end='', flush=True)

    async with agent.run_stream(prompt) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end='', flush=True)

    print()  # Newline
    return response

asyncio.run(stream_response("Write a short story"))
```

**Key Points:**

- Use `run_stream()` instead of `run()`
- Context manager handles resource cleanup
- Iterate chunks with `async for`
- Print with `flush=True` for real-time display
- Access complete `response` after streaming

### Interactive Conversations

Maintain context across multiple turns:

```python
history = []

while True:
    user_input = input("You: ")

    print("Assistant: ", end='', flush=True)

    async with agent.run_stream(
        user_input,
        message_history=history
    ) as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end='', flush=True)

    # Update history for next turn
    history = response.all_messages()
```

**Key Points:**

- Pass `message_history` to maintain context
- Update history with `response.all_messages()`
- Works with streaming and batch modes

### Streaming with Statistics

Track performance metrics:

```python
from stream_utils import StreamingDisplay

display = StreamingDisplay()

async with agent.run_stream(prompt) as response:
    await display.display_stream(response.stream_text(delta=True))

display.show_stats(verbose=True)
```

**Metrics:**

- Character count
- Word count
- Duration
- Characters/second
- Words/second
- Chunk count

### Structured Output

Stream while building typed data:

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class Character(BaseModel):
    name: str
    age: int
    traits: list[str]

# Pydantic AI 1.x uses `output_type=` (the pre-1.0 name was `result_type=`,
# kept here only as a back-reference because older tutorials still cite it).
agent = Agent('openai:gpt-5.4-mini', output_type=Character)

async with agent.run_stream("Create a character") as response:
    # Stream text representation as it's produced
    async for chunk in response.stream_text(delta=True):
        print(chunk, end='', flush=True)

    # On a StreamedRunResult, `output` is awaitable — call get_output()
    # *inside* the async-with block, after streaming has finished, to get
    # the validated Pydantic model. (Pre-1.0 used `response.data`; that
    # attribute is gone in 1.x.)
    character = await response.get_output()

print(f"\nName: {character.name}, Age: {character.age}")
```

**Key Points:**

- Define `output_type=` with a Pydantic model.
- Stream shows the text representation as the model produces it.
- `await response.get_output()` returns the validated object once streaming completes — call it inside the `async with` block.
- Full type safety and validation.

## Advanced Features

### Interruptible Streaming

Allow users to stop and provide feedback:

```python
from challenge1_interruptible import InterruptibleStreamer

streamer = InterruptibleStreamer(agent)

# User can press 's' to interrupt
response = await streamer.interactive_with_corrections(
    "Write a long story",
    max_retries=3
)
```

**Features:**

- Non-blocking keyboard input (Unix/Mac)
- Threading-based approach (Windows)
- Collect user feedback
- Refine and restart with corrections

### Parallel Streaming

Stream from multiple agents simultaneously:

```python
from challenge2_parallel import ParallelStreamCoordinator

coordinator = ParallelStreamCoordinator()

results = await coordinator.parallel_streaming(
    "A mystery story concept"
)

# Results contain: plot, characters, setting, themes
```

**Benefits:**

- Faster than sequential (true parallelism)
- Organized output by agent
- Performance statistics
- Result aggregation

## Streaming Utilities

### Progress Indicators

Show animated spinner:

```python
from stream_utils import stream_with_progress

result = await stream_with_progress(agent, "Generate content")
```

### Buffered Streaming

Reduce flicker with buffering:

```python
from stream_utils import stream_buffered

result = await stream_buffered(
    agent,
    "Write content",
    flush_interval=0.1  # Seconds between flushes
)
```

### Stream Logging

Debug streaming behavior:

```python
from stream_utils import StreamLogger

logger = StreamLogger("stream.log")

async with agent.run_stream(prompt) as response:
    async for chunk in response.stream_text(delta=True):
        logger.log_chunk(chunk)
        print(chunk, end='', flush=True)

logger.log_stats()
```

## Testing

### Run All Tests

```bash
# All tests
uv run pytest test_streaming.py -v

# Specific test
uv run pytest test_streaming.py::test_basic_streaming -v

# With coverage
pytest test_streaming.py --cov=. --cov-report=html
```

### Test Structure

Tests cover:

- Basic streaming patterns
- Conversation history
- Response object access
- Multiple independent streams
- Structured output
- Streaming utilities
- Error handling
- Performance
- Tool integration

## Interactive Modes

### Interactive Loop

```bash
python interactive_loop.py
```

**Commands:**

- Type normally for conversation
- `history` - Show conversation
- `clear` - Clear history
- `save` - Save to file
- `quit` - Exit

**Modes:**

1. Free-form conversation
2. Guided story development

### Structured Builder

```bash
python structured_streaming.py --interactive
```

**Options:**

1. Create character
2. Create plot outline
3. Create setting
4. Complete framework
5. Save framework

## Challenge Solutions

### Challenge 1: Interrupt Mechanism

**Goal:** Allow users to stop mid-stream and provide corrections.

**Implementation:**

- **Unix/Mac:** Non-blocking `select()` for keyboard input
- **Windows:** Threading-based input monitoring
- Graceful interrupt handling
- Feedback collection and refinement
- Automatic retry with corrections

**Usage:**

```bash
python challenge1_interruptible.py
```

Press 's' (or Enter on Windows) during streaming to interrupt.

### Challenge 2: Parallel Streaming

**Goal:** Stream from multiple specialist agents simultaneously.

**Implementation:**

- Four specialist agents (plot, character, setting, theme)
- `asyncio.gather()` for parallel execution
- Coordinated output with color coding
- Performance comparison vs sequential
- Structured framework generation

**Usage:**

```bash
python challenge2_parallel.py
```

**Performance:**
Parallel streaming is typically 2-4x faster than sequential when using actual API calls.

## Production Considerations

### User Experience

- ✅ Show streaming for responses > 100 words
- ✅ Use batch mode for short responses
- ✅ Add progress indicators for long generations
- ✅ Allow interrupts for very long content
- ✅ Buffer output to reduce flicker

### Error Handling

```python
async def robust_stream(agent, prompt, max_retries=2):
    for attempt in range(max_retries):
        try:
            async with agent.run_stream(prompt) as response:
                chunks = []
                try:
                    async for chunk in response.stream_text(delta=True):
                        print(chunk, end='', flush=True)
                        chunks.append(chunk)
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"\n[Retrying...]")
                        continue
                    raise

                return response
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
```

### Web Integration

For web apps, use Server-Sent Events (SSE):

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/stream")
async def stream_endpoint(prompt: str):
    async def generate():
        async with agent.run_stream(prompt) as response:
            async for chunk in response.stream_text(delta=True):
                yield f"data: {chunk}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

### Performance Optimization

- Use `asyncio.gather()` for parallel requests
- Buffer output to reduce system calls
- Implement caching for repeated queries
- Use connection pooling for API calls
- Monitor token usage and latency

## Troubleshooting

### No Streaming Output

**Problem:** Response appears all at once, not streaming.

**Solutions:**

- Use `flush=True` when printing
- Check that you're using `run_stream()` not `run()`
- Verify async context manager is used

### Flicker in Terminal

**Problem:** Terminal flickers during streaming.

**Solution:** Use buffered streaming:

```python
from stream_utils import stream_buffered
```

### Interrupts Not Working

**Problem:** Can't interrupt on Windows.

**Solution:** Use threaded implementation:

```python
from challenge1_interruptible import ThreadedInterruptibleStreamer
```

### Parallel Slower Than Sequential

**Problem:** Parallel mode not faster.

**Solution:**

- This is expected with test model (instant responses)
- With real API calls, parallel is significantly faster
- Test with `openai:gpt-5.4-mini` for realistic comparison

## Additional Resources

- [Pydantic AI Streaming Docs](https://ai.pydantic.dev/streaming/)
- [AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html)
- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

## License

Educational use only - Part of GAI-2109 course materials.
