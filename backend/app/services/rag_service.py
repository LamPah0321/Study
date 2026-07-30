"""RAG 检索增强生成核心服务。

负责：
- 商品向量的增删（写入 Chroma）
- 基于查询的向量检索（返回 product_id 列表）
- 构建 LLM 上下文
- 生成推荐摘要（一次性）
- 流式 RAG 对话（逐 chunk 返回）

所有 Chroma 同步操作均通过 asyncio.to_thread 包裹。
"""
from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator, Iterable, List, Sequence

from app.core.chroma_client import get_chroma_collection
from app.core.llm_client import llm_client
from app.utils.helpers import format_products_for_prompt, safe_int_id

# 系统提示词
SYSTEM_PROMPT = "你是 AI 商城导购助手，根据商品信息给出自然、专业的推荐语。"


def _collection():
    """获取 Chroma collection（同步，调用方需在 to_thread 中使用）。"""
    return get_chroma_collection()


# ---------------- 向量增删 ----------------
async def upsert_product_embedding(product_id: int, text: str) -> None:
    """对商品文本做 embedding，并 upsert 到 Chroma。"""
    if not text or not text.strip():
        return

    embedding = await llm_client.embed_async(text)
    collection = await asyncio.to_thread(_collection)

    await asyncio.to_thread(
        collection.upsert,
        ids=[str(product_id)],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"product_id": str(product_id)}],
    )


async def delete_product_embedding(product_id: int) -> None:
    """从 Chroma 删除指定商品的向量。"""
    collection = await asyncio.to_thread(_collection)
    await asyncio.to_thread(collection.delete, ids=[str(product_id)])


# ---------------- 检索 ----------------
async def retrieve_products(query: str, top_k: int = 5) -> List[int]:
    """基于查询文本做向量检索，返回相关商品的 product_id 列表。

    解析 Chroma 返回的 id 字符串，提取其中的数字部分。
    """
    query = (query or "").strip()
    if not query:
        return []

    embedding = await llm_client.embed_async(query)
    collection = await asyncio.to_thread(_collection)

    result = await asyncio.to_thread(
        collection.query,
        query_embeddings=[embedding],
        n_results=top_k,
    )

    ids_list = result.get("ids") or []
    if not ids_list:
        return []

    # ids 是一个二维列表：[[id1, id2, ...]]
    first_row = ids_list[0] if ids_list else []

    product_ids: List[int] = []
    for raw_id in first_row:
        pid = safe_int_id(raw_id)
        if pid is not None and pid not in product_ids:
            product_ids.append(pid)
    return product_ids


# ---------------- 上下文构建 ----------------
async def build_search_context(products: Iterable[Any]) -> str:
    """将商品列表格式化为供 LLM 使用的上下文文本。"""
    # format_products_for_prompt 是同步的且轻量，直接调用即可
    return format_products_for_prompt(products)


async def generate_summary(query: str, products: Sequence[Any]) -> str:
    """根据查询与候选商品生成一段推荐摘要。"""
    context = await build_search_context(products)
    user_prompt = (
        f"用户问题：{query}\n"
        f"候选商品：\n{context}\n"
        f"请给出推荐语"
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    try:
        return await llm_client.chat(messages, temperature=0.7)
    except Exception as e:
        # LLM 调用失败时降级，返回提示而非抛错，保证搜索接口可用
        return f"AI 摘要生成失败：{e}"


# ---------------- 流式 RAG 对话 ----------------
async def chat_with_rag(
    message: str,
    history: Sequence[Any],
) -> AsyncGenerator[str, None]:
    """基于 RAG 的流式对话。

    流程：
    1. 根据用户当前消息检索相关商品 id（仅用文本检索，不再回查 DB，
       以避免在此处引入 DB 依赖；商品细节由调用方按需注入或由 LLM 综合）。
    2. 构建包含 system + 历史对话 + 当前问题的消息列表。
    3. 调用流式接口，逐块 yield。
    """
    message = (message or "").strip()

    # 尝试检索相关商品，用作 system 上下文补充（失败不阻断对话）
    context_text = ""
    try:
        product_ids = await retrieve_products(message, top_k=5)
        if product_ids:
            # 仅把 id 作为提示；如需更丰富上下文可由调用方传入商品对象
            context_text = f"（参考商品ID：{', '.join(map(str, product_ids))}）"
    except Exception:
        context_text = ""

    # 组装消息
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT + ("\n" + context_text if context_text else "")}
    ]

    # 追加历史对话（保留 role/content）
    for h in history or []:
        role = getattr(h, "role", None) or (h.get("role") if isinstance(h, dict) else None)
        content = getattr(h, "content", None) or (h.get("content") if isinstance(h, dict) else None)
        if role and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message or "你好"})

    async for chunk in llm_client.stream_chat(messages, temperature=0.7):
        yield chunk
