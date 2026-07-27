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

_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PYTHON = sys.executable


def build_mcp_server_config() -> dict:
    """Dict suitable for ``MultiServerMCPClient(server_config)``."""
    return {
        "bookme-ai-hotels": {
            "command": _PYTHON,
            "args": ["-m", "mcp_servers.hotel_server"],
            "transport": "stdio",
            "cwd": _SRC_DIR,
        },
        "bookme-ai-flights": {
            "command": _PYTHON,
            "args": ["-m", "mcp_servers.flight_server"],
            "transport": "stdio",
            "cwd": _SRC_DIR,
        },
        "bookme-ai-web-search": {
            "command": _PYTHON,
            "args": ["-m", "mcp_servers.web_search_server"],
            "transport": "stdio",
            "cwd": _SRC_DIR,
        },
    }
