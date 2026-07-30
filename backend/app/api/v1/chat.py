"""AI 流式对话接口（SSE）。"""
from __future__ import annotations

import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest
from app.services import rag_service

router = APIRouter(prefix="/chat", tags=["AI 对话"])


async def _sse_stream(req: ChatRequest) -> AsyncGenerator[str, None]:
    """生成 SSE 流：每段内容以 data: {...}\\n\\n 推送，最后发送 [DONE]。"""
    try:
        async for chunk in rag_service.chat_with_rag(req.message, req.history):
            payload = json.dumps({"content": chunk}, ensure_ascii=False)
            yield f"data: {payload}\n\n"
    except Exception as e:
        # 在流中推送错误信息，保证客户端能感知
        err = json.dumps({"error": str(e)}, ensure_ascii=False)
        yield f"data: {err}\n\n"
    finally:
        yield "data: [DONE]\n\n"


@router.post("/stream", summary="AI 流式对话 (SSE)")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    try:
        return StreamingResponse(
            _sse_stream(req),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
