"""对话相关 schema。"""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="消息角色：system / user / assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户本次输入")
    history: List[ChatMessage] = Field(default_factory=list, description="历史对话")
