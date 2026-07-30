"""搜索相关 schema。"""
from __future__ import annotations

from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="用户搜索关键词或自然语言问题")
    top_k: int = Field(5, ge=1, le=20, description="召回商品数量")


class SearchProductOut(BaseModel):
    """搜索结果中的单个商品简要信息。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str = ""
    price: Decimal
    category: str = ""
    image: str = ""
    stock: int = 0


class SearchResponse(BaseModel):
    """语义搜索响应：包含 AI 推荐语与候选商品列表。"""
    ai_summary: str
    products: List[SearchProductOut] = []
