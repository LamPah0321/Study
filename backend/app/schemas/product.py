"""商品相关 schema。"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(..., max_length=200, description="商品名称")
    description: str = Field("", description="商品描述")
    price: Decimal = Field(..., ge=0, description="价格")
    category: str = Field("其他", max_length=100, description="分类")
    image: str = Field("", max_length=500, description="主图 URL")
    stock: int = Field(0, ge=0, description="库存")
    specs: Optional[Any] = Field(None, description="规格参数 JSON")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    """更新时所有字段可选。"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=100)
    image: Optional[str] = Field(None, max_length=500)
    stock: Optional[int] = Field(None, ge=0)
    specs: Optional[Any] = None


class ProductOut(ProductBase):
    """商品输出模型，包含主键与时间戳。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
