"""
Lifecycle Manager
Orchestrates dependency initialization and cleanup
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional
import logging
from dataclasses import dataclass
from config import Settings, load_config
from dependencies import DatabaseClient, CacheClient, HTTPClient

logger = logging.getLogger(__name__)


@dataclass
class ManagedDependencies:
    """
    Container for all managed dependencies.

    Provides access to initialized dependencies with proper lifecycle.
    """

    settings: Settings
    database: DatabaseClient
    cache: CacheClient
    http: HTTPClient

    def get_health_status(self) -> dict:
        """
        Get health status of all dependencies.

        Returns:
            Dictionary with health status
        """
        return {
            "database": self.database.get_stats(),
            "cache": self.cache.get_stats(),
            "http": self.http.get_stats(),
        }


class LifecycleManager:
    """
    Manage dependency lifecycles.

    Handles initialization, operation, and shutdown of all dependencies.
    Ensures proper cleanup even on failures.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize lifecycle manager.

        Args:
            settings: Application settings (loads from env if not provided)
        """
        self.settings = settings or load_config()
        self.dependencies: Optional[ManagedDependencies] = None
        self._initialized = False
        self._shutdown_in_progress = False

    async def initialize(self) -> ManagedDependencies:
        """
        Initialize all dependencies.

        Initializes dependencies in correct order:
        1. Database
        2. Cache
        3. HTTP client

        Returns:
            ManagedDependencies container

        Raises:
            Exception: If any initialization fails
        """
        # YOUR CODE HERE
        # [SOLUTION]
        if self._initialized:
            logger.warning("LifecycleManager already initialized")
            return self.dependencies

        logger.info("=" * 60)
        logger.info("INITIALIZING APPLICATION")
        logger.info("=" * 60)
        logger.info(f"Environment: {self.settings.environment}")
        logger.info(f"Debug: {self.settings.debug}")

        # Track partially initialized dependencies for cleanup
        database = None
        cache = None
        http = None

        try:
            # Create dependency instances
            logger.info("Creating dependency instances...")
            database = DatabaseClient(self.settings)
            cache = CacheClient(self.settings)
            http = HTTPClient(self.settings)

            # Initialize in dependency order
            logger.info("Initializing dependencies...")

            logger.info("  [1/3] Database...")
            await database.initialize()

            logger.info("  [2/3] Cache...")
            await cache.initialize()

            logger.info("  [3/3] HTTP Client...")
            await http.initialize()

            # Create container
            self.dependencies = ManagedDependencies(
                settings=self.settings, database=database, cache=cache, http=http
            )

            self._initialized = True

            logger.info("=" * 60)
            logger.info("APPLICATION INITIALIZED SUCCESSFULLY")
            logger.info("=" * 60)

            return self.dependencies

        except Exception as e:
            logger.error(f"Initialization failed: {e}", exc_info=True)

            # Cleanup partial initialization
            logger.warning("Cleaning up partial initialization...")
            await self._cleanup_dependencies(database, cache, http)

            raise
        # [/SOLUTION]

    async def _cleanup_dependencies(
        self,
        database: Optional[DatabaseClient],
        cache: Optional[CacheClient],
        http: Optional[HTTPClient],
    ):
        """
        Cleanup dependencies during failed initialization.

        Args:
            database: Database client (may be None)
            cache: Cache client (may be None)
            http: HTTP client (may be None)
        """
        errors = []

        # Close in reverse order
        if http:
            try:
                await http.close()
            except Exception as e:
                errors.append(f"HTTP cleanup: {e}")

        if cache:
            try:
                await cache.close()
            except Exception as e:
                errors.append(f"Cache cleanup: {e}")

        if database:
            try:
                await database.close()
            except Exception as e:
                errors.append(f"Database cleanup: {e}")

        if errors:
            logger.warning(f"Cleanup errors: {errors}")

    async def shutdown(self):
        """
        Shutdown all dependencies gracefully.

        Shuts down in reverse initialization order:
        1. HTTP client
        2. Cache
        3. Database

        Continues even if individual shutdowns fail.
        """
        # YOUR CODE HERE
        # [SOLUTION]
        if not self._initialized:
            logger.debug("LifecycleManager not initialized, nothing to shutdown")
            return

        if self._shutdown_in_progress:
            logger.warning("Shutdown already in progress")
            return

        self._shutdown_in_progress = True

        logger.info("=" * 60)
        logger.info("SHUTTING DOWN APPLICATION")
        logger.info("=" * 60)

        errors = []

        try:
            if self.dependencies:
                # Shutdown in reverse order
                logger.info("Shutting down dependencies...")

                logger.info("  [1/3] HTTP Client...")
                if self.dependencies.http:
                    try:
                        await self.dependencies.http.close()
                    except Exception as e:
                        logger.error(f"HTTP client shutdown error: {e}")
                        errors.append(f"HTTP client: {e}")

                logger.info("  [2/3] Cache...")
                if self.dependencies.cache:
                    try:
                        await self.dependencies.cache.close()
                    except Exception as e:
                        logger.error(f"Cache shutdown error: {e}")
                        errors.append(f"Cache: {e}")

                logger.info("  [3/3] Database...")
                if self.dependencies.database:
                    try:
                        await self.dependencies.database.close()
                    except Exception as e:
                        logger.error(f"Database shutdown error: {e}")
                        errors.append(f"Database: {e}")

        except Exception as e:
            logger.error(f"Unexpected shutdown error: {e}", exc_info=True)
            errors.append(f"Unexpected: {e}")

        finally:
            self._initialized = False
            self._shutdown_in_progress = False
            self.dependencies = None

            if errors:
                logger.warning("=" * 60)
                logger.warning(f"SHUTDOWN COMPLETED WITH ERRORS: {len(errors)}")
                for error in errors:
                    logger.warning(f"  - {error}")
                logger.warning("=" * 60)
            else:
                logger.info("=" * 60)
                logger.info("APPLICATION SHUTDOWN SUCCESSFULLY")
                logger.info("=" * 60)
        # [/SOLUTION]

    @asynccontextmanager
    async def lifespan(self) -> AsyncIterator[ManagedDependencies]:
        """
        Context manager for automatic lifecycle management.

        Usage:
            async with manager.lifespan() as deps:
                # Use dependencies
                result = await deps.database.query(...)

        Yields:
            ManagedDependencies container
        """
        try:
            deps = await self.initialize()
            yield deps
        finally:
            await self.shutdown()

    def is_initialized(self) -> bool:
        """Check if manager is initialized."""
        return self._initialized

    async def health_check(self) -> dict:
        """
        Perform health check on all dependencies.

        Returns:
            Health status dictionary
        """
        if not self._initialized:
            return {"status": "not_initialized", "healthy": False}

        try:
            # Check each dependency
            checks = {}

            # Database check
            try:
                await self.dependencies.database.query("SELECT 1")
                checks["database"] = {"healthy": True, "message": "OK"}
            except Exception as e:
                checks["database"] = {"healthy": False, "message": str(e)}

            # Cache check
            try:
                await self.dependencies.cache.set("_health_", "ok", ttl=10)
                val = await self.dependencies.cache.get("_health_")
                checks["cache"] = {
                    "healthy": val == "ok",
                    "message": "OK" if val == "ok" else "Failed",
                }
            except Exception as e:
                checks["cache"] = {"healthy": False, "message": str(e)}

            # HTTP check (just verify client exists)
            checks["http"] = {
                "healthy": self.dependencies.http._initialized,
                "message": (
                    "OK" if self.dependencies.http._initialized else "Not initialized"
                ),
            }

            # Overall health
            all_healthy = all(check["healthy"] for check in checks.values())

            return {
                "status": "healthy" if all_healthy else "degraded",
                "healthy": all_healthy,
                "checks": checks,
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "healthy": False, "error": str(e)}


# Example usage
async def main():
    """Example application with lifecycle management."""
    manager = LifecycleManager()

    try:
        # Use context manager for automatic lifecycle
        async with manager.lifespan() as deps:
            logger.info("")
            logger.info("Application running...")
            logger.info("")

            # Use dependencies
            logger.info("Querying database...")
            result = await deps.database.query("SELECT * FROM orders LIMIT 5")
            logger.info(f"Query result: {result}")

            logger.info("Using cache...")
            await deps.cache.set("test_key", {"data": "value"})
            cached = await deps.cache.get("test_key")
            logger.info(f"Cache result: {cached}")

            # Check health
            logger.info("Performing health check...")
            health = await manager.health_check()
            logger.info(f"Health status: {health['status']}")

            # Simulate some work
            import asyncio

            await asyncio.sleep(1)

            logger.info("")
            logger.info("Application work complete")
            logger.info("")

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise


async def example_with_failure():
    """Example showing cleanup on failure."""
    manager = LifecycleManager()

    try:
        async with manager.lifespan() as deps:
            logger.info("Working...")

            # Simulate failure
            raise RuntimeError("Simulated application error")

    except RuntimeError:
        logger.warning("Application failed, but cleanup still happened!")


if __name__ == "__main__":
    import asyncio

    print("\n" + "=" * 60)
    print("LIFECYCLE MANAGER EXAMPLE")
    print("=" * 60 + "\n")

    # Run normal example
    asyncio.run(main())

    print("\n" + "=" * 60)
    print("FAILURE EXAMPLE")
    print("=" * 60 + "\n")

    # Run failure example
    asyncio.run(example_with_failure())
