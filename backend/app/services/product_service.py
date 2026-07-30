"""商品业务服务层。

封装对 Product 表的 CRUD，并在写操作后同步向量索引到 Chroma，
保持 MySQL 与 Chroma 向量库的一致性。

索引同步采用直接异步调用 rag_service（无需 Redis/Celery）。
若部署了 Redis + Celery，也可改用 tasks.indexing.update_product_index.delay 异步派发。
"""
from __future__ import annotations

import logging
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

logger = logging.getLogger(__name__)


async def list_products(
    session: AsyncSession,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> Sequence[Product]:
    """分页查询商品，可按分类过滤。"""
    stmt = select(Product).offset(skip).limit(limit).order_by(Product.id.desc())
    if category:
        stmt = stmt.where(Product.category == category)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_product(session: AsyncSession, pid: int) -> Optional[Product]:
    """根据 ID 获取单个商品。"""
    result = await session.execute(select(Product).where(Product.id == pid))
    return result.scalar_one_or_none()


async def create_product(session: AsyncSession, data: ProductCreate) -> Product:
    """创建商品，并同步向量索引。"""
    product = Product(**data.model_dump())
    session.add(product)
    await session.commit()
    await session.refresh(product)

    await _sync_index(product, "upsert")
    return product


async def update_product(session: AsyncSession, pid: int, data: ProductUpdate) -> Optional[Product]:
    """更新商品，并刷新向量索引。"""
    product = await get_product(session, pid)
    if product is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    await session.commit()
    await session.refresh(product)

    await _sync_index(product, "upsert")
    return product


async def delete_product(session: AsyncSession, pid: int) -> bool:
    """删除商品，并删除对应向量。返回是否删除成功。"""
    product = await get_product(session, pid)
    if product is None:
        return False

    await session.delete(product)
    await session.commit()

    await _sync_index(product, "delete")
    return True


async def _sync_index(product: Product, action: str) -> None:
    """直接调用 rag_service 同步向量索引（无需 Redis/Celery）。

    失败时仅记录日志，不影响主业务流程（DB 写入已成功）。
    """
    try:
        from app.services import rag_service

        if action == "delete":
            await rag_service.delete_product_embedding(product.id)
        else:
            text = f"{product.name or ''} {product.category or ''} {product.description or ''}".strip()
            if text:
                await rag_service.upsert_product_embedding(product.id, text)
    except Exception:
        logger.warning(
            "同步向量索引失败 product_id=%s action=%s（不影响 DB 写入）",
            getattr(product, "id", "?"),
            action,
            exc_info=True,
        )
