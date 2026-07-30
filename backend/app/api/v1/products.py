"""商品 CRUD 接口。"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.services import product_service

router = APIRouter(prefix="/products", tags=["商品管理"])


@router.get("", response_model=List[ProductOut], summary="获取商品列表")
async def list_products(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_db),
) -> List[ProductOut]:
    try:
        products = await product_service.list_products(session, category=category, skip=skip, limit=limit)
        return [ProductOut.model_validate(p) for p in products]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{pid}", response_model=ProductOut, summary="获取单个商品")
async def get_product(pid: int, session: AsyncSession = Depends(get_db)) -> ProductOut:
    try:
        product = await product_service.get_product(session, pid)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"商品 {pid} 不存在")
        return ProductOut.model_validate(product)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED, summary="创建商品")
async def create_product(data: ProductCreate, session: AsyncSession = Depends(get_db)) -> ProductOut:
    try:
        product = await product_service.create_product(session, data)
        return ProductOut.model_validate(product)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{pid}", response_model=ProductOut, summary="更新商品")
async def update_product(
    pid: int, data: ProductUpdate, session: AsyncSession = Depends(get_db)
) -> ProductOut:
    try:
        product = await product_service.update_product(session, pid, data)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"商品 {pid} 不存在")
        return ProductOut.model_validate(product)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{pid}", summary="删除商品")
async def delete_product(pid: int, session: AsyncSession = Depends(get_db)) -> dict:
    try:
        ok = await product_service.delete_product(session, pid)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"商品 {pid} 不存在")
        return {"detail": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
