"""商品模型 Product。"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import BigInteger, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Product(Base):
    """商品表。"""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True, comment="商品名称")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="", comment="商品描述")
    price: Mapped[Any] = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="价格")
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="其他", index=True, comment="分类")
    image: Mapped[str] = mapped_column(String(500), nullable=False, default="", comment="主图 URL")
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="库存")
    specs: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True, comment="规格参数 JSON")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Product id={self.id} name={self.name!r}>"
