"""
Decision LangGraph — guardrail and router subgraph for BookMe AI.

Small ``DecisionState`` subgraph: parallel guardrail + intent router, then
``decide``. Output is mapped into ``AgentState`` via ``decision_bridge`` for
the Phase 5 orchestrator (MCP agents, merge).

Topology::

    START
      ├── guardrail   (scope: in_scope | out_of_scope)
      ├── router      (MultiRouteDecision: hotel | flight | general_qa)
              │ fan-in
              ▼
          decide      (verdict: proceed | out_of_scope; final_answer if blocked)
              ▼
             END

Invoke with plain strings (not full conversation objects)::

    await graph.ainvoke({
        "message": user_text,
        "router_context": memory_context,
    })
"""

from __future__ import annotations

import time
from typing import Any, Awaitable, Callable, Dict, Optional

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agents.decision_state import DecisionState, DecisionVerdict, GuardrailVerdict
from agents.guardrail import Guardrail, get_guardrail
from agents.prompts import get_out_of_scope_reply
from agents.router import QueryRouter, _fallback_multi, get_query_router

EmitFn = Callable[[Dict[str, Any]], Awaitable[None]]


def _ms(t0: float) -> int:
    return int((time.perf_counter() - t0) * 1000)


def _emit_from_config(config: Optional[RunnableConfig]) -> EmitFn:
    if config and (cfg := config.get("configurable")):
        fn = cfg.get("emit")
        if fn is not None:
            return fn

    async def _noop(_: Dict[str, Any]) -> None:
        return None

    return _noop


def _stage_label_safe(stage: str) -> str:
    try:
        from api.event_labels import stage_label

        return stage_label(stage)
    except Exception:
        return stage.replace("_", " ").capitalize()


def make_guardrail_node(guardrail: Guardrail):
    async def guardrail_node(
        state: DecisionState,
        config: Optional[RunnableConfig] = None,
    ) -> Dict[str, Any]:
        emit = _emit_from_config(config)
        t0 = time.perf_counter()
        await emit(
            {
                "type": "stage_start",
                "stage": "guardrail",
                "label": _stage_label_safe("guardrail"),
            }
        )
        try:
            verdict: GuardrailVerdict = await guardrail.aclassify(
                state["message"],
                state.get("router_context", "") or "",
            )
        except Exception as exc:
            logger.warning("Guardrail node failed (defaulting in_scope): {}", exc)
            verdict = "in_scope"
        ms = _ms(t0)
        await emit(
            {
                "type": "stage_done",
                "stage": "guardrail",
                "ms": ms,
                "detail": {"verdict": verdict},
            }
        )
        return {"guardrail": verdict, "guardrail_ms": ms}

    return guardrail_node


def make_router_node(router: QueryRouter):
    async def router_node(
        state: DecisionState,
        config: Optional[RunnableConfig] = None,
    ) -> Dict[str, Any]:
        emit = _emit_from_config(config)
        t0 = time.perf_counter()
        await emit(
            {
                "type": "stage_start",
                "stage": "route",
                "label": _stage_label_safe("route"),
            }
        )
        try:
            decision = await router.aroute(
                state["message"],
                state.get("router_context", ""),
            )
        except Exception as exc:
            logger.warning("Router node failed (defaulting general_qa): {}", exc)
            decision = _fallback_multi(f"Router node error: {exc}")
        ms = _ms(t0)
        primary = decision.primary
        await emit(
            {
                "type": "stage_done",
                "stage": "route",
                "ms": ms,
                "detail": {
                    "route": primary.route,
                    "action": primary.action,
                    "reasoning": (primary.reasoning or "")[:160],
                },
            }
        )
        return {"decision": decision, "route_ms": ms}

    return router_node


def decide_node(
    state: DecisionState,
    config: Optional[RunnableConfig] = None,
) -> Dict[str, Any]:
    """Gate on guardrail; router can override a false-negative guardrail for tool routes."""
    _ = config
    guardrail_v = state.get("guardrail", "in_scope")
    decision = state.get("decision")
    primary = decision.primary if decision else None
    primary_route = primary.route if primary else "general_qa"

    if guardrail_v == "out_of_scope":
        # Router already chose a travel tool path — prefer proceeding over a
        # guardrail false negative (e.g. food in London classified as OOS).
        if primary_route in ("hotel", "flight", "web_search"):
            logger.info(
                "Guardrail out_of_scope but router chose {}; proceeding",
                primary_route,
            )
            return {"verdict": "proceed", "primary_route": primary_route}
        return {
            "verdict": "out_of_scope",
            "primary_route": primary_route,
            "final_answer": get_out_of_scope_reply(),
        }

    verdict: DecisionVerdict = "proceed"
    return {"verdict": verdict, "primary_route": primary_route}


def build_decision_graph(
    *,
    guardrail: Optional[Guardrail] = None,
    router: Optional[QueryRouter] = None,
):
    """Compile the decision subgraph (inject instances for tests)."""
    guardrail = guardrail or get_guardrail()
    router = router or get_query_router()

    g = StateGraph(DecisionState)
    g.add_node("guardrail", make_guardrail_node(guardrail))
    g.add_node("router", make_router_node(router))
    g.add_node("decide", decide_node)

    g.add_edge(START, "guardrail")
    g.add_edge(START, "router")
    g.add_edge("guardrail", "decide")
    g.add_edge("router", "decide")
    g.add_edge("decide", END)

    return g.compile()


def build_decision_input(*, message: str, router_context: str = "") -> DecisionState:
    """Helper for chat layer / tests."""
    return {"message": message, "router_context": router_context}
