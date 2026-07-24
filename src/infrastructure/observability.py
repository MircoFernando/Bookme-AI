"""
Observability — optional LangFuse tracing.

Every export here is a **safe no-op** when observability is disabled in
``params.yaml`` or when the ``langfuse`` package / keys are absent. This lets
you decorate nodes with ``@observe`` and call ``update_current_*`` freely
without guarding each call — zero overhead when tracing is off.

Enable by setting ``observability.enabled: true`` in ``config/params.yaml``
and adding ``LANGFUSE_SECRET_KEY`` / ``LANGFUSE_PUBLIC_KEY`` to ``.env``.
"""

from __future__ import annotations

import os
from typing import Optional

from loguru import logger

from infrastructure.config import OBSERVABILITY_ENABLED


def _enabled() -> bool:
    return bool(OBSERVABILITY_ENABLED)


# ── Optional langfuse import ──────────────────────────────────────────────────
try:
    from langfuse import observe as _lf_observe
    from langfuse import get_client as _get_lf_client
except Exception:  # package not installed — decorators become no-ops
    _lf_observe = None
    _get_lf_client = None


_client = None
_initialised = False


def get_langfuse():
    """Return a singleton LangFuse client, or None if unavailable/disabled."""
    global _client, _initialised
    if _initialised:
        return _client
    _initialised = True

    if not _enabled() or _lf_observe is None:
        logger.debug("Observability disabled — LangFuse not initialised.")
        return None

    secret = os.getenv("LANGFUSE_SECRET_KEY")
    public = os.getenv("LANGFUSE_PUBLIC_KEY")
    host = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
    if not secret or not public:
        logger.warning("LANGFUSE keys not set — tracing disabled.")
        return None

    try:
        from langfuse import Langfuse
        _client = Langfuse(secret_key=secret, public_key=public, host=host)
        logger.info("LangFuse initialised (host={})", host)
    except Exception as exc:
        logger.error("LangFuse init failed: {}", exc)
        _client = None
    return _client


def observe(*, name: Optional[str] = None, as_type: Optional[str] = None):
    """Decorator wrapping ``langfuse.observe`` — no-op when disabled."""
    def _noop(fn):
        return fn

    if not _enabled() or _lf_observe is None:
        return _noop

    kwargs = {}
    if name is not None:
        kwargs["name"] = name
    if as_type is not None:
        kwargs["as_type"] = as_type
    return _lf_observe(**kwargs)


def update_current_trace(
    *,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    tags: Optional[list] = None,
) -> None:
    """Tag the current trace with user/session info (no-op when disabled)."""
    if _get_lf_client is None or not _enabled():
        return
    try:
        client = _get_lf_client()
        kwargs = {}
        if user_id is not None:
            kwargs["user_id"] = user_id
        if session_id is not None:
            kwargs["session_id"] = session_id
        if metadata is not None:
            kwargs["metadata"] = metadata
        if tags is not None:
            kwargs["tags"] = tags
        client.update_current_trace(**kwargs)
    except Exception as exc:
        logger.debug("update_current_trace failed (non-critical): {}", exc)


def update_current_observation(
    *,
    input: Optional[str] = None,
    output: Optional[str] = None,
    metadata: Optional[dict] = None,
    usage: Optional[dict] = None,
    model: Optional[str] = None,
) -> None:
    """Attach I/O + usage to the current span/generation (no-op when disabled)."""
    if _get_lf_client is None or not _enabled():
        return
    try:
        client = _get_lf_client()
        if usage is not None or model is not None:
            gen: dict = {}
            if input is not None:
                gen["input"] = input
            if output is not None:
                gen["output"] = output
            if metadata is not None:
                gen["metadata"] = metadata
            if model is not None:
                gen["model"] = model
            if usage is not None:
                gen["usage_details"] = usage
            try:
                client.update_current_generation(**gen)
                return
            except Exception:
                pass
        span: dict = {}
        if input is not None:
            span["input"] = input
        if output is not None:
            span["output"] = output
        if metadata is not None:
            span["metadata"] = metadata
        if span:
            client.update_current_span(**span)
    except Exception as exc:
        logger.debug("update_current_observation failed (non-critical): {}", exc)


def flush() -> None:
    """Flush pending events before process exit (no-op when disabled)."""
    if _get_lf_client is None or not _enabled():
        return
    try:
        _get_lf_client().flush()
    except Exception as exc:
        logger.debug("LangFuse flush failed: {}", exc)
