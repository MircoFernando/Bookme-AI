"""
Decision subgraph state (separate from orchestrator ``AgentState``).

Separate from ``AgentState``: the decision graph only classifies the latest
user turn. The orchestrator graph (Phase 5) runs on ``AgentState`` after
``map_decision_to_agent_state()`` copies verdict + routes across the boundary.
"""

from __future__ import annotations

from typing import Literal, Optional

from typing_extensions import TypedDict

from agents.router import MultiRouteDecision

GuardrailVerdict = Literal["in_scope", "out_of_scope"]
DecisionVerdict = Literal["out_of_scope", "proceed"]


class DecisionState(TypedDict, total=False):
    """Minimal state for parallel guardrail + intent router + decide."""

    # ── Inputs (chat layer fills before ainvoke) ─────────────────────────────
    message: str
    router_context: str

    # ── Parallel classifier outputs ──────────────────────────────────────────
    guardrail: GuardrailVerdict
    decision: MultiRouteDecision

    # ── Optional timings (SSE / observability) ───────────────────────────────
    guardrail_ms: int
    route_ms: int

    # ── decide_node ────────────────────────────────────────────────────────────
    verdict: DecisionVerdict
    primary_route: str
    final_answer: Optional[str]
