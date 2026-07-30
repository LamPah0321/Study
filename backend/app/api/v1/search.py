"""智能语义搜索接口（RAG）。"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.product import Product
from app.schemas.search import SearchProductOut, SearchRequest, SearchResponse
from app.services import rag_service

router = APIRouter(prefix="/search", tags=["智能搜索"])


@router.post("/semantic", response_model=SearchResponse, summary="语义搜索商品")
async def semantic_search(
    req: SearchRequest, session: AsyncSession = Depends(get_db)
) -> SearchResponse:
    try:
        # 1. 向量检索相关商品 ID
        product_ids = await rag_service.retrieve_products(req.query, top_k=req.top_k)

        # 2. 未找到任何商品
        if not product_ids:
            return SearchResponse(ai_summary="未找到相关商品", products=[])

        # 3. 从 MySQL 查询这些商品（保持 id 顺序）
        result = await session.execute(select(Product).where(Product.id.in_(product_ids)))
        product_map = {p.id: p for p in result.scalars().all()}
        ordered_products = [product_map[pid] for pid in product_ids if pid in product_map]

        if not ordered_products:
            return SearchResponse(ai_summary="未找到相关商品", products=[])

        # 4. 生成 AI 推荐摘要
        ai_summary = await rag_service.generate_summary(req.query, ordered_products)

        # 5. 组装响应
        products_out: List[SearchProductOut] = [
            SearchProductOut(
                id=p.id,
                name=p.name,
                description=p.description or "",
                price=p.price,
                category=p.category or "",
                image=p.image or "",
                stock=p.stock or 0,
            )
            for p in ordered_products
        ]
        return SearchResponse(ai_summary=ai_summary, products=products_out)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
