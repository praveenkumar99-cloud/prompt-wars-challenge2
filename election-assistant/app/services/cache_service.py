"""Module: cache_service.py
Description: Redis caching layer for high-performance data retrieval.
Author: Praveen Kumar
"""
import json
import logging
from typing import Any, Optional

from ..config import config
from ..constants import (
    CACHE_KEY_INTENT,
    CACHE_KEY_SESSION,
    CACHE_KEY_TIMELINE,
    CACHE_TTL_LONG,
    CACHE_TTL_MEDIUM,
    CACHE_TTL_SHORT,
)

logger = logging.getLogger(__name__)


class CacheService:
    """Service for caching operations using Redis."""

    def __init__(self) -> None:
        """Initialize CacheService with lazy Redis connection."""
        self._redis: Optional[object] = None
        self._initialized: bool = False

    def _get_redis_client(self) -> Optional[object]:
        """Get or create Redis client.

        Returns:
            Redis client instance or None if disabled/failed.
        """
        if self._initialized:
            return self._redis

        if not config.ENABLE_REDIS_CACHE:
            self._initialized = True
            return None

        try:
            import redis

            self._redis = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                password=config.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            # Test connection
            self._redis.ping()
            logger.info("Redis cache initialized successfully")
            self._initialized = True
            return self._redis
        except Exception as e:
            logger.warning("Redis initialization failed, cache disabled: %s", e)
            self._initialized = True
            return None

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache.

        Args:
            key: Cache key.

        Returns:
            Cached value or None if not found/expired.
        """
        try:
            client = self._get_redis_client()
            if not client:
                return None

            value = client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning("Cache get failed for key %s: %s", key, e)
            return None

    def set(self, key: str, value: Any, ttl: int = CACHE_TTL_MEDIUM) -> bool:
        """Store value in cache.

        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time-to-live in seconds.

        Returns:
            True if successful, False otherwise.
        """
        try:
            client = self._get_redis_client()
            if not client:
                return False

            client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.warning("Cache set failed for key %s: %s", key, e)
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key.

        Returns:
            True if successful, False otherwise.
        """
        try:
            client = self._get_redis_client()
            if not client:
                return False

            client.delete(key)
            return True
        except Exception as e:
            logger.warning("Cache delete failed for key %s: %s", key, e)
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern.

        Args:
            pattern: Redis key pattern (e.g., "session:*").

        Returns:
            Number of keys deleted.
        """
        try:
            client = self._get_redis_client()
            if not client:
                return 0

            keys = client.keys(pattern)
            if keys:
                return client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning("Cache pattern delete failed: %s", e)
            return 0

    def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve session data from cache.

        Args:
            session_id: Session identifier.

        Returns:
            Cached session data or None.
        """
        return self.get(CACHE_KEY_SESSION % session_id)

    def set_session(self, session_id: str, data: dict) -> bool:
        """Store session data in cache.

        Args:
            session_id: Session identifier.
            data: Session data.

        Returns:
            True if successful.
        """
        return self.set(
            CACHE_KEY_SESSION % session_id, data, CACHE_TTL_LONG
        )

    def get_intent_result(self, message_hash: str) -> Optional[tuple]:
        """Retrieve cached intent classification.

        Args:
            message_hash: Hash of the message.

        Returns:
            Cached (intent, confidence) tuple or None.
        """
        return self.get(CACHE_KEY_INTENT % message_hash)

    def set_intent_result(
        self, message_hash: str, intent: str, confidence: float
    ) -> bool:
        """Cache intent classification result.

        Args:
            message_hash: Hash of the message.
            intent: Classified intent.
            confidence: Confidence score.

        Returns:
            True if successful.
        """
        return self.set(
            CACHE_KEY_INTENT % message_hash,
            {"intent": intent, "confidence": confidence},
            CACHE_TTL_MEDIUM,
        )

    def get_timeline(self) -> Optional[dict]:
        """Retrieve cached timeline data.

        Returns:
            Cached timeline or None.
        """
        return self.get(CACHE_KEY_TIMELINE)

    def set_timeline(self, timeline_data: dict) -> bool:
        """Cache timeline data.

        Args:
            timeline_data: Timeline information.

        Returns:
            True if successful.
        """
        return self.set(CACHE_KEY_TIMELINE, timeline_data, CACHE_TTL_LONG)

    def health_check(self) -> bool:
        """Check Redis connection health.

        Returns:
            True if Redis is available, False otherwise.
        """
        try:
            client = self._get_redis_client()
            if not client:
                return False
            client.ping()
            return True
        except Exception as e:
            logger.warning("Redis health check failed: %s", e)
            return False
