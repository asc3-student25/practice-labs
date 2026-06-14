"""
Challenge 2: IoC Container with Automatic Dependency Resolution
Implements inversion of control with dependency graph resolution
"""

from typing import TypeVar, Generic, Callable, Any, Optional, get_type_hints
from dataclasses import dataclass, field
from enum import Enum
import inspect
import asyncio
import logging

logger = logging.getLogger(__name__)


T = TypeVar("T")


class Lifetime(Enum):
    """Dependency lifetimes."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"


@dataclass
class ServiceDescriptor:
    """
    Describes a service registration.

    Attributes:
        service_type: Type/interface being registered
        implementation: Concrete implementation type or factory
        lifetime: Service lifetime
        instance: Cached instance for singletons
    """

    service_type: type
    implementation: Any
    lifetime: Lifetime
    instance: Optional[Any] = None


class CircularDependencyError(Exception):
    """Raised when circular dependency detected."""

    pass


class IoCContainer:
    """
    Inversion of Control container with automatic dependency resolution.

    Features:
    - Automatic constructor injection
    - Dependency graph resolution
    - Circular dependency detection
    - Singleton and transient lifetimes
    - Dispose pattern for cleanup
    """

    def __init__(self):
        """Initialize empty container."""
        self._services: dict[type, ServiceDescriptor] = {}
        self._resolving: set[type] = set()  # For circular dependency detection

    def register_singleton(self, service_type: type, implementation: Any = None):
        """
        Register singleton service.

        Args:
            service_type: Service interface/type
            implementation: Implementation class or factory (defaults to service_type)
        """
        impl = implementation or service_type
        logger.info(f"Registering singleton: {service_type.__name__}")

        self._services[service_type] = ServiceDescriptor(
            service_type=service_type, implementation=impl, lifetime=Lifetime.SINGLETON
        )

    def register_transient(self, service_type: type, implementation: Any = None):
        """
        Register transient service.

        Args:
            service_type: Service interface/type
            implementation: Implementation class or factory (defaults to service_type)
        """
        impl = implementation or service_type
        logger.info(f"Registering transient: {service_type.__name__}")

        self._services[service_type] = ServiceDescriptor(
            service_type=service_type, implementation=impl, lifetime=Lifetime.TRANSIENT
        )

    def register_instance(self, service_type: type, instance: Any):
        """
        Register existing instance as singleton.

        Args:
            service_type: Service type
            instance: Existing instance
        """
        logger.info(f"Registering instance: {service_type.__name__}")

        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation=lambda: instance,
            lifetime=Lifetime.SINGLETON,
            instance=instance,
        )

    async def resolve(self, service_type: type) -> Any:
        """
        Resolve service with automatic dependency injection.

        Args:
            service_type: Type to resolve

        Returns:
            Service instance with all dependencies injected

        Raises:
            ValueError: If service not registered
            CircularDependencyError: If circular dependency detected
        """
        # YOUR CODE HERE
        # [SOLUTION]
        if service_type not in self._services:
            raise ValueError(f"Service {service_type.__name__} not registered")

        descriptor = self._services[service_type]

        # Return cached singleton if available
        if descriptor.lifetime == Lifetime.SINGLETON and descriptor.instance:
            logger.debug(f"Returning cached singleton: {service_type.__name__}")
            return descriptor.instance

        # Check for circular dependency
        if service_type in self._resolving:
            chain = " -> ".join(t.__name__ for t in self._resolving)
            raise CircularDependencyError(
                f"Circular dependency detected: {chain} -> {service_type.__name__}"
            )

        # Mark as resolving
        self._resolving.add(service_type)

        try:
            # Create instance
            instance = await self._create_instance(descriptor)

            # Cache singleton
            if descriptor.lifetime == Lifetime.SINGLETON:
                descriptor.instance = instance

            return instance

        finally:
            # Remove from resolving set
            self._resolving.discard(service_type)
        # [/SOLUTION]

    async def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """
        Create instance with dependency injection.

        Args:
            descriptor: Service descriptor

        Returns:
            Instance with injected dependencies
        """
        # YOUR CODE HERE
        # [SOLUTION]
        implementation = descriptor.implementation

        # Handle factory functions
        if callable(implementation) and not inspect.isclass(implementation):
            logger.debug(f"Creating via factory: {descriptor.service_type.__name__}")
            result = implementation()
            if asyncio.iscoroutine(result):
                result = await result
            return result

        # Handle classes with constructor injection
        logger.debug(f"Creating with constructor injection: {implementation.__name__}")

        # Resolve constructor type hints. typing.get_type_hints resolves
        # forward-reference strings (e.g. `"ServiceB"`) into the actual
        # class objects, which inspect.signature(...).parameters[x].annotation
        # would leave as a raw string and break `await self.resolve(<str>)`.
        try:
            hints = get_type_hints(implementation.__init__)
        except NameError:
            # A forward reference couldn't be resolved at the implementation's
            # module scope. Fall back to walking registered services for a
            # class whose __name__ matches the unresolved string annotation.
            hints = {}

        sig = inspect.signature(implementation.__init__)

        # Resolve constructor parameters
        kwargs = {}
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            # Prefer the resolved hint; fall back to the raw annotation.
            param_type = hints.get(param_name, param.annotation)
            if param_type is inspect.Parameter.empty:
                continue

            # Defensive fallback: if the annotation is still a string, try to
            # match it against a registered service's class name.
            if isinstance(param_type, str):
                matches = [t for t in self._services if t.__name__ == param_type]
                if not matches:
                    raise ValueError(
                        f"Service '{param_type}' not registered "
                        f"(forward reference unresolved)"
                    )
                param_type = matches[0]

            # Resolve dependency
            logger.debug(
                f"Resolving dependency: {param_name} ({param_type.__name__})"
            )
            kwargs[param_name] = await self.resolve(param_type)

        # Create instance
        instance = implementation(**kwargs)

        # Handle async initialization
        if asyncio.iscoroutine(instance):
            instance = await instance

        return instance
        # [/SOLUTION]

    async def dispose(self):
        """
        Dispose all singleton services.

        Calls dispose() or close() methods if available.
        """
        logger.info("Disposing container")

        for service_type, descriptor in self._services.items():
            if descriptor.instance:
                await self._dispose_instance(descriptor.instance, service_type.__name__)

        self._services.clear()

    async def _dispose_instance(self, instance: Any, name: str):
        """Dispose single instance."""
        # Try dispose() method
        if hasattr(instance, "dispose"):
            logger.debug(f"Disposing {name}")
            result = instance.dispose()
            if asyncio.iscoroutine(result):
                await result

        # Try close() method
        elif hasattr(instance, "close"):
            logger.debug(f"Closing {name}")
            result = instance.close()
            if asyncio.iscoroutine(result):
                await result


# Example services demonstrating automatic dependency resolution


class ILogger:
    """Logger interface."""

    def log(self, message: str):
        raise NotImplementedError


class ConsoleLogger(ILogger):
    """Console logger implementation."""

    def __init__(self):
        logger.info("ConsoleLogger created")

    def log(self, message: str):
        print(f"[LOG] {message}")


class IDatabase:
    """Database interface."""

    async def query(self, sql: str):
        raise NotImplementedError


class SqlDatabase(IDatabase):
    """SQL database implementation."""

    def __init__(self, logger: ILogger):
        self.logger = logger
        self.logger.log("SqlDatabase initialized")

    async def query(self, sql: str):
        self.logger.log(f"Executing: {sql}")
        return [{"result": "data"}]

    async def dispose(self):
        self.logger.log("SqlDatabase disposed")


class ICache:
    """Cache interface."""

    async def get(self, key: str):
        raise NotImplementedError


class MemoryCache(ICache):
    """In-memory cache implementation."""

    def __init__(self, logger: ILogger):
        self.logger = logger
        self.cache = {}
        self.logger.log("MemoryCache initialized")

    async def get(self, key: str):
        return self.cache.get(key)

    async def set(self, key: str, value: Any):
        self.cache[key] = value
        self.logger.log(f"Cached: {key}")


class OrderService:
    """
    Order service with automatic dependency injection.

    Dependencies are resolved automatically based on constructor parameters.
    """

    def __init__(self, database: IDatabase, cache: ICache, logger: ILogger):
        self.database = database
        self.cache = cache
        self.logger = logger
        self.logger.log("OrderService initialized")

    async def get_order(self, order_id: str):
        """Get order with caching."""
        # YOUR CODE HERE
        # [SOLUTION]
        # Try cache
        cached = await self.cache.get(order_id)
        if cached:
            self.logger.log(f"Cache hit: {order_id}")
            return cached

        # Query database
        self.logger.log(f"Cache miss: {order_id}")
        result = await self.database.query(
            f"SELECT * FROM orders WHERE id = '{order_id}'"
        )

        # Cache result
        await self.cache.set(order_id, result)

        return result
        # [/SOLUTION]


async def example_usage():
    """Demonstrate automatic dependency resolution."""
    # YOUR CODE HERE
    # [SOLUTION]
    container = IoCContainer()

    # Register services
    # Logger is singleton (reused everywhere)
    container.register_singleton(ILogger, ConsoleLogger)

    # Database is singleton (connection pool)
    container.register_singleton(IDatabase, SqlDatabase)

    # Cache is singleton
    container.register_singleton(ICache, MemoryCache)

    # OrderService is transient (new instance per request)
    container.register_transient(OrderService)

    print("\n=== First Resolution ===")
    # Resolve OrderService - automatically resolves all dependencies
    order_service1 = await container.resolve(OrderService)

    # Use service
    order = await order_service1.get_order("ORD-123")
    print(f"Order: {order}")

    print("\n=== Second Resolution ===")
    # Resolve again - gets new OrderService but same singletons
    order_service2 = await container.resolve(OrderService)

    # Same logger (singleton)
    print(f"Same logger: {order_service1.logger is order_service2.logger}")  # True

    # Same database (singleton)
    print(
        f"Same database: {order_service1.database is order_service2.database}"
    )  # True

    # Different service instance (transient)
    print(f"Same service: {order_service1 is order_service2}")  # False

    # Cleanup
    await container.dispose()
    # [/SOLUTION]


# Test fixtures for circular-dependency detection. Defined at module scope
# (rather than inside the test function) so typing.get_type_hints can
# resolve the `"ServiceB"` forward reference against this module's namespace.
class ServiceA:
    """Test fixture: depends on ServiceB (forward reference)."""

    def __init__(self, service_b: "ServiceB"):
        self.service_b = service_b


class ServiceB:
    """Test fixture: depends on ServiceA — completes the cycle."""

    def __init__(self, service_a: ServiceA):
        self.service_a = service_a


async def test_circular_dependency():
    """Demonstrate circular dependency detection."""
    # YOUR CODE HERE
    # [SOLUTION]
    container = IoCContainer()

    container.register_transient(ServiceA)
    container.register_transient(ServiceB)

    try:
        await container.resolve(ServiceA)
        print("ERROR: Should have detected circular dependency")
    except CircularDependencyError as e:
        print(f"\n✓ Circular dependency detected: {e}")
    # [/SOLUTION]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    print("=" * 80)
    print("IoC Container with Automatic Dependency Resolution")
    print("=" * 80)

    asyncio.run(example_usage())
    asyncio.run(test_circular_dependency())
