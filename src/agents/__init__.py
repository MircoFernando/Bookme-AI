"""
Agent layer — LangGraph orchestration, routing, guardrail, and agent nodes.

Layout:
    decision_state.py  — DecisionState (classification subgraph)
    decision_graph.py  — guardrail ∥ router → decide
    decision_bridge.py — DecisionState → AgentState
    state.py           — AgentState (orchestrator / full pipeline)
    guardrail.py, router.py, orchestrator.py (Phase 5), tools/
"""

from agents.chat_pipeline import ChatResult, run_chat_turn
from agents.decision_bridge import map_decision_to_agent_state
from agents.decision_graph import build_decision_graph, build_decision_input
from agents.decision_state import DecisionState
from agents.orchestrator import AgentOrchestrator, AgentResponse, build_agent_mcp, build_orchestrator
from agents.state import AgentState

__all__ = [
    "ChatResult",
    "run_chat_turn",
    "AgentOrchestrator",
    "AgentResponse",
    "AgentState",
    "DecisionState",
    "build_agent_mcp",
    "build_decision_graph",
    "build_decision_input",
    "build_orchestrator",
    "map_decision_to_agent_state",
]
