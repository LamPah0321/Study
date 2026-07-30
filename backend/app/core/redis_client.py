"""异步 Redis 客户端。

使用 redis.asyncio 模块。懒加载，应用启动时初始化，关闭时释放。
"""
from __future__ import annotations

from typing import Optional

import redis.asyncio as redis

from app.core.config import settings

_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """获取全局 Redis 客户端（懒加载）。"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis() -> None:
    """应用关闭时关闭 Redis 连接。"""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
