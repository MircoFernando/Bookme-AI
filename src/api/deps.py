"""
Dependency injection — objects built in ``api.main`` lifespan live on ``app.state``.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Optional

from fastapi import HTTPException, Request

if TYPE_CHECKING:
    from agents.orchestrator import AgentOrchestrator


def is_auth_disabled() -> bool:
    """When true, ``user_id`` comes from the request body or ``DEV_USER_ID``."""
    return os.getenv("AUTH_DISABLED", "1").lower() in ("1", "true", "yes")


def _state_attr(request: Request, name: str) -> Any:
    value = getattr(request.app.state, name, None)
    if value is None:
        raise HTTPException(
            status_code=503,
            detail=f"API not ready — {name} is still initialising",
        )
    return value


def get_session_store(request: Request):
    return _state_attr(request, "session_store")


def get_decision_graph(request: Request):
    return _state_attr(request, "decision_graph")


def get_orchestrator(request: Request) -> "AgentOrchestrator":
    return _state_attr(request, "orchestrator")


def _clerk_user_id(request: Request) -> str:
    secret = (os.getenv("CLERK_SECRET_KEY") or "").strip()
    if not secret:
        raise HTTPException(
            status_code=503,
            detail="Clerk auth enabled but CLERK_SECRET_KEY is not set",
        )
    try:
        from clerk_backend_api import Clerk
        from clerk_backend_api.security.types import AuthenticateRequestOptions
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail="Install clerk-backend-api for production auth (pip install clerk-backend-api)",
        ) from exc

    parties_raw = (os.getenv("CLERK_AUTHORIZED_PARTIES") or "").strip()
    authorized_parties = [p.strip() for p in parties_raw.split(",") if p.strip()] or None
    options = (
        AuthenticateRequestOptions(authorized_parties=authorized_parties)
        if authorized_parties
        else AuthenticateRequestOptions()
    )

    clerk = Clerk(bearer_auth=secret)
    state = clerk.authenticate_request(request, options)
    if not state.is_signed_in:
        raise HTTPException(status_code=401, detail="Unauthorized")
    payload = state.payload or {}
    sub = payload.get("sub") if isinstance(payload, dict) else None
    if not sub:
        raise HTTPException(status_code=401, detail="Missing user id in token")
    return str(sub)


async def resolve_user_id(request: Request, body_user_id: Optional[str] = None) -> str:
    """
    Production: Clerk JWT ``sub`` from ``Authorization: Bearer``.

    Local smoke: ``AUTH_DISABLED=1`` plus optional ``user_id`` in body or ``DEV_USER_ID``.
    """
    if is_auth_disabled():
        uid = (body_user_id or os.getenv("DEV_USER_ID") or "dev-user").strip()
        if not uid:
            raise HTTPException(status_code=400, detail="user_id required when AUTH is disabled")
        return uid
    return _clerk_user_id(request)
