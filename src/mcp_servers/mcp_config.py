"""
MCP client configuration — stdio subprocess launch for BookMe AI.

Consumed by ``langchain_mcp_adapters.client.MultiServerMCPClient`` (Day 4
``build_agent_mcp()``). Agents never import Convex URLs directly; they call
MCP tools discovered from these servers.

Servers:
  1. bookme-ai-hotels      — list_hotels, search_hotels, book_hotel
  2. bookme-ai-flights     — list_flights, search_flights, book_flight
  3. bookme-ai-web-search  — search_web
"""

from __future__ import annotations

import os
import sys

from loguru import logger

_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PYTHON = sys.executable

# MCP stdio spawns only inherit a small default set (HOME, PATH, …) — not app
# secrets. Local dev often works because MCP servers call load_dotenv(".env"), but
# Docker/production images have no .env file; secrets must be forwarded explicitly.
_MCP_ENV_KEYS = (
    "TAVILY_API_KEY",
    "LANGFUSE_SECRET_KEY",
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_BASE_URL",
    "LANGFUSE_PROMPTS",
)


def mcp_subprocess_env() -> dict[str, str]:
    """Env vars forwarded to MCP stdio child processes."""
    env: dict[str, str] = {}
    for key in _MCP_ENV_KEYS:
        val = os.environ.get(key)
        if val:
            env[key] = val
    if not env.get("TAVILY_API_KEY"):
        logger.warning(
            "TAVILY_API_KEY missing in API process — web search MCP will fail "
            "(set in .env / container env and rebuild is not required after fix)"
        )
    return env


def _stdio_server(module: str) -> dict:
    return {
        "command": _PYTHON,
        "args": ["-m", module],
        "transport": "stdio",
        "cwd": _SRC_DIR,
        "env": mcp_subprocess_env(),
    }


def build_mcp_server_config() -> dict:
    """Dict suitable for ``MultiServerMCPClient(server_config)``."""
    return {
        "bookme-ai-hotels": _stdio_server("mcp_servers.hotel_server"),
        "bookme-ai-flights": _stdio_server("mcp_servers.flight_server"),
        "bookme-ai-web-search": _stdio_server("mcp_servers.web_search_server"),
    }
