"""
Bridge decision subgraph output → orchestrator ``AgentState`` (Week 13).

The chat/API layer:
  1. ``await decision_graph.ainvoke({ message, router_context })``
  2. ``map_decision_to_agent_state(decision_out, messages=..., ...)``
  3. ``await orchestrator.ainvoke({ **mapped, ... })``  (Phase 5)
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, List, Optional

from langchain_core.messages import AnyMessage

from agents.decision_state import DecisionState
from agents.prompts import get_out_of_scope_reply
from agents.state import AgentState


def map_decision_to_agent_state(
    decision_out: DecisionState,
    *,
    messages: List[AnyMessage],
    memory_context: str = "",
    user_id: str = "",
    session_id: str = "",
) -> AgentState:
    """Copy classification results into fields the orchestrator expects."""
    patch: dict[str, Any] = {
        "messages": messages,
        "memory_context": memory_context or decision_out.get("router_context") or "",
        "user_id": user_id,
        "session_id": session_id,
        "guardrail": decision_out.get("guardrail", "in_scope"),
        "verdict": decision_out.get("verdict", "proceed"),
    }

    verdict = patch["verdict"]
    if verdict == "out_of_scope":
        patch["final_answer"] = (
            decision_out.get("final_answer") or get_out_of_scope_reply()
        )
        return patch  # type: ignore[return-value]

    decision = decision_out.get("decision")
    if decision and decision.decisions:
        patch["route_decisions"] = [asdict(d) for d in decision.decisions]
    else:
        patch["route_decisions"] = []

    return patch  # type: ignore[return-value]
