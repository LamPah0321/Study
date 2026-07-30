"""v1 路由聚合。

将各业务子路由统一挂载到一个 APIRouter 上，由 main.py 以 /api/v1 前缀引入。
"""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import cart, chat, products, search

router = APIRouter()
router.include_router(products.router)
router.include_router(search.router)
router.include_router(chat.router)
router.include_router(cart.router)
