"""FastAPI 应用入口。

负责：
- 创建 FastAPI 应用
- 配置 CORS
- 挂载 v1 路由（前缀 /api/v1）
- 启动时初始化数据库表与 Chroma collection
- 关闭时释放 Redis 连接
- 健康检查接口
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.database import init_db
from app.core.redis_client import close_redis, get_redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动与关闭钩子。"""
    # ---- 启动 ----
    logger.info("AI Mall 启动中...")
    try:
        await init_db()
        logger.info("数据库表已就绪")
    except Exception:
        logger.warning("启动时创建数据库表失败（可能是数据库尚未就绪）", exc_info=True)

    try:
        # 初始化 Redis 连接（懒加载触发）
        await get_redis()
        logger.info("Redis 已连接")
    except Exception:
        logger.warning("启动时连接 Redis 失败", exc_info=True)

    # 初始化 Chroma collection（同步，放入线程）
    try:
        import asyncio

        from app.core.chroma_client import get_chroma_collection

        await asyncio.to_thread(get_chroma_collection)
        logger.info("Chroma collection 已就绪")
    except Exception:
        logger.warning("启动时初始化 Chroma 失败", exc_info=True)

    yield

    # ---- 关闭 ----
    logger.info("AI Mall 关闭中...")
    await close_redis()
    logger.info("已关闭 Redis 连接")


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="智能商城后端：商品 CRUD、语义搜索 RAG、AI 流式对话、购物车",
    lifespan=lifespan,
)

# CORS（开发期允许配置中的来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载 v1 路由
app.include_router(v1_router, prefix="/api/v1")


@app.get("/", tags=["健康检查"], summary="健康检查")
async def root() -> dict:
    return {"status": "ok"}
