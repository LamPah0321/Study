"""智谱 AI GLM 客户端封装。

提供：
- embed / embed_async：文本向量化（embedding-3）
- chat：异步一次性补全
- stream_chat：异步流式补全，逐 chunk 返回内容

注意：
- 同步的 SDK 调用（embeddings.create / chat.completions.create 非流式）
  统一通过 asyncio.to_thread 包裹，避免阻塞事件循环。
- 流式调用本身是迭代器，在异步生成器中逐项 yield。
"""
from __future__ import annotations

import asyncio
from typing import AsyncGenerator, List

from zhipuai import ZhipuAI

from app.core.config import settings


class GLMClient:
    """对智谱 AI SDK 的轻量封装。"""

    def __init__(self, api_key: str = "", model: str = "", embedding_model: str = "") -> None:
        self._api_key = api_key or settings.ZHIPU_API_KEY
        self._model = model or settings.LLM_MODEL
        self._embedding_model = embedding_model or settings.EMBEDDING_MODEL
        # 延迟创建底层 client，便于单测与无 key 环境下导入模块
        self._client: ZhipuAI | None = None

    @property
    def client(self) -> ZhipuAI:
        if self._client is None:
            self._client = ZhipuAI(api_key=self._api_key)
        return self._client

    # ---------- 向量 ----------
    def embed(self, text: str) -> List[float]:
        """同步：返回文本的 embedding 向量。"""
        resp = self.client.embeddings.create(
            model=self._embedding_model,
            input=text,
        )
        return resp.data[0].embedding

    async def embed_async(self, text: str) -> List[float]:
        """异步：在后台线程执行同步 embed。"""
        return await asyncio.to_thread(self.embed, text)

    # ---------- 对话 ----------
    def _chat_sync(self, messages: list, **kwargs) -> str:
        """同步一次性补全，返回完整文本。"""
        resp = self.client.chat.completions.create(
            model=self._model,
            messages=messages,
            **kwargs,
        )
        return resp.choices[0].message.content or ""

    async def chat(self, messages: list, **kwargs) -> str:
        """异步一次性补全。"""
        return await asyncio.to_thread(self._chat_sync, messages, **kwargs)

    async def stream_chat(self, messages: list, **kwargs) -> AsyncGenerator[str, None]:
        """异步流式补全，逐块返回 delta.content。

        使用 try/finally 确保流被消费完毕后正常退出。
        """
        # SDK 的流式调用返回的是一个同步可迭代对象
        stream = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self._model,
            messages=messages,
            stream=True,
            **kwargs,
        )
        try:
            for chunk in stream:
                try:
                    delta = chunk.choices[0].delta.content
                except (AttributeError, IndexError):
                    delta = None
                if delta:
                    yield delta
        finally:
            # 某些 SDK 实现需要显式关闭流
            close = getattr(stream, "close", None)
            if callable(close):
                try:
                    close()
                except Exception:
                    pass


# 全局单例
llm_client = GLMClient()
