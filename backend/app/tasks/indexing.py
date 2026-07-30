"""Celery 索引任务：将商品同步到 Chroma 向量库。

Celery 任务是同步函数，内部通过 asyncio.run(...) 执行异步的
rag_service 函数与异步 DB 会话。
"""
from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select

from app.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.product import Product
from app.services import rag_service

logger = logging.getLogger(__name__)


async def _fetch_product_text(product_id: int) -> str | None:
    """异步从 MySQL 读取商品，返回用于 embedding 的拼接文本。"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if product is None:
            return None
        # 拼接名称与描述作为向量文本
        name = product.name or ""
        description = product.description or ""
        category = product.category or ""
        return f"{name} {category} {description}".strip()


async def _do_upsert(product_id: int) -> None:
    text = await _fetch_product_text(product_id)
    if not text:
        logger.warning("商品 %s 不存在或文本为空，跳过索引", product_id)
        return
    await rag_service.upsert_product_embedding(product_id, text)


async def _do_delete(product_id: int) -> None:
    await rag_service.delete_product_embedding(product_id)


def _run(coro):
    """在新事件循环中运行协程（Celery worker 进程无运行中循环）。"""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, name="app.tasks.indexing.update_product_index")
def update_product_index(self, product_id: int, action: str = "upsert") -> None:
    """同步商品向量索引。

    action:
        - "upsert": 读取商品并写入/更新向量
        - "delete": 删除对应向量
    失败时按 5 秒间隔重试，最多 3 次。
    """
    try:
        logger.info("开始处理索引任务 product_id=%s action=%s", product_id, action)
        if action == "delete":
            _run(_do_delete(product_id))
        else:
            _run(_do_upsert(product_id))
        logger.info("索引任务完成 product_id=%s action=%s", product_id, action)
    except Exception as exc:
        logger.error("索引任务失败 product_id=%s action=%s: %s", product_id, action, exc, exc_info=True)
        try:
            self.retry(exc=exc, countdown=5)
        except self.MaxRetriesExceededError:
            logger.error("索引任务重试次数耗尽 product_id=%s action=%s", product_id, action)
