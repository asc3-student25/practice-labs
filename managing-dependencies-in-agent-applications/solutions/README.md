# Managing Dependencies in Agent Applications - Solution

Complete reference implementation demonstrating dependency injection for AI agents using Pydantic AI's RunContext.

## Project Structure

```
.
├── dependencies.py                        # Core dependency definitions
├── agent.py                               # Agent with DI via RunContext
├── database.py                            # Database pool management
├── factory.py                             # Dependency factory
├── test_agent.py                          # Tests with mocked dependencies
├── challenge1_scoped_dependencies.py      # Challenge 1: Dependency scopes
├── challenge2_ioc_container.py            # Challenge 2: IoC container
├── pyproject.toml                         # UV dependencies
└── .env.example                           # Environment template
```

## Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your-key-here
```

### 2. Install Dependencies

```bash
# Install with UV
uv sync

# Or create virtual environment and install
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install pydantic-ai python-dotenv openai pytest pytest-asyncio
```

### 3. Run Agent

```bash
# Run main agent example
uv run python agent.py

# Or with factory
uv run python factory.py
```

## Core Concepts

### Dependency Injection

Pass dependencies to components instead of hardcoding them:

```python
# ❌ Hardcoded (bad)
class Agent:
    def __init__(self):
        self.db = DatabaseConnection("hardcoded://connection")

# ✅ Injected (good)
class Agent:
    def __init__(self, db: DatabaseConnection):
        self.db = db
```

### RunContext

Pydantic AI's type-safe dependency injection:

```python
@order_agent.tool
async def get_order(ctx: RunContext[AgentDependencies], order_id: str):
    # Access injected dependencies
    result = await ctx.deps.database.query(...)
    await ctx.deps.cache.set(...)
    return result
```

### State Isolation

Each agent run gets independent dependency instances:

```python
deps1 = await factory.create_dependencies()
deps2 = await factory.create_dependencies()

# Separate cache instances - no shared state
```

## Key Features

### 1. Type-Safe Dependency Injection

```python
# Dependencies container
@dataclass
class AgentDependencies:
    database: DatabaseConnection
    cache: CacheClient
    email: EmailService
    config: AppConfig

# Agent tools get type-safe access
@order_agent.tool
async def get_order(ctx: RunContext[AgentDependencies], order_id: str):
    # ctx.deps is fully typed!
    cached = await ctx.deps.cache.get(cache_key)
```

### 2. Cache-Aside Pattern

```python
# Try cache first
cached = await ctx.deps.cache.get(cache_key)
if cached:
    return cached

# Cache miss - query database
result = await ctx.deps.database.query(...)

# Cache for future requests
await ctx.deps.cache.set(cache_key, result)
```

### 3. Resource Lifecycle Management

```python
factory = DependencyFactory()

try:
    deps = await factory.create_dependencies()
    # Use dependencies
finally:
    # Proper cleanup
    await factory.shutdown()
```

### 4. Testing with Mocks

```python
class MockDatabase:
    def __init__(self):
        self.query = AsyncMock(return_value=[...])

def create_test_dependencies():
    return AgentDependencies(
        database=MockDatabase(),
        cache=MockCache(),
        email=MockEmail(),
        config=test_config
    )

# Test without external dependencies
deps = create_test_dependencies()
```

## Testing

### Run All Tests

```bash
# Run with UV
uv run pytest test_agent.py -v

# Or with pytest directly
pytest test_agent.py -v

# With coverage
pytest test_agent.py --cov=. --cov-report=html
```

### Test Coverage

The test suite covers:

- ✅ Cache hit/miss scenarios
- ✅ Email sending with feature flags
- ✅ Dependency isolation
- ✅ Concurrent requests
- ✅ Error handling
- ✅ Cache operations
- ✅ Feature flag checks

### Example Test

```python
@pytest.mark.asyncio
async def test_get_order_cache_miss():
    deps = create_test_dependencies()
    ctx = create_run_context(deps)

    order = await get_order(ctx, "ORD-123")

    # Verify database was queried
    deps.database.query.assert_called_once()

    # Verify result was cached
    deps.cache.set.assert_called_once()
```

## Challenge Solutions

### Challenge 1: Scoped Dependencies

Implements three dependency scopes:

```bash
uv run python challenge1_scoped_dependencies.py
```

**Scopes:**

- **Singleton**: One instance for entire application

  ```python
  container.register("database", DatabaseService, DependencyScope.SINGLETON)
  ```

- **Request**: New instance per agent run

  ```python
  container.register("context", RequestContext, DependencyScope.REQUEST)
  ```

- **Transient**: New instance every time requested
  ```python
  container.register("logger", Logger, DependencyScope.TRANSIENT)
  ```

**Key Features:**

- Scope-based lifecycle management
- Request context tracking
- Automatic disposal

### Challenge 2: IoC Container

Implements inversion of control with automatic dependency resolution:

```bash
uv run python challenge2_ioc_container.py
```

**Features:**

- **Constructor Injection**: Automatically resolves dependencies from constructor parameters

  ```python
  class OrderService:
      def __init__(self, database: IDatabase, cache: ICache):
          # Dependencies injected automatically!
  ```

- **Circular Dependency Detection**: Prevents infinite loops

  ```python
  # Raises CircularDependencyError
  class ServiceA:
      def __init__(self, service_b: ServiceB): ...

  class ServiceB:
      def __init__(self, service_a: ServiceA): ...
  ```

- **Lifetime Management**: Singleton and transient lifetimes

  ```python
  container.register_singleton(IDatabase, SqlDatabase)
  container.register_transient(OrderService)
  ```

- **Dispose Pattern**: Automatic cleanup
  ```python
  await container.dispose()  # Calls dispose() on all singletons
  ```

## Architecture

### Dependency Graph

```
OrderAgent
    ├── DatabaseConnection (singleton pool)
    ├── CacheClient (request-scoped)
    ├── EmailService (singleton)
    └── AppConfig (singleton)
```

### Tool Functions

All tools receive dependencies via RunContext:

```python
@order_agent.tool
async def get_order(ctx: RunContext[AgentDependencies], order_id: str):
    """Lookup order - uses database and cache."""

@order_agent.tool
async def send_order_update(ctx: RunContext[AgentDependencies], ...):
    """Send email - uses email service."""

@order_agent.tool
async def check_feature_enabled(ctx: RunContext[AgentDependencies], ...):
    """Check feature flag - uses config."""
```

## Best Practices

### 1. Separate Concerns

```python
# Dependencies - what you need
class AgentDependencies:
    database: DatabaseConnection
    cache: CacheClient

# Factory - how to create them
class DependencyFactory:
    async def create_dependencies(self): ...

# Agent - what to do with them
@order_agent.tool
async def get_order(ctx: RunContext[AgentDependencies]): ...
```

### 2. Use Interfaces/Protocols

```python
from typing import Protocol

class IDatabase(Protocol):
    async def query(self, sql: str) -> list: ...

# Allows swapping implementations
class SqliteDatabase: ...
class PostgresDatabase: ...
```

### 3. Manage Resource Lifecycle

```python
# ✅ Use context managers
async with pool.get_connection() as conn:
    await conn.query(...)

# ✅ Use try/finally
try:
    deps = await factory.create_dependencies()
    await agent.run(query, deps=deps)
finally:
    await factory.shutdown()
```

### 4. Test with Mocks

```python
# ✅ Create dedicated mock classes
class MockDatabase:
    def __init__(self):
        self.query = AsyncMock()

# ✅ Use factory for test dependencies
def create_test_dependencies():
    return AgentDependencies(
        database=MockDatabase(),
        ...
    )
```

## Production Considerations

### Singleton Resources

- Database connection pools
- Cache clients (Redis, Memcached)
- HTTP clients
- Configuration

### Request-Scoped Resources

- Request context
- User sessions
- Transaction scopes
- Request tracing

### Transient Resources

- Loggers
- Validators
- Formatters
- Temporary utilities

### Health Checks

```python
async def health_check():
    """Verify all dependencies are healthy."""
    # Check database
    await database.query("SELECT 1")

    # Check cache
    await cache.set("health", "ok")

    # Check email service
    # ...
```

## Troubleshooting

### Dependency Not Found

```
ValueError: Dependency 'database' not registered
```

**Solution**: Register dependency before resolving

```python
container.register("database", DatabaseConnection)
```

### Circular Dependency

```
CircularDependencyError: Circular dependency detected
```

**Solution**: Break the cycle using interfaces or restructure dependencies

### Type Errors

```
AttributeError: 'RunContext' object has no attribute 'deps'
```

**Solution**: Ensure agent created with `deps_type`

```python
agent = Agent(model, deps_type=AgentDependencies)
```

## Additional Resources

- [Pydantic AI Documentation](https://ai.pydantic.dev/)
- [Dependency Injection Principles](https://en.wikipedia.org/wiki/Dependency_injection)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

## License

Educational use only - Part of GAI-2109 course materials.
