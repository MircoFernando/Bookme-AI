"""
Pydantic request / response schemas for the BookMe AI API.

Chat request/response models with travel-specific route literals.
"""

from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

RouteLiteral = Literal[
    "hotel",
    "flight",
    "general_qa",
    "web_search",
    "multi",
    "out_of_scope",
]

VerdictLiteral = Literal["proceed", "out_of_scope"]


class ChatRequest(BaseModel):
    """POST /chat and POST /chat/stream."""

    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, description="User message")
    user_id: Optional[str] = Field(
        default=None,
        min_length=1,
        description=(
            "Used when AUTH_DISABLED=1 (or DEV_USER_ID fallback). "
            "Ignored when Clerk verifies the Bearer token."
        ),
    )


class ChatResponse(BaseModel):
    """POST /chat response."""

    answer: str
    route: RouteLiteral
    routes: List[str] = Field(
        default_factory=list,
        description="All agent routes for multi-intent queries",
    )
    verdict: VerdictLiteral = "proceed"
    latency_ms: int = 0
    trace_id: Optional[str] = None
    timings: Dict[str, int] = Field(
        default_factory=dict,
        description="Per-stage wall-clock latency in ms (decision, orchestrator, total, …).",
    )
    session_id: str = ""
    tool_output: str = Field(
        default="",
        description="Primary tool JSON/text from the orchestrator (debug / UI).",
    )


class ChatResetRequest(BaseModel):
    """POST /chat/reset — clear short-term memory for one thread."""

    session_id: str = Field(..., min_length=1)
    user_id: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Same rules as ChatRequest.user_id.",
    )


class ChatResetResponse(BaseModel):
    cleared: bool = True
    user_id: str
    session_id: str


class HealthResponse(BaseModel):
    status: Literal["ok", "starting", "degraded"] = "ok"


class ReadinessCheck(BaseModel):
    name: str
    ok: bool
    detail: Optional[str] = None


class ReadinessResponse(BaseModel):
    ready: bool
    checks: List[ReadinessCheck] = Field(default_factory=list)


class ConfigResponse(BaseModel):
    chat_model: str
    router_model: str
    guardrail_model: str
    merge_model: str
    provider: str
    mcp_tools_loaded: int = 0
    auth_disabled: bool = True
