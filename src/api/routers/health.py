"""
System endpoints — liveness, readiness, and active configuration.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Request

from api.deps import is_auth_disabled
from api.schemas import (
    ConfigResponse,
    HealthResponse,
    ReadinessCheck,
    ReadinessResponse,
)

router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    orchestrator = getattr(request.app.state, "orchestrator", None)
    return HealthResponse(status="ok" if orchestrator is not None else "starting")


@router.get("/ready", response_model=ReadinessResponse)
async def ready(request: Request) -> ReadinessResponse:
    orchestrator = getattr(request.app.state, "orchestrator", None)
    if orchestrator is None:
        return ReadinessResponse(
            ready=False,
            checks=[
                ReadinessCheck(name="orchestrator", ok=False, detail="not initialised"),
            ],
        )

    async def check_config() -> ReadinessCheck:
        try:
            from infrastructure import config

            await asyncio.to_thread(config.validate)
            return ReadinessCheck(name="config", ok=True)
        except Exception as exc:
            return ReadinessCheck(name="config", ok=False, detail=str(exc)[:200])

    async def check_mcp() -> ReadinessCheck:
        tools = getattr(orchestrator, "mcp_tools", None) or {}
        count = len(tools)
        ok = count >= 7
        return ReadinessCheck(
            name="mcp_tools",
            ok=ok,
            detail=f"{count} tools loaded" if ok else f"expected ≥7, got {count}",
        )

    async def check_tavily() -> ReadinessCheck:
        from infrastructure.config import get_tavily_api_key

        key = get_tavily_api_key()
        return ReadinessCheck(
            name="tavily_api_key",
            ok=bool(key),
            detail="configured" if key else "TAVILY_API_KEY missing in API env",
        )

    async def check_session_store() -> ReadinessCheck:
        store = getattr(request.app.state, "session_store", None)
        if store is None:
            return ReadinessCheck(name="session_store", ok=False, detail="missing")
        try:
            await asyncio.to_thread(store.recent_pairs, "__probe__", "__probe__", 0)
            return ReadinessCheck(name="session_store", ok=True)
        except Exception as exc:
            return ReadinessCheck(name="session_store", ok=False, detail=str(exc)[:200])

    checks = await asyncio.gather(
        check_config(), check_mcp(), check_tavily(), check_session_store()
    )
    return ReadinessResponse(ready=all(c.ok for c in checks), checks=list(checks))


@router.get("/config", response_model=ConfigResponse)
async def active_config(request: Request) -> ConfigResponse:
    from infrastructure.config import (
        CHAT_MODEL,
        GUARDRAIL_MODEL,
        MERGE_MODEL,
        PROVIDER,
        ROUTER_MODEL,
    )

    orchestrator = getattr(request.app.state, "orchestrator", None)
    tools = getattr(orchestrator, "mcp_tools", None) if orchestrator else None
    return ConfigResponse(
        chat_model=CHAT_MODEL,
        router_model=ROUTER_MODEL,
        guardrail_model=GUARDRAIL_MODEL,
        merge_model=MERGE_MODEL,
        provider=PROVIDER,
        mcp_tools_loaded=len(tools or {}),
        auth_disabled=is_auth_disabled(),
    )
