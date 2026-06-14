"""
Challenge 2: Graceful Shutdown
Graceful shutdown with timeout for in-flight requests
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from lifecycle_manager import LifecycleManager

logger = logging.getLogger(__name__)


@dataclass
class ShutdownConfig:
    """Configuration for graceful shutdown."""

    grace_period_seconds: float = 30.0  # Grace period for in-flight requests
    force_shutdown_seconds: float = 60.0  # Max time before forcing shutdown
    polling_interval_seconds: float = 0.5  # How often to check for completion


class GracefulShutdownManager:
    """
    Manages graceful shutdown with timeout.

    Features:
    - Tracks active requests
    - Waits for completion with timeout
    - Rejects new requests during shutdown
    - Forces shutdown if grace period expires
    """

    def __init__(
        self,
        lifecycle_manager: LifecycleManager,
        config: Optional[ShutdownConfig] = None,
    ):
        """
        Initialize graceful shutdown manager.

        Args:
            lifecycle_manager: Application lifecycle manager
            config: Shutdown configuration
        """
        self.lifecycle_manager = lifecycle_manager
        self.config = config or ShutdownConfig()

        self._active_requests = 0
        self._shutdown_initiated = False
        self._shutdown_complete = False
        self._lock = asyncio.Lock()

    async def increment_active_requests(self):
        """
        Increment active request counter.

        Raises:
            RuntimeError: If shutdown is in progress
        """
        async with self._lock:
            if self._shutdown_initiated:
                raise RuntimeError("Shutdown in progress, rejecting new requests")

            self._active_requests += 1
            logger.debug(f"Active requests: {self._active_requests}")

    async def decrement_active_requests(self):
        """Decrement active request counter."""
        async with self._lock:
            self._active_requests = max(0, self._active_requests - 1)
            logger.debug(f"Active requests: {self._active_requests}")

    def get_active_requests(self) -> int:
        """Get number of active requests."""
        return self._active_requests

    def is_shutdown_initiated(self) -> bool:
        """Check if shutdown has been initiated."""
        return self._shutdown_initiated

    async def shutdown(self):
        """
        Perform graceful shutdown.

        1. Mark shutdown as initiated (reject new requests)
        2. Wait for active requests to complete (with grace period)
        3. If timeout expires, force shutdown
        4. Clean up all dependencies
        """
        if self._shutdown_complete:
            return

        logger.info("=" * 60)
        logger.info("GRACEFUL SHUTDOWN STARTING")
        logger.info("=" * 60)

        async with self._lock:
            self._shutdown_initiated = True

        if self.get_active_requests() > 0:
            await self._wait_for_requests()

        await self.lifecycle_manager.shutdown()

        self._shutdown_complete = True
        logger.info("=" * 60)
        logger.info("GRACEFUL SHUTDOWN COMPLETE")
        logger.info("=" * 60)

    async def _wait_for_requests(self):
        """
        Wait for active requests to complete.

        Polls active request counter and waits up to grace period.
        If grace period expires, logs warning and proceeds.
        """
        loop = asyncio.get_event_loop()
        deadline = loop.time() + self.config.grace_period_seconds

        while True:
            active_requests = self.get_active_requests()

            if active_requests == 0:
                logger.info("All in-flight requests completed")
                break

            if loop.time() >= deadline:
                logger.warning(
                    "Grace period expired with %s active request(s), forcing shutdown",
                    active_requests,
                )
                break

            logger.info("Waiting for %s active request(s) to complete...", active_requests)
            await asyncio.sleep(self.config.polling_interval_seconds)

    async def handle_request(self, request_handler):
        """
        Context manager for handling requests with tracking.

        Usage:
            async with shutdown_manager.handle_request(handler):
                result = await handler()

        Args:
            request_handler: Async function to handle request

        Raises:
            RuntimeError: If shutdown is in progress
        """
        await self.increment_active_requests()
        try:
            return await request_handler()
        finally:
            await self.decrement_active_requests()


# Example usage with FastAPI
def create_app_with_graceful_shutdown():
    """Example FastAPI app with graceful shutdown."""
    from fastapi import FastAPI, HTTPException
    from contextlib import asynccontextmanager

    # Global instances
    lifecycle_manager = LifecycleManager()
    shutdown_manager = None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan with graceful shutdown."""
        nonlocal shutdown_manager

        # Startup
        await lifecycle_manager.initialize()

        shutdown_config = ShutdownConfig(
            grace_period_seconds=30.0, polling_interval_seconds=0.5
        )
        shutdown_manager = GracefulShutdownManager(lifecycle_manager, shutdown_config)

        logger.info("Application started")

        yield

        # Shutdown
        await shutdown_manager.shutdown()

    app = FastAPI(lifespan=lifespan)

    @app.get("/")
    async def root():
        """Root endpoint."""
        if shutdown_manager.is_shutdown_initiated():
            raise HTTPException(status_code=503, detail="Service shutting down")

        return {"status": "running"}

    @app.get("/slow")
    async def slow_endpoint():
        """Slow endpoint to test graceful shutdown."""
        if shutdown_manager.is_shutdown_initiated():
            raise HTTPException(status_code=503, detail="Service shutting down")

        await shutdown_manager.increment_active_requests()

        try:
            # Simulate slow operation
            await asyncio.sleep(5)
            return {"result": "completed"}
        finally:
            await shutdown_manager.decrement_active_requests()

    @app.get("/status")
    async def status():
        """Get application status."""
        return {
            "active_requests": shutdown_manager.get_active_requests(),
            "shutdown_initiated": shutdown_manager.is_shutdown_initiated(),
        }

    return app


# Standalone example
async def example_graceful_shutdown():
    """Example showing graceful shutdown with active requests."""
    lifecycle_manager = LifecycleManager()
    await lifecycle_manager.initialize()

    shutdown_config = ShutdownConfig(grace_period_seconds=3.0, polling_interval_seconds=0.5)
    shutdown_manager = GracefulShutdownManager(lifecycle_manager, shutdown_config)

    async def simulated_request(name: str, duration: float):
        await shutdown_manager.increment_active_requests()
        logger.info("%s started (duration=%ss)", name, duration)
        try:
            await asyncio.sleep(duration)
            logger.info("%s completed", name)
        except asyncio.CancelledError:
            logger.info("%s cancelled", name)
            raise
        finally:
            await shutdown_manager.decrement_active_requests()

    tasks = [
        asyncio.create_task(simulated_request("request-1", 1.0)),
        asyncio.create_task(simulated_request("request-2", 2.5)),
        asyncio.create_task(simulated_request("request-3", 8.0)),
    ]

    await asyncio.sleep(0.2)
    await shutdown_manager.shutdown()

    for task in tasks:
        if not task.done():
            task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    import asyncio

    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    print("\n" + "=" * 60)
    print("GRACEFUL SHUTDOWN EXAMPLE")
    print("=" * 60 + "\n")

    asyncio.run(example_graceful_shutdown())
