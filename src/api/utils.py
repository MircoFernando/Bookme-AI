"""
Shared API helpers — trace ids and ChatResult mapping.
"""

from __future__ import annotations

from typing import List, Optional

from agents.chat_pipeline import ChatResult
from api.schemas import ChatResponse, RouteLiteral, VerdictLiteral


def current_trace_id() -> Optional[str]:
    try:
        from infrastructure.observability import get_langfuse

        client = get_langfuse()
        if client is None:
            return None
        tracer = getattr(client, "tracer", None)
        span = getattr(tracer, "current_span", None) if tracer else None
        return getattr(span, "trace_id", None) if span else None
    except Exception:
        return None


def _normalize_route(
    route: str,
    routes: List[str],
    verdict: VerdictLiteral,
) -> RouteLiteral:
    if verdict == "out_of_scope" or route == "out_of_scope":
        return "out_of_scope"
    if len(routes) > 1:
        return "multi"
    if route in ("hotel", "flight", "general_qa", "web_search"):
        return route  # type: ignore[return-value]
    return "general_qa"


def chat_result_to_response(result: ChatResult) -> ChatResponse:
    """Map pipeline ``ChatResult`` → HTTP ``ChatResponse``."""
    verdict: VerdictLiteral = result.verdict
    route = _normalize_route(result.route, result.routes, verdict)
    trace_id = result.trace_id or current_trace_id()
    return ChatResponse(
        answer=result.answer,
        route=route,
        routes=list(result.routes),
        verdict=verdict,
        latency_ms=result.latency_ms,
        trace_id=trace_id,
        timings=dict(result.timings),
        session_id=result.session_id,
        tool_output=result.tool_output or "",
    )
