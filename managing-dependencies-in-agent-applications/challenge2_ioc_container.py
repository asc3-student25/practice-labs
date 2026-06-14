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
        self._resolution_path: list[type] = []  # For cycle path reporting

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
        if service_type not in self._services:
            raise ValueError(f"Service not registered: {service_type.__name__}")

        descriptor = self._services[service_type]

        if (
            descriptor.lifetime == Lifetime.SINGLETON
            and descriptor.instance is not None
        ):
            return descriptor.instance

        if service_type in self._resolving:
            chain = " -> ".join(
                [t.__name__ for t in self._resolution_path + [service_type]]
            )
            raise CircularDependencyError(f"Circular dependency detected: {chain}")

        self._resolving.add(service_type)
        self._resolution_path.append(service_type)
        try:
            instance = await self._create_instance(descriptor)
            if descriptor.lifetime == Lifetime.SINGLETON:
                descriptor.instance = instance
            return instance
        finally:
            self._resolving.discard(service_type)
            if self._resolution_path and self._resolution_path[-1] is service_type:
                self._resolution_path.pop()
            elif service_type in self._resolution_path:
                self._resolution_path.remove(service_type)

    async def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """
        Create instance with dependency injection.

        Args:
            descriptor: Service descriptor

        Returns:
            Instance with injected dependencies
        """
        implementation = descriptor.implementation

        # Factory function (callable but not a class)
        if callable(implementation) and not inspect.isclass(implementation):
            result = implementation()
            if asyncio.iscoroutine(result):
                result = await result
            return result

        # Class constructor injection
        constructor = implementation.__init__
        signature = inspect.signature(constructor)
        type_hints = get_type_hints(constructor)
        kwargs = {}

        for name, param in signature.parameters.items():
            if name == "self":
                continue

            annotation = type_hints.get(name, param.annotation)
            if annotation is not inspect.Parameter.empty:
                kwargs[name] = await self.resolve(annotation)

        return implementation(**kwargs)

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
        cached_order = await self.cache.get(order_id)
        if cached_order is not None:
            return cached_order

        result = await self.database.query(
            f"SELECT * FROM orders WHERE order_id = '{order_id}'"
        )
        await self.cache.set(order_id, result)
        return result


async def example_usage():
    """Demonstrate automatic dependency resolution."""
    container = IoCContainer()
    container.register_singleton(ILogger, ConsoleLogger)
    container.register_singleton(IDatabase, SqlDatabase)
    container.register_singleton(ICache, MemoryCache)
    container.register_transient(OrderService)

    service1 = await container.resolve(OrderService)
    service2 = await container.resolve(OrderService)

    print(f"logger same: {service1.logger is service2.logger}")
    print(f"database same: {service1.database is service2.database}")
    print(f"service same: {service1 is service2}")

    await container.dispose()


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
    container = IoCContainer()
    container.register_transient(ServiceA)
    container.register_transient(ServiceB)

    try:
        await container.resolve(ServiceA)
    except CircularDependencyError as e:
        print(f"Circular dependency detected successfully: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    print("=" * 80)
    print("IoC Container with Automatic Dependency Resolution")
    print("=" * 80)

    asyncio.run(example_usage())
    asyncio.run(test_circular_dependency())
