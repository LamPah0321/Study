"""异步数据库引擎与会话工厂。

使用 SQLAlchemy 2.0 异步风格 + aiomysql 驱动。
"""
from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# 异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """所有 ORM 模型的声明基类。"""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：提供一个异步数据库会话，请求结束自动关闭。"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """启动时创建所有表（开发用；生产建议用 alembic 迁移）。"""
    # 显式导入模型，确保元数据被注册
    from app.models import product, order  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
