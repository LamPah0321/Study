"""Chroma 向量库客户端（单例）。

注意：Chroma SDK 是同步的，所有对集合的读写操作都需要调用方
使用 asyncio.to_thread(...) 包裹，避免阻塞事件循环。
"""
from __future__ import annotations

import threading
from typing import Optional

import chromadb
from chromadb.api.models.Collection import Collection

from app.core.config import settings

_client = None
_collection: Optional[Collection] = None
_lock = threading.Lock()


def _get_client():
    """获取（或创建）Chroma PersistentClient 单例。"""
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                _client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
    return _client


def get_chroma_collection() -> Collection:
    """获取指定的 collection，不存在则创建。

    该函数本身是同步的，调用方需自行用 asyncio.to_thread 包裹。
    """
    global _collection
    if _collection is None:
        with _lock:
            if _collection is None:
                client = _get_client()
                _collection = client.get_or_create_collection(
                    name=settings.CHROMA_COLLECTION,
                    metadata={"hnsw:space": "cosine"},
                )
    return _collection


def reset_chroma() -> None:
    """重置单例（主要用于测试）。"""
    global _client, _collection
    with _lock:
        _client = None
        _collection = None
