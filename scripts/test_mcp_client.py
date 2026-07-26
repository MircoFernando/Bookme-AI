#!/usr/bin/env python3
"""Smoke test: connect to hotel + flight MCP servers and invoke list_* tools."""

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


async def main() -> None:
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
    }
    missing = expected - set(names)
    if missing:
        raise SystemExit(f"Missing tools: {missing}")

    by_name = {t.name: t for t in tools}
    hotels_raw = await by_name["list_hotels"].ainvoke({})
    flights_raw = await by_name["list_flights"].ainvoke({})

    def first_count(raw) -> int:
        if isinstance(raw, list):
            text = "\n".join(
                item.get("text", str(item)) for item in raw if isinstance(item, dict)
            )
        else:
            text = str(raw)
        data = json.loads(text)
        return data.get("count", len(data.get("hotels") or data.get("flights") or []))

    print("list_hotels count:", first_count(hotels_raw))
    print("list_flights count:", first_count(flights_raw))
    print("MCP smoke test OK")


if __name__ == "__main__":
    asyncio.run(main())
