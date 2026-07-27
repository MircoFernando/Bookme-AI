#!/usr/bin/env python3
"""Smoke test: connect to hotel + flight + web search MCP servers."""

from __future__ import annotations

import asyncio
import json
import os
import sys

# Project root on path so ``PYTHONPATH=src`` or running from repo root works.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)


def _text(raw) -> str:
    if isinstance(raw, list):
        return "\n".join(
            item.get("text", str(item)) for item in raw if isinstance(item, dict)
        )
    return str(raw)


async def main() -> None:
    from infrastructure.config import get_tavily_api_key
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from mcp_servers.mcp_config import build_mcp_server_config

    config = build_mcp_server_config()
    print("MCP servers:", list(config.keys()))

    client = MultiServerMCPClient(config)
    tools = await client.get_tools()
    names = sorted(t.name for t in tools)
    print("Tools loaded:", names)

    expected = {
        "list_hotels",
        "search_hotels",
        "book_hotel",
        "list_flights",
        "search_flights",
        "book_flight",
        "search_web",
    }
    missing = expected - set(names)
    if missing:
        raise SystemExit(f"Missing tools: {missing}")

    by_name = {t.name: t for t in tools}
    hotels_raw = await by_name["list_hotels"].ainvoke({})
    flights_raw = await by_name["list_flights"].ainvoke({})

    def first_count(raw) -> int:
        data = json.loads(_text(raw))
        return data.get("count", len(data.get("hotels") or data.get("flights") or []))

    print("list_hotels count:", first_count(hotels_raw))
    print("list_flights count:", first_count(flights_raw))

    if get_tavily_api_key():
        web_raw = await by_name["search_web"].ainvoke(
            {"query": "London tourist attractions"}
        )
        web_data = json.loads(_text(web_raw))
        if not web_data.get("ok"):
            raise SystemExit(f"search_web failed: {web_data}")
        n = len(web_data.get("results") or [])
        print("search_web results:", n, "(live Tavily)")
    else:
        print("search_web: skipped live invoke (TAVILY_API_KEY not set)")

    print("MCP smoke test OK")


if __name__ == "__main__":
    asyncio.run(main())
