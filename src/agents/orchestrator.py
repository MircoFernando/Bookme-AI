"""
BookMe AI orchestrator — LangGraph fan-out after the decision subgraph.

Phase 6 chat runs ``decision_graph`` → ``decision_bridge`` → this graph.
``route_decisions`` are usually pre-filled by the bridge; the supervisor
re-routes only when the graph is invoked standalone (CLI / tests).

Topology::

    START → (out_of_scope? END)
         → recall → supervisor → [hotel_agent | flight_agent | general_qa_agent]
                                              ↘ merge_responses → save_memory → END

Tools reach Convex only via MCP adapters in ``build_agent_mcp()`` (assessment E1).
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Union

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agents.prompts import (
    build_flight_agent_system_prompt,
    build_general_qa_system_prompt,
    build_hotel_agent_system_prompt,
    build_merge_system_prompt,
)
from agents.router import QueryRouter, get_query_router
from agents.state import AgentState
from infrastructure.observability import observe


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

_ROUTE_TO_NODE = {
    "hotel": "hotel",
    "flight": "flight",
    "general_qa": "general_qa",
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


def _llm_content_to_str(content: Any) -> str:
    """Normalize OpenAI/Gemini message content to plain text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text")
                if text:
                    parts.append(str(text))
                elif block.get("type") == "text" and "content" in block:
                    parts.append(str(block["content"]))
            else:
                text = getattr(block, "text", None)
                if text:
                    parts.append(str(text))
        return "\n".join(parts) if parts else str(content)
    return str(content)


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
        return ""
    lines: List[str] = []
    for user_msg, assistant_msg in pairs:
        lines.append(f"User: {user_msg}")
        lines.append(f"Assistant: {assistant_msg}")
    return "\n".join(lines)


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
    data = payload.get("data")
    if isinstance(data, dict):
        items = data.get(key, [])
        return items if isinstance(items, list) else []
    return []


class AgentOrchestrator:
    """Supervisor–worker LangGraph with parallel hotel / flight / general_qa nodes."""

    def __init__(
        self,
        llm_chat: Any,
        *,
        llm_merge: Optional[Any] = None,
        session_store: Any = None,
        router: Optional[QueryRouter] = None,
        hotel_tool: Optional[Any] = None,
        flight_tool: Optional[Any] = None,
    ) -> None:
        self.llm_chat = llm_chat
        self.llm_merge = llm_merge or llm_chat
        self.session_store = session_store
        self.router = router or get_query_router()
        self.hotel_tool = hotel_tool
        self.flight_tool = flight_tool
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("recall", self.recall_node)
        workflow.add_node("supervisor", self.supervisor_node)
        workflow.add_node("hotel_agent", self.hotel_agent_node)
        workflow.add_node("flight_agent", self.flight_agent_node)
        workflow.add_node("general_qa_agent", self.general_qa_agent_node)
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
            },
        )
        workflow.add_edge("hotel_agent", "merge_responses")
        workflow.add_edge("flight_agent", "merge_responses")
        workflow.add_edge("general_qa_agent", "merge_responses")
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
        return {"route": route, "action": "general", "params": {}}

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
    ) -> str:
        user_message = _last_user_text(state)
        memory_context = state.get("memory_context") or ""
        system_content = (
            f"{system_prompt}\n\n"
            f"=== MEMORY CONTEXT ===\n{memory_context}\n\n"
            f"=== TOOL OUTPUT ===\n{tool_output or '(no tool output)'}"
        )
        response = await self.llm_chat.ainvoke(
            [
                SystemMessage(content=system_content),
                HumanMessage(content=user_message),
            ]
        )
        return _llm_content_to_str(
            response.content if hasattr(response, "content") else response
        )

    @observe(name="node_hotel_agent")
    async def hotel_agent_node(self, state: AgentState) -> Dict[str, Any]:
        decision = self._decision_for_route(state, "hotel")
        action = decision.get("action") or "search"
        params = decision.get("params") or {}
        memory_context = state.get("memory_context") or ""

        tool_output = await self._dispatch_hotel(action, params)
        system_prompt = build_hotel_agent_system_prompt(memory_context=memory_context)
        answer = await self._generate_agent_response(state, system_prompt, tool_output)
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
    async def flight_agent_node(self, state: AgentState) -> Dict[str, Any]:
        decision = self._decision_for_route(state, "flight")
        action = decision.get("action") or "search"
        params = decision.get("params") or {}
        memory_context = state.get("memory_context") or ""

        tool_output = await self._dispatch_flight(action, params)
        system_prompt = build_flight_agent_system_prompt(memory_context=memory_context)
        answer = await self._generate_agent_response(state, system_prompt, tool_output)
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
        return patch

    @observe(name="node_general_qa_agent")
    async def general_qa_agent_node(self, state: AgentState) -> Dict[str, Any]:
        memory_context = state.get("memory_context") or ""
        system_prompt = build_general_qa_system_prompt(memory_context=memory_context)
        answer = await self._generate_agent_response(state, system_prompt, "")
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

    @observe(name="node_merge_responses")
    async def merge_responses_node(self, state: AgentState) -> Dict[str, Any]:
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
        try:
            response = await self.llm_merge.ainvoke(messages)
        except Exception as exc:
            if self.llm_merge is self.llm_chat:
                raise
            logger.warning(
                "Merge LLM failed ({}); falling back to chat LLM.", exc
            )
            response = await self.llm_chat.ainvoke(messages)
        merged = _llm_content_to_str(
            response.content if hasattr(response, "content") else response
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

    async def arun_state(self, state: AgentState) -> AgentState:
        """Invoke with a bridged ``AgentState`` patch (Phase 6 path)."""
        merged = dict(state)
        merged["agent_outputs"] = []
        return await self.graph.ainvoke(merged)  # type: ignore[return-value]

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
    if use_direct_tools:
        try:
            from agents.tools import FlightTool, HotelTool

            hotel_tool = HotelTool()
            flight_tool = FlightTool()
            logger.info("Orchestrator using direct HotelTool / FlightTool")
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
    )
    orchestrator.mcp_client = mcp_client
    orchestrator.mcp_tools = tools_by_name
    return orchestrator
