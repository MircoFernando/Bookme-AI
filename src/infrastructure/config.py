"""
Application configuration — loads from YAML + environment.

CONFIGURATION POLICY
====================
- Behaviour/config lives in ``config/params.yaml`` and ``config/models.yaml``.
- Secrets (API keys, credentialed URLs) live ONLY in ``.env`` and are read
  via ``os.getenv()``. Never commit secrets.

BookMe AI loads a provider-flexible multi-model LLM setup, the external
travel service endpoints the MCP servers bridge to, per-session memory limits,
and logging/observability toggles.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

# ── Project paths ─────────────────────────────────────────────────────────────
# config.py lives at src/infrastructure/config.py → project root is 3 parents up.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_DIR = _PROJECT_ROOT / "config"

# Load .env once, from the project root, at import time.
load_dotenv(dotenv_path=_PROJECT_ROOT / ".env", override=False)


# ── YAML loading helpers ──────────────────────────────────────────────────────
def _load_yaml(filename: str) -> Dict[str, Any]:
    path = _CONFIG_DIR / filename
    if not path.exists():
        return {}
    with open(path, "r") as fh:
        return yaml.safe_load(fh) or {}


def _get_nested(d: Dict, *keys, default=None):
    """Safely read a nested key path from a dict."""
    cur: Any = d
    for key in keys:
        if isinstance(cur, dict):
            cur = cur.get(key)
        else:
            return default
    return cur if cur is not None else default


_PARAMS = _load_yaml("params.yaml")
_MODELS = _load_yaml("models.yaml")


# ── Provider ──────────────────────────────────────────────────────────────────
PROVIDER: str = _get_nested(_PARAMS, "provider", "default", default="openai")
MODEL_TIER: str = _get_nested(_PARAMS, "provider", "tier", default="general")

OPENROUTER_BASE_URL: str = _get_nested(
    _PARAMS, "provider", "openrouter_base_url",
    default="https://openrouter.ai/api/v1",
)
GROQ_BASE_URL: str = _get_nested(
    _PARAMS, "provider", "groq_base_url",
    default="https://api.groq.com/openai/v1",
)


def _model_for(role: str, tier: Optional[str] = None, provider: Optional[str] = None) -> str:
    """Resolve a model name for a role (chat|router|guardrail|extractor|merge)."""
    provider = provider or PROVIDER
    tier = tier or MODEL_TIER
    # Fall back to the "general" tier, then a sane hardcoded default.
    return (
        _get_nested(_MODELS, provider, role, tier)
        or _get_nested(_MODELS, provider, role, "general")
        or _get_nested(_MODELS, provider, "chat", tier)
        or _get_nested(_MODELS, provider, "chat", "general")
        or "gpt-4o-mini"
    )


def _role_yaml_spec(role: str) -> Optional[Dict[str, Any]]:
    spec = _get_nested(_PARAMS, "llm", "roles", role)
    return spec if isinstance(spec, dict) else None


def resolve_role(
    role: str,
    *,
    provider_override: Optional[str] = None,
) -> tuple[str, str]:
    """
    Resolve per-role (model, provider).

    Reads ``llm.roles.<role>`` from params.yaml; falls back to ``provider.default``
    + models.yaml tier lookup.
    """
    spec = _role_yaml_spec(role)
    if spec:
        provider = provider_override or spec.get("provider") or PROVIDER
        if spec.get("model"):
            return str(spec["model"]), provider
        tier = spec.get("tier", MODEL_TIER)
        yaml_role = role
        if role == "fast_chat":
            yaml_role = "chat"
        if role == "merge" and not _get_nested(_MODELS, provider, "merge", tier):
            yaml_role = "chat"
        return _model_for(yaml_role, tier=tier, provider=provider), provider

    provider = provider_override or PROVIDER
    if role == "fast_chat":
        return _model_for("chat", provider="groq"), "groq"
    yaml_role = "chat" if role == "merge" else role
    return _model_for(yaml_role, provider=provider), provider


def role_provider(role: str) -> str:
    """Provider id for a role (after YAML resolution)."""
    return resolve_role(role)[1]


def required_llm_providers() -> list[str]:
    """Distinct providers referenced by configured roles (for validate())."""
    roles = _get_nested(_PARAMS, "llm", "roles", default={}) or {}
    if isinstance(roles, dict) and roles:
        providers = {resolve_role(r)[1] for r in roles}
    else:
        providers = {PROVIDER}
    return sorted(providers)


# Legacy single-provider view (default tier on PROVIDER).
CHAT_MODEL: str = resolve_role("chat")[0]
ROUTER_MODEL: str = resolve_role("router")[0]
GUARDRAIL_MODEL: str = resolve_role("guardrail")[0]
EXTRACTOR_MODEL: str = resolve_role("extractor")[0]
MERGE_MODEL: str = resolve_role("merge")[0]

CHAT_PROVIDER: str = resolve_role("chat")[1]
ROUTER_PROVIDER: str = resolve_role("router")[1]
GUARDRAIL_PROVIDER: str = resolve_role("guardrail")[1]
EXTRACTOR_PROVIDER: str = resolve_role("extractor")[1]
MERGE_PROVIDER: str = resolve_role("merge")[1]
FAST_CHAT_MODEL: str = resolve_role("fast_chat")[0]
FAST_CHAT_PROVIDER: str = resolve_role("fast_chat")[1]

# Tier label for merge when resolved via models.yaml (logging only).
MERGE_TIER: str = (
    (_role_yaml_spec("merge") or {}).get("tier")
    or MODEL_TIER
)


# ── LLM defaults ──────────────────────────────────────────────────────────────
LLM_TEMPERATURE: float = _get_nested(_PARAMS, "llm", "temperature", default=0.0)
LLM_MAX_TOKENS: int = _get_nested(_PARAMS, "llm", "max_tokens", default=1500)
LLM_STREAMING: bool = _get_nested(_PARAMS, "llm", "streaming", default=False)
LLM_MAX_RETRIES: int = _get_nested(_PARAMS, "llm", "max_retries", default=2)
LLM_REQUEST_TIMEOUT: int = _get_nested(_PARAMS, "llm", "request_timeout", default=30)
LLM_ENABLE_FALLBACK: bool = _get_nested(_PARAMS, "llm", "enable_fallback", default=True)
LLM_FALLBACK_TIER: str = _get_nested(_PARAMS, "llm", "fallback_tier", default="general")


# ── External travel services (bridged by the MCP servers) ─────────────────────
HOTELS_BASE_URL: str = _get_nested(
    _PARAMS, "services", "hotels_base_url",
    default="https://standing-fish-574.convex.site/hotels",
)
FLIGHTS_BASE_URL: str = _get_nested(
    _PARAMS, "services", "flights_base_url",
    default="https://standing-fish-574.convex.site/flights",
)
HTTP_TIMEOUT: int = _get_nested(_PARAMS, "services", "http_timeout", default=15)
HTTP_MAX_RETRIES: int = _get_nested(_PARAMS, "services", "http_max_retries", default=3)
HTTP_BACKOFF_SECONDS: float = _get_nested(_PARAMS, "services", "http_backoff_seconds", default=0.5)


# ── Tavily web search (secret via get_tavily_api_key(); behaviour in params.yaml)
TAVILY_SEARCH_URL: str = _get_nested(
    _PARAMS, "tavily", "search_url", default="https://api.tavily.com/search"
)
TAVILY_MAX_RESULTS: int = _get_nested(_PARAMS, "tavily", "max_results", default=5)
TAVILY_SEARCH_DEPTH: str = _get_nested(_PARAMS, "tavily", "search_depth", default="basic")
TAVILY_INCLUDE_ANSWER: bool = _get_nested(_PARAMS, "tavily", "include_answer", default=True)


# ── MCP ───────────────────────────────────────────────────────────────────────
MCP_TRANSPORT: str = _get_nested(_PARAMS, "mcp", "transport", default="stdio")


# ── Session / conversation memory ─────────────────────────────────────────────
SESSION_MAX_TURNS: int = _get_nested(_PARAMS, "session", "max_turns", default=20)
SESSION_HISTORY_WINDOW: int = _get_nested(_PARAMS, "session", "history_window", default=3)

# ── Chat streaming ────────────────────────────────────────────────────────────
CHAT_STREAM_TOKENS: bool = _get_nested(_PARAMS, "chat", "stream_tokens", default=True)


# ── Logging / observability ───────────────────────────────────────────────────
LOG_LEVEL: str = _get_nested(_PARAMS, "logging", "level", default="INFO")
OBSERVABILITY_ENABLED: bool = _get_nested(_PARAMS, "observability", "enabled", default=False)
OBSERVABILITY_PROMPTS_ENABLED: bool = _get_nested(
    _PARAMS, "observability", "prompts_enabled", default=False
)
PROMPT_CACHE_TTL_SECONDS: int = _get_nested(
    _PARAMS, "observability", "prompt_cache_ttl_seconds", default=300
)

# Timezone (display / logging helpers)
TIMEZONE = "Asia/Colombo"


# ── Secrets (from .env only) ──────────────────────────────────────────────────
_API_KEY_ENV: Dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "groq": "GROQ_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
    "tavily": "TAVILY_API_KEY",
}


def get_api_key(provider: Optional[str] = None) -> Optional[str]:
    """Return the API key for *provider* (or active LLM ``PROVIDER`` if omitted).

    Also used for non-LLM integrations, e.g. ``get_api_key("tavily")``.
    Values are stripped; empty strings count as missing.
    """
    provider = (provider or PROVIDER).lower()
    env_var = _API_KEY_ENV.get(provider, f"{provider.upper()}_API_KEY")
    raw = os.getenv(env_var)
    if raw is None:
        return None
    stripped = raw.strip().strip('"').strip("'")
    return stripped or None


def get_tavily_api_key() -> Optional[str]:
    """Tavily Search API key from ``TAVILY_API_KEY`` in project ``.env``."""
    return get_api_key("tavily")


def provider_base_url(provider: Optional[str] = None) -> Optional[str]:
    """Return the OpenAI-compatible base URL for a provider (None for openai)."""
    provider = provider or PROVIDER
    if provider == "openrouter":
        return OPENROUTER_BASE_URL
    if provider == "groq":
        return GROQ_BASE_URL
    return None  # OpenAI uses the SDK default endpoint.


# ── Validation / debug ────────────────────────────────────────────────────────
def validate() -> None:
    """Fail fast if any configured LLM role provider is missing its API key."""
    missing = []
    for prov in required_llm_providers():
        if not get_api_key(prov):
            key_map = {
                "openai": "OPENAI_API_KEY",
                "openrouter": "OPENROUTER_API_KEY",
                "groq": "GROQ_API_KEY",
                "google": "GOOGLE_API_KEY",
            }
            missing.append(key_map.get(prov, f"{prov.upper()}_API_KEY"))
    if missing:
        raise ValueError(
            "Missing required secret(s) for configured llm.roles providers: "
            + ", ".join(sorted(set(missing)))
            + ". Add them to .env (see .env.example)."
        )


def dump() -> None:
    """Log the active non-secret configuration (handy on startup)."""
    from loguru import logger

    logger.info("── BookMe AI configuration ──────────────────────────")
    logger.info("  provider default: {} (tier={})", PROVIDER, MODEL_TIER)
    logger.info("  router          : {} @ {}", ROUTER_MODEL, ROUTER_PROVIDER)
    logger.info("  guardrail       : {} @ {}", GUARDRAIL_MODEL, GUARDRAIL_PROVIDER)
    logger.info("  extractor       : {} @ {}", EXTRACTOR_MODEL, EXTRACTOR_PROVIDER)
    logger.info("  chat            : {} @ {}", CHAT_MODEL, CHAT_PROVIDER)
    logger.info("  merge           : {} @ {}", MERGE_MODEL, MERGE_PROVIDER)
    logger.info("  fast_chat       : {} @ {}", FAST_CHAT_MODEL, FAST_CHAT_PROVIDER)
    logger.info("  llm fallback    : {}", LLM_ENABLE_FALLBACK)
    logger.info("  hotels service  : {}", HOTELS_BASE_URL)
    logger.info("  flights service : {}", FLIGHTS_BASE_URL)
    logger.info(
        "  tavily search   : {} (key={})",
        TAVILY_SEARCH_URL,
        "yes" if get_tavily_api_key() else "NO",
    )
    logger.info("  mcp transport   : {}", MCP_TRANSPORT)
    logger.info("  observability   : {}", OBSERVABILITY_ENABLED)
    try:
        from infrastructure.observability import langfuse_prompts_enabled

        logger.info("  langfuse prompts: {}", langfuse_prompts_enabled())
    except Exception:
        logger.info("  langfuse prompts: {} (yaml)", OBSERVABILITY_PROMPTS_ENABLED)
    logger.info("  api keys        : {}", ", ".join(
        f"{p}={'yes' if get_api_key(p) else 'NO'}" for p in required_llm_providers()
    ))
    logger.info("──────────────────────────────────────────────────────")


def get_params() -> Dict[str, Any]:
    """Return the full parsed params.yaml (read-only view)."""
    return _PARAMS


def get_models() -> Dict[str, Any]:
    """Return the full parsed models.yaml (read-only view)."""
    return _MODELS
