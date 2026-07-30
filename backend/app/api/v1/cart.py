"""购物车接口（简化版，模拟下单）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.order import Order
from app.models.product import Product
from app.schemas.cart import CartRequest

router = APIRouter(prefix="/cart", tags=["购物车"])


@router.post("/checkout", summary="购物车结算（模拟下单）")
async def checkout(req: CartRequest, session: AsyncSession = Depends(get_db)) -> dict:
    try:
        if not req.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="购物车为空")

        # 查询购物车中所有商品
        ids = [item.product_id for item in req.items]
        result = await session.execute(select(Product).where(Product.id.in_(ids)))
        product_map = {p.id: p for p in result.scalars().all()}

        # 校验商品存在性并计算总价
        order_items = []
        total = 0.0
        for item in req.items:
            product = product_map.get(item.product_id)
            if product is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"商品 {item.product_id} 不存在",
                )
            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"商品 {product.name} 库存不足",
                )
            subtotal = float(product.price) * item.quantity
            total += subtotal
            order_items.append(
                {
                    "product_id": product.id,
                    "name": product.name,
                    "price": float(product.price),
                    "quantity": item.quantity,
                    "subtotal": subtotal,
                }
            )

        # 创建订单（简化：不真实扣库存，仅记录快照）
        order = Order(
            user_id="guest",
            total_amount=total,
            status="pending",
            items=order_items,
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)

        return {
            "detail": "订单已创建",
            "order_id": order.id,
            "total_amount": total,
            "created_at": order.created_at.isoformat() if order.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
