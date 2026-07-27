"""
AgentState — the shared state for the BookMe AI LangGraph.

Every node reads from and writes to this TypedDict; it is the single source of
truth passed along the graph ("the conveyor belt"). Design notes:

- ``messages`` uses ``add_messages`` so LangGraph merges conversation turns.
- ``agent_outputs`` uses ``operator.add`` as a **reducer**: when the supervisor
  fans out to multiple agent nodes in parallel (e.g. a query asking for BOTH a
  hotel and a flight), each node appends its own result and LangGraph
  concatenates the lists on fan-in. The ``merge_responses`` node then
  synthesises them into one answer.
- Routing signals (``route_decisions``) let downstream nodes know which agents
  were selected and with what extracted parameters.
- Travel slots (city/dates/ids/guest/passenger) are the extracted booking
  fields; agents ask a follow-up question when required ones are missing
  rather than fabricating values.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, List, Optional

from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    # ── Conversation ──────────────────────────────────────────────────────────
    messages: Annotated[List[AnyMessage], add_messages]

    # Identifiers threaded through every node.
    user_id: str
    session_id: str

    # Formatted recent history (from SessionStore), injected into prompts.
    memory_context: Optional[str]

    # ── Gating ────────────────────────────────────────────────────────────────
    guardrail: Optional[str]        # "in_scope" | "out_of_scope"
    verdict: Optional[str]          # "out_of_scope" | "proceed"

    # ── Routing ───────────────────────────────────────────────────────────────
    # One dict per detected intent:
    #   {"route": "hotel"|"flight"|"general_qa"|"web_search",
    #    "action": "search"|"list_all"|"book"|"general",
    #    "params": {...}, "reasoning": str, "confidence": float}
    route_decisions: Optional[List[dict]]

    # ── Fan-out collector (parallel agents append here) ─────────────────────────
    # Each agent node appends:
    #   {"route": str, "tool_output": Any, "answer": str, "status": "ok"|"failed"}
    agent_outputs: Annotated[List[dict], operator.add]

    # ── Results surfaced to the API/UI ──────────────────────────────────────────
    hotel_results: List[dict]
    flight_results: List[dict]
    final_answer: Optional[str]
