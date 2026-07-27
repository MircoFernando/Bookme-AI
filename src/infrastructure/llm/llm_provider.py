"""
Chat LLM providers — BookMe AI hybrid layout.

  - Router / guardrail / extractor / chat → OpenAI (gpt-4o-mini via models.yaml)
  - Merge (hotel + flight synthesis) → native Gemini (GOOGLE_API_KEY)

Role → (model, provider) is in ``config/params.yaml`` under ``llm.roles``.
"""

from __future__ import annotations

from typing import Any, List, Optional

from langchain_openai import ChatOpenAI
from loguru import logger

from infrastructure import config


def _build_llm(
    model: str,
    provider: str,
    *,
    temperature: float = 0.0,
    streaming: bool = False,
    max_tokens: Optional[int] = None,
    **kwargs: Any,
) -> ChatOpenAI:
    """Build ``ChatOpenAI`` for OpenAI, OpenRouter, or Groq."""
    if provider == "google":
        return _build_google_llm(
            model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    llm_kwargs: dict[str, Any] = dict(
        model=model,
        temperature=temperature,
        streaming=streaming,
        max_tokens=max_tokens or config.LLM_MAX_TOKENS,
        max_retries=config.LLM_MAX_RETRIES,
        timeout=config.LLM_REQUEST_TIMEOUT,
        api_key=config.get_api_key(provider),
    )
    base_url = config.provider_base_url(provider)
    if base_url:
        llm_kwargs["base_url"] = base_url

    llm_kwargs.update(kwargs)
    return ChatOpenAI(**llm_kwargs)


def _build_google_llm(
    model: str,
    *,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    **kwargs: Any,
):
    """Native Gemini Developer API (optional; OpenRouter can serve Gemini models too)."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    api_key = config.get_api_key("google")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is required when provider is google.")
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        max_output_tokens=max_tokens or config.LLM_MAX_TOKENS,
        google_api_key=api_key,
        **kwargs,
    )


def _secondary_providers() -> List[str]:
    candidates = ["openai", "openrouter", "groq"]
    out = []
    for p in candidates:
        if config.get_api_key(p):
            out.append(p)
    return out


def _maybe_with_fallbacks(primary: ChatOpenAI, role: str, temperature: float):
    if not config.LLM_ENABLE_FALLBACK:
        return primary

    fallbacks = []
    primary_prov = config.role_provider(role)
    for p in _secondary_providers():
        if p == primary_prov:
            continue
        try:
            model, _ = config.resolve_role(role, provider_override=p)
            fallbacks.append(
                _build_llm(model, p, temperature=temperature)
            )
        except Exception as exc:
            logger.debug("Skipping fallback provider {} for {}: {}", p, role, exc)

    if not fallbacks:
        return primary

    logger.debug(
        "LLM role '{}': primary={} + {} fallback(s)",
        role,
        primary_prov,
        len(fallbacks),
    )
    return primary.with_fallbacks(fallbacks)


def get_router_llm(temperature: float = 0.0, **kwargs: Any) -> ChatOpenAI:
    """Intent routing — JSON classification."""
    model, provider = config.resolve_role("router")
    return _build_llm(model, provider, temperature=temperature, **kwargs)


def get_guardrail_llm(temperature: float = 0.0, **kwargs: Any) -> ChatOpenAI:
    """Binary scope guardrail."""
    model, provider = config.resolve_role("guardrail")
    return _build_llm(model, provider, temperature=temperature, **kwargs)


def get_extractor_llm(temperature: float = 0.0, **kwargs: Any) -> ChatOpenAI:
    """Structured extraction (memory / slots)."""
    model, provider = config.resolve_role("extractor")
    return _build_llm(model, provider, temperature=temperature, **kwargs)


def get_fast_chat_llm(temperature: float = 0.0, **kwargs: Any) -> ChatOpenAI:
    """Fast conversational replies (lighter model role from config)."""
    model, provider = config.resolve_role("fast_chat")
    return _build_llm(model, provider, temperature=temperature, **kwargs)


def get_chat_llm(
    temperature: float = 0.3,
    *,
    with_fallback: bool = True,
    **kwargs: Any,
):
    """Agent synthesis — hotel / flight / general_qa answers."""
    model, provider = config.resolve_role("chat")
    primary = _build_llm(
        model,
        provider,
        temperature=temperature,
        streaming=kwargs.pop("streaming", config.LLM_STREAMING),
        **kwargs,
    )
    if with_fallback:
        return _maybe_with_fallbacks(primary, "chat", temperature)
    return primary


def get_merge_llm(temperature: float = 0.0, **kwargs: Any):
    """Multi-route merge synthesiser (native Gemini; see llm.roles.merge)."""
    model, provider = config.resolve_role("merge")
    return _build_llm(model, provider, temperature=temperature, **kwargs)
