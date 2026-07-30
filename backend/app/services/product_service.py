"""商品业务服务层。

封装对 Product 表的 CRUD，并在写操作后触发 Celery 索引任务，
保持 MySQL 与 Chroma 向量库的一致性。

为避免循环导入，Celery task 采用函数内懒加载导入。
"""
from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


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
    """创建商品，并触发向量化索引任务。"""
    product = Product(**data.model_dump())
    session.add(product)
    await session.commit()
    await session.refresh(product)

    _trigger_index(product.id, "upsert")
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

    _trigger_index(product.id, "upsert")
    return product


async def delete_product(session: AsyncSession, pid: int) -> bool:
    """删除商品，并删除对应向量。返回是否删除成功。"""
    product = await get_product(session, pid)
    if product is None:
        return False

    await session.delete(product)
    await session.commit()

    _trigger_index(pid, "delete")
    return True


def _trigger_index(product_id: int, action: str) -> None:
    """触发 Celery 索引任务（懒导入，避免循环依赖与无 broker 时硬失败）。"""
    try:
        from app.tasks.indexing import update_product_index

        update_product_index.delay(product_id, action)
    except Exception:
        # 任务派发失败不应影响主流程（例如无 Redis 时仍保证 DB 写入成功）
        # 生产环境可改为日志记录告警
        import logging

        logging.getLogger(__name__).warning(
            "派发索引任务失败 product_id=%s action=%s", product_id, action, exc_info=True
        )
