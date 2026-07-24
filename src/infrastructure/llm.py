"""
LLM provider factory — multi-model, provider-flexible, resilient.

Mirrors the Week 13 pattern: one ``ChatOpenAI``-compatible client per role,
built from ``config`` (which reads ``models.yaml`` / ``params.yaml``). Every
client is created with ``max_retries`` (exponential backoff on transient
errors) and an optional cross-provider ``with_fallbacks`` wrapper so a full
provider outage degrades gracefully instead of failing the request.

Roles
-----
    get_router_llm()     → intent classification (structured JSON)
    get_guardrail_llm()  → binary in/out-of-scope classification
    get_extractor_llm()  → structured slot extraction (city, dates, ids)
    get_chat_llm()       → user-facing synthesis / agent answers

All roles default to the active provider in ``params.yaml`` (``openai`` out of
the box, so the app runs with only ``OPENAI_API_KEY``). Switch provider/model
in YAML with zero code changes.
"""

from __future__ import annotations

from typing import Any, List, Optional

from langchain_openai import ChatOpenAI
from loguru import logger

from infrastructure import config


def _build_llm(
    model: str,
    provider: Optional[str] = None,
    *,
    temperature: float = 0.0,
    streaming: bool = False,
    max_tokens: Optional[int] = None,
    **kwargs: Any,
) -> ChatOpenAI:
    """Build a single ``ChatOpenAI`` client for any OpenAI-compatible provider."""
    provider = provider or config.PROVIDER
    llm_kwargs: dict[str, Any] = dict(
        model=model,
        temperature=temperature,
        streaming=streaming,
        max_tokens=max_tokens or config.LLM_MAX_TOKENS,
        max_retries=config.LLM_MAX_RETRIES,       # built-in exponential backoff
        timeout=config.LLM_REQUEST_TIMEOUT,
        api_key=config.get_api_key(provider),
    )
    base_url = config.provider_base_url(provider)
    if base_url:
        llm_kwargs["base_url"] = base_url

    llm_kwargs.update(kwargs)
    return ChatOpenAI(**llm_kwargs)


def _secondary_providers() -> List[str]:
    """Other providers (besides the active one) whose API key is present.

    These back the ``with_fallbacks`` chain: if the primary provider errors
    (after its own retries), LangChain transparently retries the same request
    on the next provider in the list.
    """
    candidates = ["openai", "openrouter", "groq"]
    out = []
    for p in candidates:
        if p != config.PROVIDER and config.get_api_key(p):
            out.append(p)
    return out


def _maybe_with_fallbacks(primary: ChatOpenAI, role: str, temperature: float):
    """Wrap ``primary`` with fallbacks to other providers when enabled + available."""
    if not config.LLM_ENABLE_FALLBACK:
        return primary

    fallbacks = []
    for p in _secondary_providers():
        try:
            model = config._model_for(role, tier=config.LLM_FALLBACK_TIER, provider=p)
            fallbacks.append(
                _build_llm(model, provider=p, temperature=temperature)
            )
        except Exception as exc:  # pragma: no cover — defensive
            logger.debug("Skipping fallback provider {}: {}", p, exc)

    if not fallbacks:
        return primary

    logger.debug(
        "LLM role '{}': primary={} + {} fallback(s)",
        role, config.PROVIDER, len(fallbacks),
    )
    return primary.with_fallbacks(fallbacks)


# ── Role factories ────────────────────────────────────────────────────────────
def get_router_llm(temperature: float = 0.0, **kwargs: Any) -> ChatOpenAI:
    """Intent-classification LLM. Returns a raw client so callers may use
    ``.with_structured_output(...)`` or parse JSON directly."""
    return _build_llm(config.ROUTER_MODEL, temperature=temperature, **kwargs)


def get_guardrail_llm(temperature: float = 0.0, **kwargs: Any) -> ChatOpenAI:
    """Binary scope-classifier LLM (fast/cheap tier)."""
    return _build_llm(config.GUARDRAIL_MODEL, temperature=temperature, **kwargs)


def get_extractor_llm(temperature: float = 0.0, **kwargs: Any) -> ChatOpenAI:
    """Structured slot-extraction LLM. Returned raw so callers can use
    ``.with_structured_output(...)``."""
    return _build_llm(config.EXTRACTOR_MODEL, temperature=temperature, **kwargs)


def get_chat_llm(temperature: float = 0.3, *, with_fallback: bool = True, **kwargs: Any):
    """User-facing synthesis LLM.

    By default wrapped with cross-provider fallbacks (used via ``.invoke`` /
    ``.ainvoke`` only). Pass ``with_fallback=False`` to get the raw client.
    """
    primary = _build_llm(config.CHAT_MODEL, temperature=temperature,
                         streaming=kwargs.pop("streaming", config.LLM_STREAMING), **kwargs)
    if with_fallback:
        return _maybe_with_fallbacks(primary, "chat", temperature)
    return primary
