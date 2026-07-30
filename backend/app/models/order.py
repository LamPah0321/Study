"""订单模型 Order（简化版）。"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, Numeric, String, func
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Order(Base):
    """订单表。"""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, default="guest", comment="用户ID")
    total_amount: Mapped[Any] = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="总金额")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", comment="订单状态")
    items: Mapped[Any] = mapped_column(JSON, nullable=False, comment="订单商品快照")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Order id={self.id} user={self.user_id!r} status={self.status!r}>"
