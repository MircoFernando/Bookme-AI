"""
Agent layer — LangGraph orchestration, routing, guardrail, and agent nodes.

Populated across the enhancement sprint:
    state.py           — shared AgentState (this Day-1 deliverable)
    guardrail.py       — fail-open scope classifier            (Day 3)
    router.py          — intent classification                (Day 3)
    decision_graph.py  — parallel guardrail + router → decide  (Day 3)
    orchestrator.py    — supervisor → fan-out agents → merge   (Day 4)
    tools/             — hotel/flight business logic           (Day 2)
"""

from agents.state import AgentState

__all__ = ["AgentState"]
