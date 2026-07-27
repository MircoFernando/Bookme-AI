"""
Single async entry for one chat turn: decision graph → orchestrator (or OOS short-circuit).

Used by the FastAPI chat routers (Phase 6); keeps HTTP handlers thin.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Literal, Optional

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from agents.decision_bridge import map_decision_to_agent_state
from agents.decision_graph import EmitFn, build_decision_input
from agents.orchestrator import AgentOrchestrator, _format_session_memory
from infrastructure.observability import observe, update_current_trace

Verdict = Literal["proceed", "out_of_scope"]


async def _noop_emit(_: Dict[str, Any]) -> None:
    return None


@dataclass
class ChatResult:
    """One user turn — maps cleanly to ``api.schemas.ChatResponse``."""

    answer: str
    verdict: Verdict
    route: str
    routes: List[str]
    session_id: str
    latency_ms: int
    timings: Dict[str, int] = field(default_factory=dict)
    trace_id: Optional[str] = None
    tool_output: str = ""


def _routes_from_patch(patch: dict, *, verdict: Verdict) -> tuple[str, List[str]]:
    decisions = patch.get("route_decisions") or []
    names = [d.get("route", "general_qa") for d in decisions if d.get("route")]
    if verdict == "out_of_scope" and not names:
        return "out_of_scope", ["out_of_scope"]
    if not names:
        return "general_qa", ["general_qa"]
    return names[0], names


def _result_from_orchestrator_final(
    final_state: dict,
    *,
    verdict: Verdict,
    session_id: str,
    total_ms: int,
    timings: Dict[str, int],
    orchestrator: AgentOrchestrator,
) -> ChatResult:
    orch_ms = timings.get("orchestrator_ms", 0)
    agent = orchestrator._to_agent_response(final_state, orch_ms)
    return ChatResult(
        answer=agent.answer,
        verdict=verdict,
        route=agent.route,
        routes=agent.routes,
        session_id=session_id,
        latency_ms=total_ms,
        timings=timings,
        tool_output=agent.tool_output or "",
    )


@observe(name="chat_turn")
async def run_chat_turn(
    *,
    message: str,
    user_id: str,
    session_id: str,
    decision_graph: Any,
    orchestrator: AgentOrchestrator,
    session_store: Any = None,
    emit: EmitFn | None = None,
) -> ChatResult:
    """
    Run decision graph, then orchestrator unless ``verdict == out_of_scope``.

    Loads ``memory_context`` from ``session_store`` when provided.
    On proceed, orchestrator ``save_memory_node`` persists the exchange;
    on out-of-scope, this module writes the pair directly.
    """
    emit_fn: EmitFn = emit or _noop_emit
    t_total = time.perf_counter()
    timings: Dict[str, int] = {}

    memory_context = ""
    if session_store and session_id:
        memory_context = _format_session_memory(session_store, user_id, session_id)

    update_current_trace(
        user_id=user_id or None,
        session_id=session_id or None,
        metadata={"phase": "chat_pipeline"},
    )

    await emit_fn(
        {
            "type": "stage_start",
            "stage": "decision",
            "label": "Classifying your request…",
        }
    )
    t_dec = time.perf_counter()
    config: RunnableConfig = {"configurable": {"emit": emit_fn}}
    decision_out = await decision_graph.ainvoke(
        build_decision_input(message=message, router_context=memory_context),
        config=config,
    )
    timings["decision_ms"] = int((time.perf_counter() - t_dec) * 1000)
    await emit_fn(
        {
            "type": "stage_done",
            "stage": "decision",
            "ms": timings["decision_ms"],
            "detail": {"verdict": decision_out.get("verdict")},
        }
    )

    patch = map_decision_to_agent_state(
        decision_out,
        messages=[HumanMessage(content=message)],
        memory_context=memory_context,
        user_id=user_id,
        session_id=session_id,
    )
    verdict: Verdict = (
        "out_of_scope" if patch.get("verdict") == "out_of_scope" else "proceed"
    )

    if verdict == "out_of_scope":
        answer = patch.get("final_answer") or ""
        if session_store and session_id and answer:
            session_store.add_exchange(user_id, session_id, message, answer)
        route, routes = _routes_from_patch(patch, verdict=verdict)
        timings["orchestrator_ms"] = 0
        timings["total_ms"] = int((time.perf_counter() - t_total) * 1000)
        update_current_trace(
            metadata={"verdict": verdict, "routes": routes},
            tags=[verdict],
        )
        return ChatResult(
            answer=answer,
            verdict=verdict,
            route=route,
            routes=routes,
            session_id=session_id,
            latency_ms=timings["total_ms"],
            timings=timings,
        )

    await emit_fn(
        {
            "type": "stage_start",
            "stage": "orchestrator",
            "label": "Running travel agents…",
        }
    )
    t_orch = time.perf_counter()
    final_state = await orchestrator.arun_state(patch)
    timings["orchestrator_ms"] = int((time.perf_counter() - t_orch) * 1000)
    await emit_fn(
        {
            "type": "stage_done",
            "stage": "orchestrator",
            "ms": timings["orchestrator_ms"],
        }
    )

    timings["total_ms"] = int((time.perf_counter() - t_total) * 1000)
    routes = _routes_from_patch(final_state, verdict=verdict)[1]
    update_current_trace(
        metadata={"verdict": verdict, "routes": routes},
        tags=[verdict],
    )
    return _result_from_orchestrator_final(
        final_state,
        verdict=verdict,
        session_id=session_id,
        total_ms=timings["total_ms"],
        timings=timings,
        orchestrator=orchestrator,
    )
