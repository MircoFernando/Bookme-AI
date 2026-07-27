#!/usr/bin/env python3
"""Smoke test: MCP orchestrator web_search agent (tourism + Tavily)."""

from __future__ import annotations

import asyncio
import json
import sys

from langchain_core.messages import HumanMessage

from agents.orchestrator import build_agent_mcp


async def main() -> int:
    msg = "tourist locations in England for a first visit"

    # Orchestrator path: bridge already filled route_decisions from decision graph.
    patch = {
        "messages": [HumanMessage(content=msg)],
        "verdict": "proceed",
        "route_decisions": [
            {
                "route": "web_search",
                "action": "search",
                "params": {"query": msg},
                "confidence": 1.0,
                "reasoning": "test fixture",
            }
        ],
        "session_id": "test-web-search-orchestrator",
        "agent_outputs": [],
    }

    orchestrator = await build_agent_mcp()
    final = await orchestrator.arun_state(patch)
    answer = final.get("final_answer") or ""
    if len(answer) < 40:
        print("FAIL: final_answer too short:", repr(answer))
        return 1

    outputs = final.get("agent_outputs") or []
    web = next((o for o in outputs if o.get("route") == "web_search"), None)
    if not web:
        print("FAIL: no web_search agent_outputs", outputs)
        return 1

    tool_raw = web.get("tool_output") or ""
    try:
        tool_data = json.loads(tool_raw)
    except json.JSONDecodeError:
        print("FAIL: web_search tool_output not JSON:", tool_raw[:200])
        return 1
    if not tool_data.get("ok"):
        print("FAIL: Tavily tool failed:", tool_data)
        return 1

    print("OK web_search agent: tool results=", len(tool_data.get("results") or []))
    print("Answer preview:", answer[:280].replace("\n", " "), "...")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
