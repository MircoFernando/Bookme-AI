"""
Conversational chat endpoints — decision graph → orchestrator with SSE streaming.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Awaitable, Callable, Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from loguru import logger

from agents.chat_pipeline import run_chat_turn
from api.deps import (
    get_decision_graph,
    get_orchestrator,
    get_session_store,
    resolve_user_id,
)
from api.schemas import ChatRequest, ChatResetRequest, ChatResetResponse, ChatResponse
from api.utils import chat_result_to_response

EmitFn = Callable[[Dict[str, Any]], Awaitable[None]]

router = APIRouter(tags=["Chat"])


async def _noop_emit(_event: Dict[str, Any]) -> None:
    return None


async def _run_chat_pipeline(
    req: ChatRequest,
    *,
    request: Request,
    emit: EmitFn,
) -> ChatResponse:
    user_id = await resolve_user_id(request, req.user_id)
    result = await run_chat_turn(
        message=req.message,
        user_id=user_id,
        session_id=req.session_id,
        decision_graph=get_decision_graph(request),
        orchestrator=get_orchestrator(request),
        session_store=get_session_store(request),
        emit=emit,
    )
    return chat_result_to_response(result)


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request) -> ChatResponse:
    return await _run_chat_pipeline(req, request=request, emit=_noop_emit)


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest, request: Request) -> StreamingResponse:
    queue: asyncio.Queue = asyncio.Queue()

    async def emit(event: Dict[str, Any]) -> None:
        await queue.put(event)

    async def run() -> None:
        try:
            final = await _run_chat_pipeline(req, request=request, emit=emit)
            await queue.put(
                {
                    "type": "final",
                    "answer": final.answer,
                    "route": final.route,
                    "routes": final.routes,
                    "verdict": final.verdict,
                    "latency_ms": final.latency_ms,
                    "trace_id": final.trace_id,
                    "timings": final.timings,
                    "session_id": final.session_id,
                    "tool_output": final.tool_output,
                }
            )
        except HTTPException as exc:
            await queue.put(
                {
                    "type": "error",
                    "status": exc.status_code,
                    "message": str(exc.detail),
                }
            )
        except Exception as exc:
            logger.exception("Streaming chat failed: {}", exc)
            await queue.put({"type": "error", "status": 500, "message": str(exc)})
        finally:
            await queue.put(None)

    asyncio.create_task(run())

    async def event_generator():
        yield ": stream-open\n\n"
        while True:
            event = await queue.get()
            if event is None:
                break
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "cache-control": "no-cache",
            "x-accel-buffering": "no",
            "connection": "keep-alive",
        },
    )


@router.post("/chat/reset", response_model=ChatResetResponse)
async def chat_reset(
    req: ChatResetRequest,
    request: Request,
    session_store=Depends(get_session_store),
) -> ChatResetResponse:
    user_id = await resolve_user_id(request, req.user_id)
    await asyncio.to_thread(session_store.reset, user_id, req.session_id)
    return ChatResetResponse(cleared=True, user_id=user_id, session_id=req.session_id)
