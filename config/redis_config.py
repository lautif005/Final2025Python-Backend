"""
Redis Configuration Module

Provides Redis client connection and configuration for caching,
sessions, and rate limiting.
"""
import os
import logging
from typing import Optional
import redis
from redis.connection import ConnectionPool

logger = logging.getLogger(__name__)


class RedisConfig:
    """
    Singleton Redis configuration class

    Manages Redis connection pool and provides a single client instance
    across the application.
    """

    _instance: Optional['RedisConfig'] = None
    _client: Optional[redis.Redis] = None
    _pool: Optional[ConnectionPool] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._initialize_client()

    def _initialize_client(self):
        """Initialize Redis client with connection pool"""
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        max_connections = int(os.getenv('REDIS_MAX_CONNECTIONS', '50'))

        try:
            # Create connection pool
            self._client = redis.from_url(
                redis_url,
                max_connections=max_connections,
                decode_responses=True,  # Auto-decode bytes to str
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )

            self._pool = self._client.connection_pool

            # Test connection
            self._client.ping()
            logger.info(f"✅ Redis connected successfully using URL: {redis_url}")

        except redis.ConnectionError as e:
            logger.warning(f"⚠️  Redis connection failed: {e}")
            logger.warning("Application will run without caching")
            self._client = None
        except Exception as e:
            logger.error(f"❌ Redis initialization error: {e}")
            self._client = None

    def get_client(self) -> Optional[redis.Redis]:
        """
        Get Redis client instance

        Returns:
            Redis client or None if connection failed
        """
        return self._client

    def is_available(self) -> bool:
        """
        Check if Redis is available

        Returns:
            True if Redis is connected and responsive
        """
        if self._client is None:
            return False

        try:
            return self._client.ping()
        except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
            logger.debug(f"Redis ping failed: {e}")
            return False

    def close(self):
        """Close Redis connection and pool"""
        # Elimina la llamada a self._client.close()
        
        # Desconecta el pool, que es la acción funcional de cerrar conexiones.
        if self._pool:
            self._pool.disconnect()
            logger.info("Redis connection pool disconnected")
            self._pool = None  # Limpiamos la referencia del pool

        # Luego limpiamos la referencia del cliente.
        if self._client:
            self._client = None
            logger.info("Redis client instance marked as closed")


# Global Redis instance
redis_config = RedisConfig()


def get_redis_client() -> Optional[redis.Redis]:
    """
    Dependency injection function for FastAPI

    Returns:
        Redis client instance or None
    """
    return redis_config.get_client()


def check_redis_connection() -> bool:
    """
    Check if Redis is available

    Returns:
        True if Redis is connected
    """
    return redis_config.is_available()