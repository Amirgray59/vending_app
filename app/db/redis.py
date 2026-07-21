"""
Redis async client (used for caching, pub/sub, session state).

The client is created lazily and closed on application shutdown.
"""

from __future__ import annotations

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

_redis_client: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    """Return a process-wide async Redis client (creates it if missing)."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.Redis_url(),
            encoding="utf-8",
            decode_responses=True,
            health_check_interval=30,
        )
    return _redis_client


async def close_redis() -> None:
    """Close the shared Redis client (call at shutdown)."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


async def check_redis_connection() -> bool:
    """Ping Redis for /health endpoint."""
    try:
        client = get_redis()
        pong = await client.ping()
        return bool(pong)
    except Exception as exc:  # pragma: no cover
        logger.error("redis_connection_failed", err=str(exc))
        return False
