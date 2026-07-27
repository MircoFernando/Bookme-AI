#!/usr/bin/env python3
"""Smoke test: SessionStore + decision graph + chat_pipeline (mock orchestrator)."""

from __future__ import annotations

import asyncio
import sys
from typing import Any

from agents.chat_pipeline import run_chat_turn
from agents.decision_graph import build_decision_graph
from agents.orchestrator import AgentOrchestrator
from agents.state import AgentState
from infrastructure.session_store import SessionStore


class _RecordingOrchestrator:
    """Minimal stand-in — records whether MCP path would run."""

    def __init__(self) -> None:
        self.calls = 0
        self._inner = AgentOrchestrator(
            llm_chat=None,
            llm_merge=None,
            router=None,
            hotel_tool=None,
            flight_tool=None,
            session_store=None,
        )

    async def arun_state(self, state: AgentState) -> AgentState:
        self.calls += 1
        merged: dict[str, Any] = dict(state)
        merged["final_answer"] = "Mock orchestrator answer for testing."
        merged["agent_outputs"] = [{"route": "hotel", "tool_output": "{}"}]
        merged.setdefault("route_decisions", [{"route": "hotel", "action": "search"}])
        return merged  # type: ignore[return-value]

    def _to_agent_response(self, final_state: dict, latency_ms: int):
        return self._inner._to_agent_response(final_state, latency_ms)


async def main() -> int:
    graph = build_decision_graph()
    store = SessionStore()
    orch = _RecordingOrchestrator()
    user = "pipeline-test-user"
    session = "pipeline-test-session"

    oos = await run_chat_turn(
        message="What is the capital of France?",
        user_id=user,
        session_id=session,
        decision_graph=graph,
        orchestrator=orch,  # type: ignore[arg-type]
        session_store=store,
    )
    if oos.verdict != "out_of_scope":
        print("FAIL: expected out_of_scope, got", oos.verdict)
        return 1
    if orch.calls != 0:
        print("FAIL: orchestrator invoked on OOS")
        return 1
    if not oos.answer:
        print("FAIL: empty OOS answer")
        return 1
    pairs = store.recent_pairs(user, session)
    if len(pairs) != 1:
        print("FAIL: expected OOS exchange stored, pairs=", pairs)
        return 1
    print("OK OOS: orchestrator skipped, memory stored")

    travel = await run_chat_turn(
        message="Find hotels in Colombo",
        user_id=user,
        session_id=session,
        decision_graph=graph,
        orchestrator=orch,  # type: ignore[arg-type]
        session_store=store,
    )
    if travel.verdict != "proceed":
        print("FAIL: expected proceed, got", travel.verdict)
        return 1
    if orch.calls != 1:
        print("FAIL: expected one orchestrator call, got", orch.calls)
        return 1
    if travel.timings.get("decision_ms", 0) <= 0:
        print("FAIL: missing decision_ms timing")
        return 1
    print(
        "OK travel: route=",
        travel.route,
        "timings=",
        travel.timings,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
