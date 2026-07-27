"""
FastAPI application — BookMe AI travel assistant (Phase 6).

Start::

    make run-api
    # or: cd src && PYTHONPATH=. uvicorn api.main:app --reload --port 8000
"""

from __future__ import annotations

import asyncio
import os
import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

_PROJECT_ROOT = os.path.dirname(_SRC)
load_dotenv(dotenv_path=os.path.join(_PROJECT_ROOT, ".env"), override=False)

from agents.decision_graph import build_decision_graph
from agents.orchestrator import build_agent_mcp
from agents.prompts.agent_prompts import ALL_LANGFUSE_PROMPT_NAMES
from agents.router import get_query_router
from api.deps import is_auth_disabled
from api.middleware import install_middleware
from api.routers import chat as chat_router
from api.routers import health as health_router
from infrastructure.observability import prefetch_prompts
from infrastructure.session_store import SessionStore


def _cors_origins() -> list[str]:
    raw = (os.getenv("CORS_ORIGINS") or "*").strip()
    if raw == "*":
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    from infrastructure import config

    logger.info("Starting BookMe AI API...")
    if not is_auth_disabled() and not (os.getenv("CLERK_SECRET_KEY") or "").strip():
        raise RuntimeError(
            "CLERK_SECRET_KEY is required when AUTH_DISABLED is not set. "
            "For local dev, set AUTH_DISABLED=1 in .env. See docs/CLERK_SETUP.md."
        )
    if not is_auth_disabled() and not (
        os.getenv("CLERK_AUTHORIZED_PARTIES") or ""
    ).strip():
        logger.warning(
            "CLERK_AUTHORIZED_PARTIES is empty — set frontend origins (e.g. "
            "http://localhost:5173). See docs/CLERK_SETUP.md."
        )

    await asyncio.to_thread(config.validate)
    config.dump()

    session_store = SessionStore()
    decision_graph = build_decision_graph()
    orchestrator = await build_agent_mcp(session_store=session_store)

    app.state.session_store = session_store
    app.state.decision_graph = decision_graph
    app.state.orchestrator = orchestrator

    async def _warmup_prompts() -> None:
        try:
            await asyncio.to_thread(prefetch_prompts, ALL_LANGFUSE_PROMPT_NAMES)
        except Exception as exc:
            logger.warning("Prompt prefetch failed: {}", exc)

    async def _warmup_router() -> None:
        try:
            await get_query_router().aroute("ping", "")
        except Exception as exc:
            logger.debug("Router warmup (non-fatal): {}", exc)

    await asyncio.gather(_warmup_prompts(), _warmup_router())
    logger.success("BookMe AI API ready (MCP orchestrator + decision graph online)")

    try:
        yield
    finally:
        logger.info("Shutting down BookMe AI API...")
        mcp_client = getattr(orchestrator, "mcp_client", None)
        if mcp_client is not None:
            try:
                close = getattr(mcp_client, "aclose", None) or getattr(
                    mcp_client, "close", None
                )
                if close:
                    result = close()
                    if asyncio.iscoroutine(result):
                        await result
            except Exception as exc:
                logger.warning("MCP client shutdown raised: {}", exc)


app = FastAPI(
    title="BookMe AI API",
    description=(
        "Travel planning chat API: parallel guardrail + router decision graph, "
        "then MCP-backed hotel / flight / web search agents."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
install_middleware(app)

app.include_router(health_router.router)
app.include_router(chat_router.router)


@app.get("/", tags=["System"])
async def root():
    return {
        "service": "BookMe AI API",
        "version": app.version,
        "docs": "/docs",
        "auth_disabled": is_auth_disabled(),
    }
