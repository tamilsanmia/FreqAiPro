import redis
import json
import logging

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_DECODE_RESPONSES = True

# Initialize Redis client
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=REDIS_DECODE_RESPONSES
    )
    redis_client.ping()
    logger.info("Redis connected successfully")
except redis.ConnectionError:
    logger.warning("Redis connection failed, running without cache")
    redis_client = None

def cache_signals(signals, signal_type):
    """Cache signals in Redis"""
    if redis_client:
        try:
            key = f"signals:{signal_type}"
            redis_client.setex(key, 300, json.dumps(signals))  # Cache for 5 minutes
        except Exception as e:
            logger.error(f"Error caching signals: {e}")

def get_cached_signals(signal_type):
    """Get cached signals from Redis"""
    if redis_client:
        try:
            key = f"signals:{signal_type}"
            data = redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Error getting cached signals: {e}")
    return None

def cache_scanned_coins(coins):
    """Cache scanned coins in Redis"""
    if redis_client:
        try:
            redis_client.setex("scanned_coins", 300, json.dumps(coins))  # Cache for 5 minutes
        except Exception as e:
            logger.error(f"Error caching scanned coins: {e}")

def get_cached_scanned_coins():
    """Get cached scanned coins from Redis"""
    if redis_client:
        try:
            data = redis_client.get("scanned_coins")
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Error getting cached scanned coins: {e}")
    return None

def cache_positions(positions, position_type):
    """Cache positions in Redis"""
    if redis_client:
        try:
            key = f"positions:{position_type}"
            redis_client.setex(key, 60, json.dumps(positions))  # Cache for 1 minute
        except Exception as e:
            logger.error(f"Error caching positions: {e}")

def get_cached_positions(position_type):
    """Get cached positions from Redis"""
    if redis_client:
        try:
            key = f"positions:{position_type}"
            data = redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Error getting cached positions: {e}")
    return None

def invalidate_cache():
    """Invalidate all cache"""
    if redis_client:
        try:
            redis_client.flushdb()
            logger.info("Cache invalidated")
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
