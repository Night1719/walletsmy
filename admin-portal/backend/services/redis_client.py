"""
Настройка Redis клиента для кэширования и очередей
"""
import redis.asyncio as redis
import json
from typing import Any, Optional
import os

# Настройки Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Глобальный клиент Redis
redis_client: Optional[redis.Redis] = None


async def init_redis():
    """Инициализация Redis клиента"""
    global redis_client
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)


async def get_redis() -> redis.Redis:
    """Получение Redis клиента"""
    if redis_client is None:
        await init_redis()
    return redis_client


async def cache_set(key: str, value: Any, expire: int = 3600):
    """Установка значения в кэш"""
    redis = await get_redis()
    await redis.setex(key, expire, json.dumps(value))


async def cache_get(key: str) -> Optional[Any]:
    """Получение значения из кэша"""
    redis = await get_redis()
    value = await redis.get(key)
    if value:
        return json.loads(value)
    return None


async def cache_delete(key: str):
    """Удаление значения из кэша"""
    redis = await get_redis()
    await redis.delete(key)


async def publish_message(channel: str, message: Any):
    """Публикация сообщения в канал"""
    redis = await get_redis()
    await redis.publish(channel, json.dumps(message))