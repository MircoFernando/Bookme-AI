#!/usr/bin/env python3
"""Smoke test: Week 13 decision subgraph + bridge to AgentState."""

from __future__ import annotations

import asyncio
import sys

from langchain_core.messages import HumanMessage

from agents.decision_bridge import map_decision_to_agent_state
from agents.decision_graph import build_decision_graph, build_decision_input


async def _run(message: str) -> dict:
    graph = build_decision_graph()
    decision_out = await graph.ainvoke(build_decision_input(message=message))
    agent_patch = map_decision_to_agent_state(
        decision_out,
        messages=[HumanMessage(content=message)],
        memory_context="",
    )
    return {"decision": decision_out, "agent": agent_patch}


async def _router_primary_route(message: str) -> str:
    from agents.router import get_query_router

    multi = await get_query_router().aroute(message, "")
    return multi.primary.route


async def main() -> int:
    off = await _run("What is the capital of France?")
    d_off = off["decision"]
    a_off = off["agent"]
    if d_off.get("verdict") != "out_of_scope":
        print("FAIL: expected out_of_scope for trivia, got", d_off.get("verdict"))
        return 1
    if not a_off.get("final_answer"):
        print("FAIL: expected final_answer on agent patch")
        return 1
    print("OK off-topic:", d_off.get("verdict"), "final_answer len=", len(a_off["final_answer"]))

    travel = await _run(
        "Find hotels in Colombo and a flight from BOM to CMB on 2026-08-01"
    )
    d_tr = travel["decision"]
    a_tr = travel["agent"]
    if d_tr.get("verdict") != "proceed":
        print("FAIL: expected proceed for travel query, got", d_tr.get("verdict"))
        return 1
    routes = a_tr.get("route_decisions") or []
    route_names = {r.get("route") for r in routes}
    if len(routes) < 2 or not {"hotel", "flight"} <= route_names:
        print("FAIL: expected hotel+flight routes, got", routes)
        return 1
    print("OK travel: verdict=proceed routes=", route_names)

    hi_route = await _router_primary_route("hi")
    if hi_route != "general_qa":
        print("FAIL: expected general_qa for 'hi', got", hi_route)
        return 1
    print("OK router chitchat: hi →", hi_route)

    tourism_route = await _router_primary_route("tourist locations in England")
    if tourism_route != "web_search":
        print("FAIL: expected web_search for tourism, got", tourism_route)
        return 1
    print("OK router tourism: tourist locations in England →", tourism_route)

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
