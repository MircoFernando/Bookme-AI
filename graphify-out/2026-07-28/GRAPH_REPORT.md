# Graph Report - Bookme AI  (2026-07-27)

## Corpus Check
- 58 files · ~24,164 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 578 nodes · 1083 edges · 24 communities (19 shown, 5 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 126 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d46920ce`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- decision_graph.py
- router.py
- nodes.py
- observability.py
- http_client.py
- SessionStore
- Decision graph & routing — architecture notes
- BookMe AI — Development Roadmap & Phase Log
- config.py
- infrastructure/llm.py
- llm/__init__.py
- Setup
- main.py
- flight_server.py
- hotel_server.py
- mcp_config.py
- frontend.py
- prompts/__init__.py
- tools/__init__.py
- src/__init__.py
- infrastructure/__init__.py
- decision_graph.py
- flight_server.py

## God Nodes (most connected - your core abstractions)
1. `AgentOrchestrator` - 33 edges
2. `AgentState` - 30 edges
3. `QueryRouter` - 23 edges
4. `SessionStore` - 21 edges
5. `BookMe AI — Development Roadmap & Phase Log` - 20 edges
6. `observe()` - 19 edges
7. `fetch_prompt()` - 16 edges
8. `build_decision_graph()` - 14 edges
9. `build_agent_mcp()` - 14 edges
10. `Decision graph & routing — architecture notes` - 13 edges

## Surprising Connections (you probably didn't know these)
- `_RecordingOrchestrator` --uses--> `SessionStore`  [INFERRED]
  scripts/test_chat_pipeline.py → src/infrastructure/session_store.py
- `main()` --calls--> `run_chat_turn()`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/chat_pipeline.py
- `main()` --calls--> `build_decision_graph()`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/decision_graph.py
- `main()` --calls--> `SessionStore`  [INFERRED]
  scripts/test_chat_pipeline.py → src/infrastructure/session_store.py
- `_router_primary_route()` --calls--> `get_query_router()`  [INFERRED]
  scripts/test_decision_graph.py → src/agents/router.py

## Import Cycles
- None detected.

## Communities (24 total, 5 thin omitted)

### Community 0 - "decision_graph.py"
Cohesion: 0.07
Nodes (35): AnyMessage, RunnableConfig, main(), _router_primary_route(), _run(), main(), map_decision_to_agent_state(), Bridge decision subgraph output → orchestrator ``AgentState`` (Week 13).  The ch (+27 more)

### Community 1 - "router.py"
Cohesion: 0.12
Nodes (19): _fallback_multi(), get_query_router(), _last_user_text(), MultiRouteDecision, _normalize_action(), _normalize_params(), Any, QueryRouter (+11 more)

### Community 2 - "nodes.py"
Cohesion: 0.09
Nodes (40): GraphState, TypedDict, build_graph(), flight_node(), _format_flight(), _format_hotel(), generate_response(), hotel_node() (+32 more)

### Community 3 - "observability.py"
Cohesion: 0.08
Nodes (37): GuardrailVerdict, _build_user_prompt(), Classify *message* as ``in_scope`` or ``out_of_scope``.          *memory_context, build_extractor_system_prompt(), build_flight_agent_system_prompt(), build_general_qa_system_prompt(), build_guardrail_system_prompt(), build_hotel_agent_system_prompt() (+29 more)

### Community 4 - "http_client.py"
Cohesion: 0.14
Nodes (16): _dumps(), _extract_hotels(), HotelTool, Any, Hotel tool — Convex hotel API (list / search / book).  Week 13 pattern: business, Hotel service actions routed by ``dispatch``., Map router aliases and drop Nones., book_hotel() (+8 more)

### Community 5 - "SessionStore"
Cohesion: 0.08
Nodes (43): _clerk_user_id(), get_decision_graph(), get_orchestrator(), get_session_store(), is_auth_disabled(), Any, Request, Dependency injection — objects built in ``api.main`` lifespan live on ``app.stat (+35 more)

### Community 6 - "Decision graph & routing — architecture notes"
Cohesion: 0.08
Nodes (24): 10. Phase 4–6 status & acceptance, 11. Repository map (agents + API), 12. Questions for Week 13 / instructor (optional prompt), 1. Two-stage pipeline (mental model), 2. Week 13 architecture choice (two state types), 3. Decision graph topology (BookMe AI), 4.1 Both branches always start, 4.2 Fan-in before `decide` (+16 more)

### Community 7 - "BookMe AI — Development Roadmap & Phase Log"
Cohesion: 0.06
Nodes (34): main(), Minimal stand-in — records whether MCP path would run., _RecordingOrchestrator, Agent layer — LangGraph orchestration, routing, guardrail, and agent nodes.  Wee, AgentOrchestrator, AgentResponse, _async_mcp_dispatch(), _DirectWebSearchToolAdapter (+26 more)

### Community 8 - "config.py"
Cohesion: 0.08
Nodes (34): main(), _text(), dump(), get_api_key(), get_models(), _get_nested(), get_params(), get_tavily_api_key() (+26 more)

### Community 9 - "infrastructure/llm.py"
Cohesion: 0.07
Nodes (25): BaseHTTPMiddleware, main(), lifespan(), FastAPI, get, FastAPI application — BookMe AI travel assistant (Phase 6).  Start::      make r, root(), install_middleware() (+17 more)

### Community 11 - "Setup"
Cohesion: 0.06
Nodes (31): Assessment mapping (SRS), BookMe AI — Development Roadmap & Phase Log, Commands cheat sheet, Decision log (consolidated), High-level phase map, How to read this document, Next recommended step, Phase 0 — Baseline starter ✅ (+23 more)

### Community 12 - "main.py"
Cohesion: 0.17
Nodes (12): _compact_results(), _dumps(), Any, Web search tool — Tavily Search API (travel / tourism Q&A).  Business logic live, Sync entry for scripts/tests., Tavily-backed web search for destination and tourism questions., WebSearchTool, _get_web_search() (+4 more)

### Community 13 - "flight_server.py"
Cohesion: 0.12
Nodes (21): Exception, retry, _dumps(), _extract_flights(), FlightTool, _normalize_airport(), Any, Flight tool — Convex flight API (list / search / book).  Same contract as ``Hote (+13 more)

### Community 15 - "mcp_config.py"
Cohesion: 0.13
Nodes (26): ChatOpenAI, main(), build_agent_mcp(), build_orchestrator(), In-process ``HotelTool`` / ``FlightTool`` (debug without MCP subprocesses)., Assessment path — agents call Convex only through MCP stdio servers., _build_google_llm(), _build_llm() (+18 more)

### Community 16 - "frontend.py"
Cohesion: 0.60
Nodes (5): call_chat_api(), format_flights(), format_hotels(), main(), respond()

### Community 20 - "infrastructure/__init__.py"
Cohesion: 0.13
Nodes (22): RouteLiteral, ChatResult, _noop_emit(), Any, EmitFn, Single async entry for one chat turn: decision graph → orchestrator (or OOS shor, One user turn — maps cleanly to ``api.schemas.ChatResponse``., Run decision graph, then orchestrator unless ``verdict == out_of_scope``.      L (+14 more)

### Community 21 - "decision_graph.py"
Cohesion: 0.18
Nodes (8): LogRecord, Infrastructure layer — pure plumbing (config, logging, LLM clients, observabilit, Backward-compatible re-export — prefer ``from infrastructure.llm import ...``., _InterceptHandler, Centralised logging — powered by **loguru**.  Usage (any module)::      from log, Route stdlib ``logging`` records into loguru so third-party libs     (uvicorn, h, Configure loguru for the current process. Call once at each entry-point.      Ar, setup_logging()

### Community 23 - "flight_server.py"
Cohesion: 0.31
Nodes (9): book_flight(), _get_flight(), list_flights(), tool, Flight MCP server — exposes FlightTool over the Model Context Protocol.  Run sta, List all available flights from the travel service., Search flights by origin, destination, and optional date (YYYY-MM-DD).      Args, Book a flight.      Args:         flight_id: Flight identifier from search/list (+1 more)

## Knowledge Gaps
- **48 isolated node(s):** `Requirements`, `Setup`, `Chat (non-streaming)`, `Chat (SSE chain-of-thought)`, `Other API routes` (+43 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_orchestrator()` connect `mcp_config.py` to `http_client.py`, `BookMe AI — Development Roadmap & Phase Log`, `infrastructure/llm.py`, `main.py`, `flight_server.py`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `AgentOrchestrator` connect `BookMe AI — Development Roadmap & Phase Log` to `router.py`, `infrastructure/__init__.py`, `infrastructure/llm.py`, `mcp_config.py`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `SessionStore` connect `infrastructure/llm.py` to `mcp_config.py`, `BookMe AI — Development Roadmap & Phase Log`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `AgentOrchestrator` (e.g. with `_RecordingOrchestrator` and `.__init__()`) actually correct?**
  _`AgentOrchestrator` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `AgentState` (e.g. with `_RecordingOrchestrator` and `AgentOrchestrator`) actually correct?**
  _`AgentState` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `QueryRouter` (e.g. with `AgentOrchestrator` and `AgentResponse`) actually correct?**
  _`QueryRouter` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `SessionStore` (e.g. with `main()` and `_RecordingOrchestrator`) actually correct?**
  _`SessionStore` has 12 INFERRED edges - model-reasoned connections that need verification._