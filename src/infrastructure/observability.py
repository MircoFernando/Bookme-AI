"""
Observability — LangFuse tracing + Prompt Management.

Tracing
-------
Decorate nodes with ``@observe``. No-op when ``observability.enabled`` is false
in ``params.yaml`` (or LangFuse keys missing).

Prompt Management
-----------------
Call ``fetch_prompt(name, fallback=..., **vars)`` from ``agents/prompts/``.
When ``LANGFUSE_PROMPTS=true`` in ``.env`` *or*
``observability.prompts_enabled: true`` in ``params.yaml``, the LangFuse copy
is used (Mustache ``{{variable}}``). Otherwise the local fallback string is
used (Python ``{variable}`` via ``str.format``).

Edit prompts in the LangFuse UI and bump the production label — no redeploy.
The client cache TTL (default 300s) controls how quickly changes appear; lower
``prompt_cache_ttl_seconds`` in dev if you want faster iteration.

Requires in ``.env`` (for either feature):
    LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY
Optional:
    LANGFUSE_BASE_URL (default https://cloud.langfuse.com)
    LANGFUSE_PROMPTS=true
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator, Iterable, Optional

from loguru import logger

from infrastructure.config import (
    OBSERVABILITY_ENABLED,
    OBSERVABILITY_PROMPTS_ENABLED,
    PROMPT_CACHE_TTL_SECONDS,
)


def langfuse_prompts_enabled() -> bool:
    """True when LangFuse Prompt Management should be the source of truth."""
    env_flag = os.getenv("LANGFUSE_PROMPTS", "").strip().lower()
    if env_flag in {"1", "true", "yes", "on"}:
        return True
    if env_flag in {"0", "false", "no", "off"}:
        return False
    return bool(OBSERVABILITY_PROMPTS_ENABLED)


def _tracing_enabled() -> bool:
    return bool(OBSERVABILITY_ENABLED)


def _langfuse_should_init() -> bool:
    """Initialise client if tracing and/or prompt management is on."""
    return _tracing_enabled() or langfuse_prompts_enabled()


# ── Optional langfuse import ──────────────────────────────────────────────────
try:
    from langfuse import observe as _lf_observe
    from langfuse import get_client as _get_lf_client
    from langfuse import propagate_attributes as _propagate_attributes
except Exception:
    _lf_observe = None
    _get_lf_client = None
    _propagate_attributes = None


_client = None
_initialised = False


def get_langfuse():
    """Singleton LangFuse client, or None if unavailable / not needed."""
    global _client, _initialised
    if _initialised:
        return _client
    _initialised = True

    if not _langfuse_should_init() or _lf_observe is None:
        logger.debug("LangFuse not initialised (tracing/prompts off or package missing).")
        return None

    secret = os.getenv("LANGFUSE_SECRET_KEY")
    public = os.getenv("LANGFUSE_PUBLIC_KEY")
    host = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
    if not secret or not public:
        logger.warning("LANGFUSE keys not set — tracing/prompts unavailable.")
        return None

    try:
        from langfuse import Langfuse

        _client = Langfuse(secret_key=secret, public_key=public, host=host)
        logger.info(
            "LangFuse initialised (host={}, tracing={}, prompts={})",
            host,
            _tracing_enabled(),
            langfuse_prompts_enabled(),
        )
    except Exception as exc:
        logger.error("LangFuse init failed: {}", exc)
        _client = None
    return _client


def observe(*, name: Optional[str] = None, as_type: Optional[str] = None):
    """Decorator wrapping ``langfuse.observe`` — no-op when tracing is off."""
    def _noop(fn):
        return fn

    if not _tracing_enabled() or _lf_observe is None:
        return _noop

    kwargs = {}
    if name is not None:
        kwargs["name"] = name
    if as_type is not None:
        kwargs["as_type"] = as_type
    return _lf_observe(**kwargs)


def fetch_prompt(
    name: str,
    *,
    fallback: str,
    cache_ttl_seconds: Optional[int] = None,
    **compile_vars: str,
) -> str:
    """
    Resolve a prompt template by name.

    LangFuse path uses Mustache ``{{var}}``; local fallback uses ``{var}``.
    """
    ttl = cache_ttl_seconds if cache_ttl_seconds is not None else PROMPT_CACHE_TTL_SECONDS

    if langfuse_prompts_enabled():
        client = get_langfuse()
        if client is not None:
            try:
                prompt_obj = client.get_prompt(
                    name,
                    type="text",
                    cache_ttl_seconds=ttl,
                )
                if compile_vars:
                    compiled = prompt_obj.compile(**compile_vars)
                else:
                    compiled = prompt_obj.compile()
                logger.debug(
                    "LangFuse prompt '{}' loaded (version={})",
                    name,
                    getattr(prompt_obj, "version", "?"),
                )
                return compiled
            except Exception as exc:
                logger.debug(
                    "LangFuse prompt '{}' unavailable ({}); using local fallback.",
                    name,
                    exc,
                )

    if compile_vars:
        return fallback.format(**compile_vars)
    return fallback


def prefetch_prompts(names: Iterable[str]) -> int:
    """
    Warm the LangFuse client cache at startup so the first chat request
    does not pay a network hop per prompt.
    """
    if not langfuse_prompts_enabled():
        logger.info(
            "Prompt source: LOCAL fallbacks (set LANGFUSE_PROMPTS=true or "
            "observability.prompts_enabled in params.yaml to use LangFuse)."
        )
        return 0

    client = get_langfuse()
    if client is None:
        return 0

    warmed = 0
    for name in names:
        try:
            client.get_prompt(name, type="text", cache_ttl_seconds=PROMPT_CACHE_TTL_SECONDS)
            warmed += 1
        except Exception as exc:
            logger.debug("prefetch: '{}' not in LangFuse ({})", name, exc)
    if warmed:
        logger.info("Pre-warmed {} LangFuse prompt(s).", warmed)
    return warmed


@asynccontextmanager
async def langfuse_turn_attributes(
    *,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    tags: Optional[list] = None,
) -> AsyncIterator[None]:
    """
    Langfuse SDK v4: propagate user/session/tags to all child spans in a chat turn.

    Wrap the body of ``run_chat_turn`` (inside ``@observe(name="chat_turn")``).
    """
    if (
        not _tracing_enabled()
        or _propagate_attributes is None
        or _get_lf_client is None
    ):
        yield
        return

    prop_kwargs: dict = {}
    if user_id:
        prop_kwargs["user_id"] = user_id
    if session_id:
        prop_kwargs["session_id"] = session_id
    if metadata:
        prop_kwargs["metadata"] = metadata
    if tags:
        prop_kwargs["tags"] = tags

    if not prop_kwargs:
        yield
        return

    with _propagate_attributes(**prop_kwargs):
        yield


def update_current_trace(
    *,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    tags: Optional[list] = None,
) -> None:
    """
    Enrich the active observation (Langfuse SDK v4).

    ``user_id`` / ``session_id`` / initial ``tags`` should be set via
    ``langfuse_turn_attributes`` for the whole turn so child spans inherit them.
    This helper updates the current span metadata (and optional tags) mid-flight.
    """
    if _get_lf_client is None or not _tracing_enabled():
        return
    try:
        client = _get_lf_client()
        span_meta: dict = {}
        if metadata:
            span_meta.update(metadata)
        if tags:
            span_meta["tags"] = tags
        if span_meta:
            client.update_current_span(metadata=span_meta)
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
    """Attach I/O + usage to the current span/generation (no-op when tracing is off)."""
    if _get_lf_client is None or not _tracing_enabled():
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


def get_current_trace_id() -> Optional[str]:
    """OpenTelemetry / Langfuse trace id for the active context, if any."""
    if _get_lf_client is None or not _tracing_enabled():
        return None
    try:
        client = _get_lf_client()
        fn = getattr(client, "get_current_trace_id", None)
        if callable(fn):
            tid = fn()
            return str(tid) if tid else None
    except Exception as exc:
        logger.debug("get_current_trace_id failed (non-critical): {}", exc)
    return None


def flush() -> None:
    """Flush pending LangFuse events before process exit."""
    if _get_lf_client is None or not _langfuse_should_init():
        return
    try:
        _get_lf_client().flush()
    except Exception as exc:
        logger.debug("LangFuse flush failed: {}", exc)
