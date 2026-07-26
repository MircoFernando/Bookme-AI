"""
Application configuration — loads from YAML + environment.

CONFIGURATION POLICY
====================
- Behaviour/config lives in ``config/params.yaml`` and ``config/models.yaml``.
- Secrets (API keys, credentialed URLs) live ONLY in ``.env`` and are read
  via ``os.getenv()``. Never commit secrets.

This mirrors the Week 13 (Nawaloka) infrastructure pattern, trimmed to what
TripWeaver needs: a provider-flexible multi-model LLM setup, the external
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
    """Resolve a model name for a role (chat|router|guardrail|extractor)."""
    provider = provider or PROVIDER
    tier = tier or MODEL_TIER
    # Fall back to the "general" tier, then a sane hardcoded default.
    return (
        _get_nested(_MODELS, provider, role, tier)
        or _get_nested(_MODELS, provider, role, "general")
        or "gpt-4o-mini"
    )


# Active model names per role (recomputed on import from YAML).
CHAT_MODEL: str = _model_for("chat")
ROUTER_MODEL: str = _model_for("router")
GUARDRAIL_MODEL: str = _model_for("guardrail")
EXTRACTOR_MODEL: str = _model_for("extractor")


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


# ── MCP ───────────────────────────────────────────────────────────────────────
MCP_TRANSPORT: str = _get_nested(_PARAMS, "mcp", "transport", default="stdio")


# ── Session / conversation memory ─────────────────────────────────────────────
SESSION_MAX_TURNS: int = _get_nested(_PARAMS, "session", "max_turns", default=20)
SESSION_HISTORY_WINDOW: int = _get_nested(_PARAMS, "session", "history_window", default=3)


# ── Logging / observability ───────────────────────────────────────────────────
LOG_LEVEL: str = _get_nested(_PARAMS, "logging", "level", default="INFO")
OBSERVABILITY_ENABLED: bool = _get_nested(_PARAMS, "observability", "enabled", default=False)
OBSERVABILITY_PROMPTS_ENABLED: bool = _get_nested(
    _PARAMS, "observability", "prompts_enabled", default=False
)
PROMPT_CACHE_TTL_SECONDS: int = _get_nested(
    _PARAMS, "observability", "prompt_cache_ttl_seconds", default=300
)


# ── Secrets (from .env only) ──────────────────────────────────────────────────
def get_api_key(provider: Optional[str] = None) -> Optional[str]:
    """Return the API key env var for the given (or active) provider."""
    provider = provider or PROVIDER
    key_map = {
        "openai": "OPENAI_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "groq": "GROQ_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
    }
    env_var = key_map.get(provider, f"{provider.upper()}_API_KEY")
    return os.getenv(env_var)


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
    """Fail fast if the active provider's API key is missing."""
    if not get_api_key():
        env_var = f"{PROVIDER.upper()}_API_KEY"
        raise ValueError(
            f"Missing required secret: {env_var}. Add it to your .env file "
            f"(see .env.example)."
        )


def dump() -> None:
    """Log the active non-secret configuration (handy on startup)."""
    from loguru import logger

    logger.info("── TripWeaver configuration ──────────────────────────")
    logger.info("  provider        : {} (tier={})", PROVIDER, MODEL_TIER)
    logger.info("  chat model      : {}", CHAT_MODEL)
    logger.info("  router model    : {}", ROUTER_MODEL)
    logger.info("  guardrail model : {}", GUARDRAIL_MODEL)
    logger.info("  extractor model : {}", EXTRACTOR_MODEL)
    logger.info("  llm fallback    : {}", LLM_ENABLE_FALLBACK)
    logger.info("  hotels service  : {}", HOTELS_BASE_URL)
    logger.info("  flights service : {}", FLIGHTS_BASE_URL)
    logger.info("  mcp transport   : {}", MCP_TRANSPORT)
    logger.info("  observability   : {}", OBSERVABILITY_ENABLED)
    try:
        from infrastructure.observability import langfuse_prompts_enabled

        logger.info("  langfuse prompts: {}", langfuse_prompts_enabled())
    except Exception:
        logger.info("  langfuse prompts: {} (yaml)", OBSERVABILITY_PROMPTS_ENABLED)
    logger.info("  api key present : {}", "yes" if get_api_key() else "NO")
    logger.info("──────────────────────────────────────────────────────")


def get_params() -> Dict[str, Any]:
    """Return the full parsed params.yaml (read-only view)."""
    return _PARAMS


def get_models() -> Dict[str, Any]:
    """Return the full parsed models.yaml (read-only view)."""
    return _MODELS
