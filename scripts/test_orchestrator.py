#!/usr/bin/env python3
"""Smoke test: decision graph → bridge → MCP orchestrator (multi-intent)."""

from __future__ import annotations

import asyncio
import sys

from langchain_core.messages import HumanMessage

from agents.decision_bridge import map_decision_to_agent_state
from agents.decision_graph import build_decision_graph, build_decision_input
from agents.orchestrator import build_agent_mcp


async def main() -> int:
    msg = "Find hotels in Colombo and a flight from BOM to CMB on 2026-08-01"

    graph = build_decision_graph()
    decision_out = await graph.ainvoke(build_decision_input(message=msg))
    patch = map_decision_to_agent_state(
        decision_out,
        messages=[HumanMessage(content=msg)],
        session_id="test-orchestrator",
    )

    if patch.get("verdict") != "proceed":
        print("FAIL: expected proceed, got", patch.get("verdict"))
        return 1

    routes = {r.get("route") for r in (patch.get("route_decisions") or [])}
    if not {"hotel", "flight"} <= routes:
        print("FAIL: expected hotel+flight routes, got", routes)
        return 1
    print("OK decision routes:", routes)

    orchestrator = await build_agent_mcp()
    final = await orchestrator.arun_state(patch)
    answer = final.get("final_answer") or ""
    if len(answer) < 20:
        print("FAIL: final_answer too short:", repr(answer))
        return 1

    outputs = final.get("agent_outputs") or []
    out_routes = {o.get("route") for o in outputs}
    if not {"hotel", "flight"} <= out_routes:
        print("FAIL: expected hotel+flight agent_outputs, got", out_routes)
        return 1

    print("OK orchestrator: agent_outputs=", out_routes)
    print("Answer preview:", answer[:280].replace("\n", " "), "...")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
