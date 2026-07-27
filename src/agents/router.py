"""
Query Router — LLM-based intent classification.

Takes a user message + memory context and returns a ``MultiRouteDecision``
containing one or more ``RouteDecision`` objects. Multiple routes enable the
orchestrator to fan out to parallel hotel / flight / general_qa / web_search agent nodes.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from agents.prompts import build_router_prompt
from agents.state import AgentState
from infrastructure.llm import get_router_llm
from infrastructure.observability import observe, update_current_observation

VALID_ROUTES = frozenset({"hotel", "flight", "general_qa", "web_search"})
VALID_ACTIONS = frozenset({"search", "list_all", "book", "general"})
MAX_ROUTES = 3

_default_router: Optional["QueryRouter"] = None


@dataclass
class RouteDecision:
    """One routed intent for a downstream agent node."""

    route: str = "general_qa"
    confidence: float = 0.0
    reasoning: str = ""
    action: Optional[str] = "general"
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiRouteDecision:
    """
    One or more ``RouteDecision`` objects.

    Multi-intent queries (e.g. hotels in Colombo and a flight BOM→CMB) produce
    multiple elements for LangGraph parallel fan-out.
    """

    decisions: List[RouteDecision] = field(default_factory=list)

    @property
    def is_multi_route(self) -> bool:
        return len(self.decisions) > 1

    @property
    def primary(self) -> RouteDecision:
        return self.decisions[0] if self.decisions else RouteDecision()


def _normalize_action(route: str, action: Optional[str]) -> str:
    """Map router LLM output to a valid action per route."""
    if route == "general_qa":
        return "general"
    if route == "web_search":
        if action in (None, "general", "search"):
            return "search"
        logger.warning(
            "Invalid action '{}' for route 'web_search'; defaulting to search.",
            action,
        )
        return "search"
    if action in VALID_ACTIONS:
        return action
    if route in ("hotel", "flight"):
        logger.warning("Invalid action '{}' for route '{}'; defaulting to search.", action, route)
        return "search"
    return "general"


def _normalize_params(raw: Any) -> Dict[str, Any]:
    params = raw or {}
    if not isinstance(params, dict):
        return {}
    return params


def _fallback_multi(reasoning: str) -> MultiRouteDecision:
    return MultiRouteDecision(
        decisions=[
            RouteDecision(
                route="general_qa",
                action="general",
                confidence=0.0,
                reasoning=reasoning,
            )
        ]
    )


def _last_user_text(state: AgentState) -> str:
    messages = state.get("messages") or []
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            content = msg.content
            return content if isinstance(content, str) else str(content)
        if isinstance(msg, dict) and msg.get("role") == "user":
            return str(msg.get("content") or "")
    return ""


def get_query_router() -> QueryRouter:
    global _default_router
    if _default_router is None:
        _default_router = QueryRouter(get_router_llm())
    return _default_router


def router_node(state: AgentState) -> dict:
    """Orchestrator graph node → ``route_decisions`` on ``AgentState``.

    The decision subgraph uses ``QueryRouter.aroute`` via ``decision_graph``
    (``DecisionState``), not this node.
    """
    user_message = _last_user_text(state)
    memory_context = state.get("memory_context") or ""
    result = get_query_router().route(user_message, memory_context=memory_context)
    return {"route_decisions": [asdict(d) for d in result.decisions]}


class QueryRouter:
    """Routes user queries via LLM JSON classification."""

    def __init__(self, llm: Any) -> None:
        self.llm = llm

    @observe(name="router", as_type="generation")
    def route(
        self,
        user_message: str,
        memory_context: str = "",
    ) -> MultiRouteDecision:
        return self._call(user_message, memory_context)

    @observe(name="router", as_type="generation")
    async def aroute(
        self,
        user_message: str,
        memory_context: str = "",
    ) -> MultiRouteDecision:
        """Async routing for the API path (``llm.ainvoke``)."""
        return await self._acall(user_message, memory_context)

    def _build_messages(self, user_message: str, memory_context: str):
        """LangFuse/base system prompt + hard rules + user template (memory + message)."""
        system_prompt, user_prompt = build_router_prompt(user_message, memory_context)
        update_current_observation(
            input=user_prompt[:1000],
            model=self._model_name(),
        )
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

    def _record_usage(self, content: str, response) -> None:
        usage = {}
        if hasattr(response, "response_metadata"):
            meta = response.response_metadata or {}
            token_usage = meta.get("token_usage") or meta.get("usage", {})
            if token_usage:
                usage = {
                    "input": token_usage.get("prompt_tokens", 0),
                    "output": token_usage.get("completion_tokens", 0),
                    "total": token_usage.get("total_tokens", 0),
                }
        update_current_observation(
            output=content[:500],
            usage=usage if usage else None,
        )

    @staticmethod
    def _content(response) -> str:
        return response.content if hasattr(response, "content") else str(response)

    def _call(self, user_message: str, memory_context: str) -> MultiRouteDecision:
        try:
            response = self.llm.invoke(self._build_messages(user_message, memory_context))
            content = self._content(response)
            self._record_usage(content, response)
        except Exception as exc:
            logger.error("Router LLM call failed: {}", exc)
            return _fallback_multi(f"Router LLM error: {exc}")
        return self._parse_response(content)

    async def _acall(self, user_message: str, memory_context: str) -> MultiRouteDecision:
        try:
            response = await self.llm.ainvoke(
                self._build_messages(user_message, memory_context)
            )
            content = self._content(response)
            self._record_usage(content, response)
        except Exception as exc:
            logger.error("Router LLM async call failed: {}", exc)
            return _fallback_multi(f"Router LLM error: {exc}")
        return self._parse_response(content)

    def _model_name(self) -> str:
        if hasattr(self.llm, "model_name"):
            return self.llm.model_name
        if hasattr(self.llm, "model"):
            return self.llm.model
        return "unknown"

    def _parse_response(self, raw: str) -> MultiRouteDecision:
        """
        Parse router LLM JSON.

        Supports ``{"routes": [...]}`` or a single route object (wrapped).
        """
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()

        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            logger.warning("Router output is not JSON; falling back to general_qa.")
            return _fallback_multi("Failed to parse router output as JSON.")

        try:
            data = json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            logger.warning("Router JSON parse error: {}", exc)
            return _fallback_multi(f"JSON parse error: {exc}")

        if "routes" in data and isinstance(data["routes"], list):
            route_dicts = data["routes"][:MAX_ROUTES]
        else:
            route_dicts = [data]

        decisions: List[RouteDecision] = []
        seen_routes: set[str] = set()

        for rd in route_dicts:
            if not isinstance(rd, dict):
                continue
            route = rd.get("route", "general_qa")
            if route not in VALID_ROUTES:
                logger.warning("Invalid route '{}'; skipping.", route)
                continue
            if route in seen_routes:
                continue
            seen_routes.add(route)

            action = _normalize_action(route, rd.get("action"))
            params = _normalize_params(rd.get("params"))

            decisions.append(
                RouteDecision(
                    route=route,
                    confidence=float(rd.get("confidence", 0.5)),
                    reasoning=rd.get("reasoning", "") or "",
                    action=action,
                    params=params,
                )
            )

        if not decisions:
            return _fallback_multi("No valid routes parsed.")

        return MultiRouteDecision(decisions=decisions)
