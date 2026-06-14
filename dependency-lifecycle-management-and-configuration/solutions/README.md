# Dependency Lifecycle Management and Configuration - Solution

Complete reference implementation demonstrating production-grade dependency lifecycle management with type-safe configuration.

## Features

- ✅ **Type-safe configuration** with Pydantic Settings
- ✅ **Lifecycle management** with initialization/cleanup hooks
- ✅ **Context managers** for automatic resource management
- ✅ **Health checks** for all dependencies
- ✅ **Graceful shutdown** with timeout for in-flight requests
- ✅ **Testing support** with fake dependencies
- ✅ **FastAPI integration** with lifespan events

## Project Structure

```
.
├── config.py                    # Pydantic Settings configuration
├── dependencies.py              # Dependencies with lifecycle hooks
├── lifecycle_manager.py         # Lifecycle orchestration
├── agent.py                     # Agent using managed dependencies
├── test_lifecycle.py            # Tests with fake dependencies
├── challenge1_health_checks.py  # Comprehensive health checks
├── challenge2_graceful_shutdown.py  # Graceful shutdown
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
pip install pydantic-ai pydantic-settings python-dotenv openai httpx pytest pytest-asyncio
```

### 3. Run Examples

```bash
# Run configuration example
uv run python config.py

# Run lifecycle manager example
uv run python lifecycle_manager.py

# Run agent example
uv run python agent.py

# Run tests
uv run pytest test_lifecycle.py -v
```

## Configuration Management

### Type-Safe Settings

```python
from config import Settings, load_config

# Load from environment
settings = load_config()

# Access with type safety
print(settings.database_url)      # str
print(settings.database_pool_size) # int
print(settings.enable_caching)     # bool
```

### Environment Variables

All settings can be configured via environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/db
DATABASE_POOL_SIZE=20

# Cache
REDIS_HOST=redis.example.com
REDIS_PORT=6379
REDIS_TTL=3600

# Features
ENABLE_CACHING=true
MAX_RETRIES=5
```

### Validation

Configuration is validated on load:

```python
settings = Settings(
    openai_api_key="key",
    environment="invalid"  # ❌ Error: must be development/staging/production
)

settings = Settings(
    database_pool_size=200  # ❌ Error: max is 100
)
```

## Lifecycle Management

### Basic Usage

```python
from lifecycle_manager import LifecycleManager

manager = LifecycleManager()

# Manual lifecycle
deps = await manager.initialize()
# ... use dependencies ...
await manager.shutdown()

# Context manager (recommended)
async with manager.lifespan() as deps:
    # Dependencies initialized
    result = await deps.database.query("SELECT * FROM orders")
    # Automatic cleanup on exit
```

### Initialization Order

Dependencies are initialized in dependency order:

1. **Database** - Connection pool
2. **Cache** - Redis connection
3. **HTTP Client** - Connection pooling

### Shutdown Order

Shutdown happens in reverse order, ensuring proper cleanup even on errors.

### Error Handling

```python
async with manager.lifespan() as deps:
    # If initialization fails, partial cleanup happens automatically
    result = await deps.database.query(...)

    # If runtime error occurs, cleanup still happens
    raise RuntimeError("Something went wrong")
# Dependencies cleaned up even with error
```

## Dependencies

### Database Client

```python
# Initialize
await db.initialize()

# Use
result = await db.query("SELECT * FROM orders WHERE id = :id", {'id': 'ORD-123'})
affected = await db.execute("UPDATE orders SET status = :status", {'status': 'shipped'})

# Stats
stats = db.get_stats()  # {'status': 'initialized', 'active_connections': 2}

# Cleanup
await db.close()
```

### Cache Client

```python
# Initialize
await cache.initialize()

# Use
await cache.set('key', 'value', ttl=3600)
value = await cache.get('key')
await cache.delete('key')

# Stats
stats = cache.get_stats()  # {'status': 'initialized', 'entries': 42}

# Cleanup
await cache.close()
```

### HTTP Client

```python
# Initialize
await http.initialize()

# Use
response = await http.get('https://api.example.com/data')
response = await http.post('https://api.example.com/create', json={...})

# Stats
stats = http.get_stats()  # {'status': 'initialized', 'timeout': 30.0}

# Cleanup
await http.close()
```

## Testing

### Run Tests

```bash
# All tests
uv run pytest test_lifecycle.py -v

# Specific test
uv run pytest test_lifecycle.py::test_lifecycle_initialization -v

# With coverage
pytest test_lifecycle.py --cov=. --cov-report=html
```

### Fake Dependencies

```python
class FakeDatabaseClient:
    def __init__(self, settings):
        self.queries = []

    async def query(self, sql, params=None):
        self.queries.append((sql, params))
        return [{'id': 1, 'data': 'fake'}]

# Use in tests
fake_db = FakeDatabaseClient(settings)
result = await fake_db.query("SELECT 1")
assert len(fake_db.queries) == 1
```

## Challenge Solutions

### Challenge 1: Health Checks

Comprehensive health checks for monitoring:

```bash
uv run python challenge1_health_checks.py
```

**Features:**

- Individual dependency checks (database, cache, HTTP)
- Latency measurement
- Overall status (healthy/degraded/unhealthy)
- FastAPI endpoint integration

**Usage:**

```python
from challenge1_health_checks import HealthChecker

checker = HealthChecker(deps)

# Check individual dependency
result = await checker.check_database()
print(f"Database: {result.healthy} ({result.latency_ms}ms)")

# Check all
results = await checker.check_all()

# Get full report
report = await checker.get_health_report()
```

**FastAPI Integration:**

```python
@app.get("/health")
async def health():
    checker = HealthChecker(app_dependencies)
    return await checker.get_health_report()
```

### Challenge 2: Graceful Shutdown

Graceful shutdown with timeout for in-flight requests:

```bash
uv run python challenge2_graceful_shutdown.py
```

**Features:**

- Tracks active requests
- Rejects new requests during shutdown
- Waits for completion with grace period
- Forces shutdown if timeout expires

**Usage:**

```python
from challenge2_graceful_shutdown import GracefulShutdownManager

shutdown_manager = GracefulShutdownManager(
    lifecycle_manager,
    ShutdownConfig(grace_period_seconds=30.0)
)

# Track request
await shutdown_manager.increment_active_requests()
try:
    # Process request
    result = await process_query(...)
finally:
    await shutdown_manager.decrement_active_requests()

# Graceful shutdown
await shutdown_manager.shutdown()
```

**FastAPI Integration:**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await lifecycle_manager.initialize()
    shutdown_manager = GracefulShutdownManager(lifecycle_manager)

    yield

    # Graceful shutdown
    await shutdown_manager.shutdown()
```

## Production Considerations

### Configuration

- ✅ Use environment variables for all config
- ✅ Validate on startup (fail fast)
- ✅ Mask sensitive values in logs
- ✅ Use secrets management (AWS Secrets Manager, Vault)

### Lifecycle

- ✅ Initialize dependencies in correct order
- ✅ Handle partial initialization failures
- ✅ Cleanup even on errors
- ✅ Log all lifecycle events

### Health Checks

- ✅ Implement for all dependencies
- ✅ Expose via HTTP endpoint
- ✅ Measure latency
- ✅ Alert on failures

### Graceful Shutdown

- ✅ Track active requests
- ✅ Reject new requests during shutdown
- ✅ Wait for completion (with timeout)
- ✅ Force shutdown if needed

## Troubleshooting

### Configuration Errors

```
ValueError: Invalid environment: invalid_env
```

**Solution**: Use `development`, `staging`, or `production`

### Initialization Failures

```
RuntimeError: Failed to initialize database
```

**Solution**: Check database connection string and credentials

### Cleanup Errors

```
WARNING: Cleanup errors: ['Database: Connection closed']
```

**Solution**: These are logged but don't prevent shutdown

## Additional Resources

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)
- [Graceful Shutdown Patterns](https://cloud.google.com/blog/products/containers-kubernetes/kubernetes-best-practices-terminating-with-grace)

## License

Educational use only - Part of GAI-2109 course materials.
