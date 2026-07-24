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
from typing import Iterable, Optional

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
except Exception:
    _lf_observe = None
    _get_lf_client = None


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


def update_current_trace(
    *,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    tags: Optional[list] = None,
) -> None:
    """Tag the current trace with user/session info (no-op when tracing is off)."""
    if _get_lf_client is None or not _tracing_enabled():
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


def flush() -> None:
    """Flush pending LangFuse events before process exit."""
    if _get_lf_client is None or not _langfuse_should_init():
        return
    try:
        _get_lf_client().flush()
    except Exception as exc:
        logger.debug("LangFuse flush failed: {}", exc)
