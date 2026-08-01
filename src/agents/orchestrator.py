"""
BookMe AI orchestrator — LangGraph fan-out after the decision subgraph.

Phase 6 chat runs ``decision_graph`` → ``decision_bridge`` → this graph.
``route_decisions`` are usually pre-filled by the bridge; the supervisor
re-routes only when the graph is invoked standalone (CLI / tests).

Topology::

    START → (out_of_scope? END)
         → recall → supervisor → [hotel_agent | flight_agent | general_qa_agent | web_search_agent]
                                              ↘ merge_responses → save_memory → END

Tools reach Convex only via MCP adapters in ``build_agent_mcp()`` (assessment E1).
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agents.prompts import (
    build_flight_agent_system_prompt,
    build_general_qa_system_prompt,
    build_hotel_agent_system_prompt,
    build_merge_system_prompt,
    build_web_search_agent_system_prompt,
)
from agents.tools.flight_tool import _looks_like_convex_id, resolve_flight_id
from agents.state import AgentState
from infrastructure import config as app_config
from infrastructure.observability import observe

EmitFn = Callable[[Dict[str, Any]], Awaitable[None]]


# Router actions (search | list_all | book | general) → MCP / HotelTool.dispatch names
_HOTEL_ACTION_TO_TOOL = {
    "list_all": "list_hotels",
    "search": "search_hotels",
    "book": "book_hotel",
}
_FLIGHT_ACTION_TO_TOOL = {
    "list_all": "list_flights",
    "search": "search_flights",
    "book": "book_flight",
}
_WEB_SEARCH_ACTION_TO_TOOL = {
    "search": "search_web",
    "general": "search_web",
}

_ROUTE_TO_NODE = {
    "hotel": "hotel",
    "flight": "flight",
    "general_qa": "general_qa",
    "web_search": "web_search",
}


@dataclass
class AgentResponse:
    """One orchestrator turn — metadata for API / scripts."""

    answer: str
    route: str = "general_qa"
    routes: List[str] = field(default_factory=list)
    action: Optional[str] = None
    tool_output: str = ""
    memory_context: str = ""
    latency_ms: int = 0


def _text_from_content_block(block: Any) -> str:
    """Extract user-visible text from one OpenAI/Gemini content block."""
    if isinstance(block, str):
        return block
    if isinstance(block, dict):
        text = block.get("text")
        if text:
            return str(text)
        if block.get("type") == "text" and block.get("content"):
            return str(block["content"])
        return ""
    text = getattr(block, "text", None)
    if text:
        return str(text)
    content = getattr(block, "content", None)
    if isinstance(content, str) and content:
        return content
    return ""


def _llm_content_to_str(content: Any) -> str:
    """Normalize OpenAI/Gemini message content to plain text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for block in content:
            text = _text_from_content_block(block)
            if text:
                parts.append(text)
        return "\n".join(parts)
    if isinstance(content, dict):
        return _text_from_content_block(content)
    text = getattr(content, "text", None)
    if text:
        return str(text)
    return ""


def _emit_from_config(config: Optional[RunnableConfig]) -> Optional[EmitFn]:
    if config and (cfg := config.get("configurable")):
        fn = cfg.get("emit")
        if fn is not None:
            return fn
    return None


def _route_decision_count(state: AgentState) -> int:
    return len(state.get("route_decisions") or [])


async def _invoke_llm_text(llm: Any, messages: list) -> str:
    response = await llm.ainvoke(messages)
    return _llm_content_to_str(
        response.content if hasattr(response, "content") else response
    )


async def _stream_llm_text(llm: Any, messages: list, emit: EmitFn) -> str:
    await emit({"type": "token_start"})
    parts: List[str] = []
    async for chunk in llm.astream(messages):
        delta = _llm_content_to_str(
            chunk.content if hasattr(chunk, "content") else chunk
        )
        if not delta:
            continue
        parts.append(delta)
        await emit({"type": "token_delta", "delta": delta})
    text = "".join(parts)
    await emit({"type": "token_end"})
    return text


async def _synthesize_llm_text(
    llm: Any,
    messages: list,
    *,
    emit: Optional[EmitFn],
    stream: bool,
) -> str:
    if emit and stream and app_config.CHAT_STREAM_TOKENS:
        return await _stream_llm_text(llm, messages, emit)
    return await _invoke_llm_text(llm, messages)


def _last_user_text(state: AgentState) -> str:
    messages = state.get("messages") or []
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            content = msg.content
            return content if isinstance(content, str) else str(content)
        if isinstance(msg, dict) and msg.get("role") == "user":
            return str(msg.get("content") or "")
    return ""


def _format_session_memory(
    session_store: Any, user_id: str, session_id: str
) -> str:
    if not session_store or not session_id:
        return ""
    try:
        pairs = session_store.recent_pairs(user_id, session_id)
    except Exception as exc:
        logger.warning("Session recall failed: {}", exc)
        return ""
    if not pairs:
        lines: List[str] = []
    else:
        lines = []
        for user_msg, assistant_msg in pairs:
            lines.append(f"User: {user_msg}")
            lines.append(f"Assistant: {assistant_msg}")
    try:
        catalog = session_store.format_flight_inventory_for_memory(
            user_id, session_id
        )
        if catalog:
            if lines:
                lines.append("")
            lines.append(catalog)
    except Exception as exc:
        logger.debug("Flight inventory recall failed: {}", exc)
    return "\n".join(lines) if lines else ""


def _mcp_result_to_str(raw: Any) -> str:
    if isinstance(raw, list):
        parts = [
            item.get("text", str(item))
            for item in raw
            if isinstance(item, dict)
        ]
        return "\n".join(parts) if parts else str(raw)
    return str(raw)


def _tool_status(tool_output: str) -> str:
    if not tool_output:
        return "ok"
    try:
        payload = json.loads(tool_output)
        if isinstance(payload, dict) and payload.get("ok") is False:
            return "failed"
    except (json.JSONDecodeError, TypeError):
        if tool_output.lower().startswith("error"):
            return "failed"
    return "ok"


def _parse_inventory(tool_output: str, key: str) -> List[dict]:
    try:
        payload = json.loads(tool_output)
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(payload, dict) or not payload.get("ok"):
        return []
    items = payload.get(key, [])
    if isinstance(items, list) and items:
        return items
    data = payload.get("data")
    if isinstance(data, dict):
        nested = data.get(key, [])
        return nested if isinstance(nested, list) else []
    return []


def _persist_flight_inventory(
    session_store: Any,
    user_id: str,
    session_id: str,
    flights: List[dict],
) -> None:
    if not session_store or not session_id or not flights:
        return
    try:
        session_store.merge_flight_inventory(user_id, session_id, flights)
    except Exception as exc:
        logger.warning("Flight inventory persist failed: {}", exc)


def _prepare_flight_book_params(
    state: AgentState,
    params: dict,
    *,
    session_store: Any,
) -> dict:
    """Map flight numbers / airline labels to Convex ids before MCP book."""
    prepared = dict(params or {})
    token = prepared.get("flight_id")
    if not token or _looks_like_convex_id(str(token)):
        return prepared

    inventory: List[dict] = []
    user_id = state.get("user_id") or ""
    session_id = state.get("session_id") or ""
    if session_store and session_id:
        inventory = session_store.get_flight_inventory(user_id, session_id)

    resolved, _err = resolve_flight_id(
        str(token),
        origin=prepared.get("origin"),
        destination=prepared.get("destination"),
        date=prepared.get("flight_date") or prepared.get("date"),
        candidate_flights=inventory or None,
    )
    if resolved:
        prepared["flight_id"] = resolved
    return prepared


class AgentOrchestrator:
    """Supervisor–worker LangGraph with parallel hotel / flight / general_qa / web_search nodes."""

    def __init__(
        self,
        llm_chat: Any,
        *,
        llm_merge: Optional[Any] = None,
        session_store: Any = None,
        router: Optional[QueryRouter] = None,
        hotel_tool: Optional[Any] = None,
        flight_tool: Optional[Any] = None,
        web_search_tool: Optional[Any] = None,
    ) -> None:
        self.llm_chat = llm_chat
        self.llm_merge = llm_merge or llm_chat
        self.session_store = session_store
        self.router = router or get_query_router()
        self.hotel_tool = hotel_tool
        self.flight_tool = flight_tool
        self.web_search_tool = web_search_tool
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("recall", self.recall_node)
        workflow.add_node("supervisor", self.supervisor_node)
        workflow.add_node("hotel_agent", self.hotel_agent_node)
        workflow.add_node("flight_agent", self.flight_agent_node)
        workflow.add_node("general_qa_agent", self.general_qa_agent_node)
        workflow.add_node("web_search_agent", self.web_search_agent_node)
        workflow.add_node("merge_responses", self.merge_responses_node)
        workflow.add_node("save_memory", self.save_memory_node)

        workflow.add_conditional_edges(
            START,
            self.entry_routing,
            {"end": END, "recall": "recall"},
        )
        workflow.add_edge("recall", "supervisor")
        workflow.add_conditional_edges(
            "supervisor",
            self.supervisor_routing,
            {
                "hotel": "hotel_agent",
                "flight": "flight_agent",
                "general_qa": "general_qa_agent",
                "web_search": "web_search_agent",
            },
        )
        workflow.add_edge("hotel_agent", "merge_responses")
        workflow.add_edge("flight_agent", "merge_responses")
        workflow.add_edge("general_qa_agent", "merge_responses")
        workflow.add_edge("web_search_agent", "merge_responses")
        workflow.add_edge("merge_responses", "save_memory")
        workflow.add_edge("save_memory", END)

        return workflow.compile()

    def entry_routing(self, state: AgentState) -> str:
        if state.get("verdict") == "out_of_scope":
            return "end"
        return "recall"

    @observe(name="node_recall")
    async def recall_node(self, state: AgentState) -> Dict[str, Any]:
        if state.get("memory_context"):
            return {}
        user_id = state.get("user_id") or ""
        session_id = state.get("session_id") or ""
        memory_context = _format_session_memory(
            self.session_store, user_id, session_id
        )
        return {"memory_context": memory_context or "(no prior turns)"}

    @observe(name="node_supervisor")
    async def supervisor_node(self, state: AgentState) -> Dict[str, Any]:
        existing = state.get("route_decisions")
        if existing:
            return {}

        user_message = _last_user_text(state)
        memory_context = state.get("memory_context") or ""
        multi = await self.router.aroute(user_message, memory_context)
        route_decisions = [asdict(d) for d in multi.decisions]
        return {"route_decisions": route_decisions}

    def supervisor_routing(
        self, state: AgentState
    ) -> Union[str, List[str]]:
        decisions = state.get("route_decisions") or []
        if not decisions:
            return "general_qa"

        node_names: List[str] = []
        seen: set[str] = set()
        for d in decisions:
            route = d.get("route", "general_qa")
            node = _ROUTE_TO_NODE.get(route, "general_qa")
            if node not in seen:
                node_names.append(node)
                seen.add(node)

        if len(node_names) == 1:
            return node_names[0]
        return node_names

    def _decision_for_route(
        self, state: AgentState, route: str
    ) -> Dict[str, Any]:
        decisions = state.get("route_decisions") or []
        match = next((d for d in decisions if d.get("route") == route), None)
        if match:
            return match
        if len(decisions) == 1:
            return decisions[0]
        default_action = "search" if route == "web_search" else "general"
        return {"route": route, "action": default_action, "params": {}}

    async def _dispatch_web_search(
        self, action: str, params: dict, *, fallback_query: str = ""
    ) -> str:
        if action == "general" or not action:
            action = "search"
        tool_action = _WEB_SEARCH_ACTION_TO_TOOL.get(action)
        if not tool_action:
            return json.dumps(
                {
                    "ok": False,
                    "error": f"Unknown web_search action: {action}",
                    "code": "UNKNOWN_ACTION",
                }
            )
        if not self.web_search_tool:
            return json.dumps(
                {
                    "ok": False,
                    "error": "Web search tool unavailable.",
                    "code": "UNAVAILABLE",
                }
            )
        clean = {k: v for k, v in (params or {}).items() if v is not None}
        if not clean.get("query"):
            clean["query"] = fallback_query
        if not clean.get("query"):
            return json.dumps(
                {"ok": False, "error": "Missing search query.", "code": "VALIDATION"}
            )
        try:
            if hasattr(self.web_search_tool, "adispatch"):
                return await self.web_search_tool.adispatch(action, clean)
            return self.web_search_tool.dispatch(tool_action, clean)
        except Exception as exc:
            logger.error("Web search tool dispatch failed: {}", exc)
            return json.dumps(
                {"ok": False, "error": str(exc), "code": "INTERNAL"}
            )

    async def _dispatch_hotel(self, action: str, params: dict) -> str:
        if action == "general" or not action:
            return ""
        tool_action = _HOTEL_ACTION_TO_TOOL.get(action)
        if not tool_action:
            return json.dumps(
                {
                    "ok": False,
                    "error": f"Unknown hotel action: {action}",
                    "code": "UNKNOWN_ACTION",
                }
            )
        if not self.hotel_tool:
            return json.dumps(
                {"ok": False, "error": "Hotel tool unavailable.", "code": "UNAVAILABLE"}
            )
        clean = {k: v for k, v in (params or {}).items() if v is not None}
        try:
            if hasattr(self.hotel_tool, "adispatch"):
                return await self.hotel_tool.adispatch(action, clean)
            return self.hotel_tool.dispatch(tool_action, clean)
        except Exception as exc:
            logger.error("Hotel tool dispatch failed: {}", exc)
            return json.dumps(
                {"ok": False, "error": str(exc), "code": "INTERNAL"}
            )

    async def _dispatch_flight(self, action: str, params: dict) -> str:
        if action == "general" or not action:
            return ""
        tool_action = _FLIGHT_ACTION_TO_TOOL.get(action)
        if not tool_action:
            return json.dumps(
                {
                    "ok": False,
                    "error": f"Unknown flight action: {action}",
                    "code": "UNKNOWN_ACTION",
                }
            )
        if not self.flight_tool:
            return json.dumps(
                {"ok": False, "error": "Flight tool unavailable.", "code": "UNAVAILABLE"}
            )
        clean = {k: v for k, v in (params or {}).items() if v is not None}
        try:
            if hasattr(self.flight_tool, "adispatch"):
                return await self.flight_tool.adispatch(action, clean)
            return self.flight_tool.dispatch(tool_action, clean)
        except Exception as exc:
            logger.error("Flight tool dispatch failed: {}", exc)
            return json.dumps(
                {"ok": False, "error": str(exc), "code": "INTERNAL"}
            )

    async def _generate_agent_response(
        self,
        state: AgentState,
        system_prompt: str,
        tool_output: str,
        config: Optional[RunnableConfig] = None,
    ) -> str:
        user_message = _last_user_text(state)
        memory_context = state.get("memory_context") or ""
        system_content = (
            f"{system_prompt}\n\n"
            f"=== MEMORY CONTEXT ===\n{memory_context}\n\n"
            f"=== TOOL OUTPUT ===\n{tool_output or '(no tool output)'}"
        )
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=user_message),
        ]
        emit = _emit_from_config(config)
        stream = _route_decision_count(state) <= 1
        return await _synthesize_llm_text(
            self.llm_chat,
            messages,
            emit=emit,
            stream=stream,
        )

    @observe(name="node_hotel_agent")
    async def hotel_agent_node(
        self,
        state: AgentState,
        config: Optional[RunnableConfig] = None,
    ) -> Dict[str, Any]:
        decision = self._decision_for_route(state, "hotel")
        action = decision.get("action") or "search"
        params = decision.get("params") or {}
        memory_context = state.get("memory_context") or ""

        tool_output = await self._dispatch_hotel(action, params)
        system_prompt = build_hotel_agent_system_prompt(memory_context=memory_context)
        answer = await self._generate_agent_response(
            state, system_prompt, tool_output, config
        )
        status = _tool_status(tool_output)

        patch: Dict[str, Any] = {
            "messages": [AIMessage(content=answer)],
            "agent_outputs": [
                {
                    "route": "hotel",
                    "tool_output": tool_output,
                    "answer": answer,
                    "status": status,
                }
            ],
        }
        hotels = _parse_inventory(tool_output, "hotels")
        if hotels:
            patch["hotel_results"] = hotels
        return patch

    @observe(name="node_flight_agent")
    async def flight_agent_node(
        self,
        state: AgentState,
        config: Optional[RunnableConfig] = None,
    ) -> Dict[str, Any]:
        decision = self._decision_for_route(state, "flight")
        action = decision.get("action") or "search"
        params = decision.get("params") or {}
        if action == "book":
            params = _prepare_flight_book_params(
                state, params, session_store=self.session_store
            )
        memory_context = state.get("memory_context") or ""

        tool_output = await self._dispatch_flight(action, params)
        system_prompt = build_flight_agent_system_prompt(memory_context=memory_context)
        answer = await self._generate_agent_response(
            state, system_prompt, tool_output, config
        )
        status = _tool_status(tool_output)

        patch: Dict[str, Any] = {
            "messages": [AIMessage(content=answer)],
            "agent_outputs": [
                {
                    "route": "flight",
                    "tool_output": tool_output,
                    "answer": answer,
                    "status": status,
                }
            ],
        }
        flights = _parse_inventory(tool_output, "flights")
        if flights:
            patch["flight_results"] = flights
            _persist_flight_inventory(
                self.session_store,
                state.get("user_id") or "",
                state.get("session_id") or "",
                flights,
            )
        return patch

    @observe(name="node_general_qa_agent")
    async def general_qa_agent_node(
        self,
        state: AgentState,
        config: Optional[RunnableConfig] = None,
    ) -> Dict[str, Any]:
        memory_context = state.get("memory_context") or ""
        system_prompt = build_general_qa_system_prompt(memory_context=memory_context)
        answer = await self._generate_agent_response(
            state, system_prompt, "", config
        )
        return {
            "messages": [AIMessage(content=answer)],
            "agent_outputs": [
                {
                    "route": "general_qa",
                    "tool_output": "",
                    "answer": answer,
                    "status": "ok",
                }
            ],
        }

    @observe(name="node_web_search_agent")
    async def web_search_agent_node(
        self,
        state: AgentState,
        config: Optional[RunnableConfig] = None,
    ) -> Dict[str, Any]:
        decision = self._decision_for_route(state, "web_search")
        action = decision.get("action") or "search"
        params = decision.get("params") or {}
        memory_context = state.get("memory_context") or ""
        user_message = _last_user_text(state)

        tool_output = await self._dispatch_web_search(
            action, params, fallback_query=user_message
        )
        system_prompt = build_web_search_agent_system_prompt(
            memory_context=memory_context
        )
        answer = await self._generate_agent_response(
            state, system_prompt, tool_output, config
        )
        status = _tool_status(tool_output)

        return {
            "messages": [AIMessage(content=answer)],
            "agent_outputs": [
                {
                    "route": "web_search",
                    "tool_output": tool_output,
                    "answer": answer,
                    "status": status,
                }
            ],
        }

    @observe(name="node_merge_responses")
    async def merge_responses_node(
        self,
        state: AgentState,
        config: Optional[RunnableConfig] = None,
    ) -> Dict[str, Any]:
        agent_outputs = state.get("agent_outputs") or []
        if len(agent_outputs) <= 1:
            if agent_outputs:
                out = agent_outputs[0]
                return {
                    "final_answer": out.get("answer", ""),
                    "tool_output": out.get("tool_output", ""),
                }
            return {}

        logger.info("Merging {} agent outputs", len(agent_outputs))
        user_message = _last_user_text(state)
        memory_context = state.get("memory_context") or ""

        combined = ""
        for out in agent_outputs:
            route = out.get("route", "unknown").upper()
            combined += f"=== {route} AGENT RESULT ===\n{out.get('answer', '')}\n\n"

        system_prompt = build_merge_system_prompt(memory_context=memory_context)
        system_content = (
            f"{system_prompt}\n\n"
            f"=== AGENT RESULTS TO MERGE ===\n{combined}"
        )
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=user_message),
        ]
        emit = _emit_from_config(config)
        try:
            merged = await _synthesize_llm_text(
                self.llm_merge,
                messages,
                emit=emit,
                stream=True,
            )
        except Exception as exc:
            if self.llm_merge is self.llm_chat:
                raise
            logger.warning(
                "Merge LLM failed ({}); falling back to chat LLM.", exc
            )
            merged = await _synthesize_llm_text(
                self.llm_chat,
                messages,
                emit=emit,
                stream=True,
            )
        all_tool = "\n---\n".join(
            o.get("tool_output", "")
            for o in agent_outputs
            if o.get("tool_output")
        )
        return {
            "final_answer": merged,
            "messages": [AIMessage(content=merged)],
            "tool_output": all_tool,
        }

    @observe(name="node_save_memory")
    async def save_memory_node(self, state: AgentState) -> Dict[str, Any]:
        user_id = state.get("user_id") or ""
        session_id = state.get("session_id") or ""
        answer = state.get("final_answer")
        if not self.session_store or not session_id or not answer:
            return {}
        user_message = _last_user_text(state)
        if not user_message:
            return {}
        try:
            self.session_store.add_exchange(
                user_id, session_id, user_message, answer
            )
        except Exception as exc:
            logger.warning("save_memory failed: {}", exc)
        return {}

    @observe(name="agent_chat")
    async def achat(
        self,
        user_message: str,
        *,
        user_id: str = "",
        session_id: str = "",
    ) -> AgentResponse:
        """Standalone turn: no decision graph (supervisor runs router)."""
        t0 = time.perf_counter()
        final_state = await self.graph.ainvoke(
            {
                "messages": [HumanMessage(content=user_message)],
                "user_id": user_id,
                "session_id": session_id,
                "verdict": "proceed",
                "agent_outputs": [],
            }
        )
        latency = int((time.perf_counter() - t0) * 1000)
        return self._to_agent_response(final_state, latency)

    async def arun_state(
        self,
        state: AgentState,
        *,
        config: Optional[RunnableConfig] = None,
    ) -> AgentState:
        """Invoke with a bridged ``AgentState`` patch (Phase 6 path)."""
        merged = dict(state)
        merged["agent_outputs"] = []
        return await self.graph.ainvoke(merged, config=config or {})  # type: ignore[return-value]

    def _to_agent_response(self, final_state: dict, latency_ms: int) -> AgentResponse:
        route_decisions = final_state.get("route_decisions") or []
        all_routes = [d.get("route", "general_qa") for d in route_decisions]
        primary = route_decisions[0] if route_decisions else {"route": "general_qa"}
        if not all_routes and final_state.get("verdict") == "out_of_scope":
            all_routes = ["out_of_scope"]
        return AgentResponse(
            answer=final_state.get("final_answer") or "",
            route=primary.get("route", "general_qa"),
            routes=all_routes,
            action=primary.get("action"),
            tool_output=final_state.get("tool_output", ""),
            memory_context=final_state.get("memory_context", ""),
            latency_ms=latency_ms,
        )


# ── MCP tool adapters ───────────────────────────────────────────────────────


class _MCPHotelToolAdapter:
    """MCP hotel tools → ``dispatch(action, params)`` (sync or async)."""

    _ACTION_TO_TOOL = _HOTEL_ACTION_TO_TOOL

    def __init__(self, tools_by_name: dict):
        self._tools = tools_by_name

    def dispatch(self, action: str, params: dict) -> str:
        return _sync_mcp_dispatch(self._tools, self._ACTION_TO_TOOL, action, params)

    async def adispatch(self, action: str, params: dict) -> str:
        return await _async_mcp_dispatch(self._tools, self._ACTION_TO_TOOL, action, params)


class _MCPFlightToolAdapter:
    """MCP flight tools → ``dispatch(action, params)`` (sync or async)."""

    _ACTION_TO_TOOL = _FLIGHT_ACTION_TO_TOOL

    def __init__(self, tools_by_name: dict):
        self._tools = tools_by_name

    def dispatch(self, action: str, params: dict) -> str:
        return _sync_mcp_dispatch(self._tools, self._ACTION_TO_TOOL, action, params)

    async def adispatch(self, action: str, params: dict) -> str:
        return await _async_mcp_dispatch(self._tools, self._ACTION_TO_TOOL, action, params)


class _MCPWebSearchToolAdapter:
    """MCP ``search_web`` → ``adispatch(action, params)`` with ``query``."""

    _ACTION_TO_TOOL = _WEB_SEARCH_ACTION_TO_TOOL

    def __init__(self, tools_by_name: dict):
        self._tools = tools_by_name

    def dispatch(self, action: str, params: dict) -> str:
        return _sync_mcp_dispatch(
            self._tools, self._ACTION_TO_TOOL, action, params
        )

    async def adispatch(self, action: str, params: dict) -> str:
        return await _async_mcp_dispatch(
            self._tools, self._ACTION_TO_TOOL, action, params
        )


class _DirectWebSearchToolAdapter:
    """In-process ``WebSearchTool`` for ``build_orchestrator`` debug path."""

    def __init__(self, tool: Any) -> None:
        self._tool = tool

    async def adispatch(self, action: str, params: dict) -> str:
        _ = action
        query = (params or {}).get("query") or ""
        return await self._tool.asearch(query)


async def _async_mcp_dispatch(
    tools_by_name: dict,
    action_map: dict,
    action: str,
    params: dict,
) -> str:
    tool_name = action_map.get(action) or action
    tool = tools_by_name.get(tool_name)
    if tool is None:
        return json.dumps(
            {
                "ok": False,
                "error": f"MCP tool not available: {tool_name}",
                "code": "UNAVAILABLE",
            }
        )
    clean = {k: v for k, v in (params or {}).items() if v is not None}
    try:
        raw = await tool.ainvoke(clean)
        return _mcp_result_to_str(raw)
    except Exception as exc:
        logger.error("MCP tool '{}' failed: {}", tool_name, exc)
        return json.dumps({"ok": False, "error": str(exc), "code": "INTERNAL"})


def _sync_mcp_dispatch(
    tools_by_name: dict,
    action_map: dict,
    action: str,
    params: dict,
) -> str:
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(
            _async_mcp_dispatch(tools_by_name, action_map, action, params)
        )
    return loop.run_until_complete(
        _async_mcp_dispatch(tools_by_name, action_map, action, params)
    )


# ── Factories ───────────────────────────────────────────────────────────────


def build_orchestrator(
    *,
    session_store: Any = None,
    use_direct_tools: bool = True,
) -> AgentOrchestrator:
    """In-process ``HotelTool`` / ``FlightTool`` (debug without MCP subprocesses)."""
    from infrastructure.llm import get_chat_llm, get_merge_llm

    hotel_tool = None
    flight_tool = None
    web_search_tool = None
    if use_direct_tools:
        try:
            from agents.tools import FlightTool, HotelTool, WebSearchTool

            hotel_tool = HotelTool()
            flight_tool = FlightTool()
            web_search_tool = _DirectWebSearchToolAdapter(WebSearchTool())
            logger.info(
                "Orchestrator using direct HotelTool / FlightTool / WebSearchTool"
            )
        except Exception as exc:
            logger.warning("Direct travel tools unavailable: {}", exc)

    if session_store is None:
        from infrastructure.session_store import SessionStore

        session_store = SessionStore()

    return AgentOrchestrator(
        get_chat_llm(temperature=0),
        llm_merge=get_merge_llm(temperature=0),
        session_store=session_store,
        hotel_tool=hotel_tool,
        flight_tool=flight_tool,
        web_search_tool=web_search_tool,
    )


async def build_agent_mcp(
    *,
    session_store: Any = None,
) -> AgentOrchestrator:
    """Assessment path — agents call Convex only through MCP stdio servers."""
    from langchain_mcp_adapters.client import MultiServerMCPClient

    from infrastructure.llm import get_chat_llm, get_merge_llm
    from mcp_servers.mcp_config import build_mcp_server_config

    if session_store is None:
        from infrastructure.session_store import SessionStore

        session_store = SessionStore()

    llm_chat = get_chat_llm(temperature=0)
    llm_merge = get_merge_llm(temperature=0)
    server_config = build_mcp_server_config()
    logger.info("Connecting to MCP servers: {}", list(server_config.keys()))
    mcp_client = MultiServerMCPClient(server_config)
    all_tools = await mcp_client.get_tools()
    tools_by_name = {t.name: t for t in all_tools}
    logger.info("Loaded {} MCP tools: {}", len(all_tools), list(tools_by_name.keys()))

    orchestrator = AgentOrchestrator(
        llm_chat,
        llm_merge=llm_merge,
        session_store=session_store,
        hotel_tool=_MCPHotelToolAdapter(tools_by_name),
        flight_tool=_MCPFlightToolAdapter(tools_by_name),
        web_search_tool=_MCPWebSearchToolAdapter(tools_by_name),
    )
    orchestrator.mcp_client = mcp_client
    orchestrator.mcp_tools = tools_by_name
    return orchestrator
