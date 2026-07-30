"""购物车相关 schema。"""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class CartItem(BaseModel):
    product_id: int = Field(..., ge=1, description="商品ID")
    quantity: int = Field(1, ge=1, description="数量")


class CartRequest(BaseModel):
    items: List[CartItem] = Field(default_factory=list, description="购物车商品列表")


class CartCheckout(BaseModel):
    """结账请求（可附加收货信息）。"""
    items: List[CartItem] = Field(default_factory=list, description="购物车商品列表")
    user_id: str = Field("guest", description="用户ID")
    address: str = Field("", description="收货地址")
