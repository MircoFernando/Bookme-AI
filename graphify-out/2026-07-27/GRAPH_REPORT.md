# Graph Report - Bookme AI  (2026-07-27)

## Corpus Check
- 48 files · ~21,899 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 493 nodes · 925 edges · 23 communities (19 shown, 4 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 107 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ff6de2cd`
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
- build_mcp_server_config

## God Nodes (most connected - your core abstractions)
1. `AgentOrchestrator` - 32 edges
2. `AgentState` - 30 edges
3. `QueryRouter` - 23 edges
4. `SessionStore` - 20 edges
5. `observe()` - 19 edges
6. `BookMe AI — Development Roadmap & Phase Log` - 19 edges
7. `fetch_prompt()` - 16 edges
8. `run_chat_turn()` - 14 edges
9. `build_decision_graph()` - 13 edges
10. `build_agent_mcp()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `_RecordingOrchestrator` --uses--> `AgentOrchestrator`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/orchestrator.py
- `_RecordingOrchestrator` --uses--> `AgentState`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/state.py
- `main()` --calls--> `run_chat_turn()`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/chat_pipeline.py
- `main()` --calls--> `build_decision_graph()`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/decision_graph.py
- `_router_primary_route()` --calls--> `get_query_router()`  [INFERRED]
  scripts/test_decision_graph.py → src/agents/router.py

## Import Cycles
- None detected.

## Communities (23 total, 4 thin omitted)

### Community 0 - "decision_graph.py"
Cohesion: 0.07
Nodes (34): AnyMessage, GuardrailVerdict, RunnableConfig, main(), _router_primary_route(), _run(), main(), map_decision_to_agent_state() (+26 more)

### Community 1 - "router.py"
Cohesion: 0.12
Nodes (19): _fallback_multi(), get_query_router(), _last_user_text(), MultiRouteDecision, _normalize_action(), _normalize_params(), Any, QueryRouter (+11 more)

### Community 2 - "nodes.py"
Cohesion: 0.09
Nodes (39): GraphState, TypedDict, build_graph(), flight_node(), _format_flight(), _format_hotel(), generate_response(), hotel_node() (+31 more)

### Community 3 - "observability.py"
Cohesion: 0.10
Nodes (33): build_extractor_system_prompt(), build_flight_agent_system_prompt(), build_general_qa_system_prompt(), build_guardrail_system_prompt(), build_hotel_agent_system_prompt(), build_merge_system_prompt(), build_router_hard_rules_prompt(), build_router_prompt() (+25 more)

### Community 4 - "http_client.py"
Cohesion: 0.12
Nodes (21): Exception, retry, _dumps(), _extract_hotels(), HotelTool, Any, Hotel tool — Convex hotel API (list / search / book).  Week 13 pattern: business, Hotel service actions routed by ``dispatch``. (+13 more)

### Community 5 - "SessionStore"
Cohesion: 0.10
Nodes (19): Assessment mapping (SRS), BookMe AI — Development Roadmap & Phase Log, Commands cheat sheet, Decision log (consolidated), High-level phase map, How to read this document, Next recommended step, Phase 0 — Baseline starter ✅ (+11 more)

### Community 6 - "Decision graph & routing — architecture notes"
Cohesion: 0.08
Nodes (24): 10. Phase 4 status & acceptance, 11. Repository map (Phase 4 agents), 12. Questions for Week 13 / instructor (optional prompt), 1. Two-stage pipeline (mental model), 2. Week 13 architecture choice (two state types), 3. Decision graph topology (BookMe AI), 4.1 Both branches always start, 4.2 Fan-in before `decide` (+16 more)

### Community 7 - "BookMe AI — Development Roadmap & Phase Log"
Cohesion: 0.07
Nodes (31): Agent layer — LangGraph orchestration, routing, guardrail, and agent nodes.  Wee, AgentOrchestrator, AgentResponse, _async_mcp_dispatch(), _DirectWebSearchToolAdapter, _format_session_memory(), _last_user_text(), _llm_content_to_str() (+23 more)

### Community 8 - "config.py"
Cohesion: 0.11
Nodes (28): dump(), get_api_key(), get_models(), _get_nested(), get_params(), get_tavily_api_key(), _load_yaml(), _model_for() (+20 more)

### Community 9 - "infrastructure/llm.py"
Cohesion: 0.09
Nodes (17): main(), Minimal stand-in — records whether MCP path would run., _RecordingOrchestrator, main(), Per-session conversation memory — kills the global-history bug.  The baseline ke, Clear a single thread's history., Number of active threads (debug/health)., A single conversation turn. (+9 more)

### Community 11 - "Setup"
Cohesion: 0.17
Nodes (11): 1. Create Virtual Environment, 2. Install Dependencies, 3. Configure API Key, 4. Run the Backend, 5. Run the Frontend, API Endpoints, BookMe AI, Chat Example (+3 more)

### Community 12 - "main.py"
Cohesion: 0.17
Nodes (12): _compact_results(), _dumps(), Any, Web search tool — Tavily Search API (travel / tourism Q&A).  Business logic live, Sync entry for scripts/tests., Tavily-backed web search for destination and tourism questions., WebSearchTool, _get_web_search() (+4 more)

### Community 13 - "flight_server.py"
Cohesion: 0.14
Nodes (16): _dumps(), _extract_flights(), FlightTool, _normalize_airport(), Any, Flight tool — Convex flight API (list / search / book).  Same contract as ``Hote, Flight service actions routed by ``dispatch``., book_flight() (+8 more)

### Community 14 - "hotel_server.py"
Cohesion: 0.31
Nodes (9): book_hotel(), _get_hotel(), list_hotels(), tool, Hotel MCP server — exposes HotelTool over the Model Context Protocol.  Thin tran, List all available hotels from the travel service., Search hotels by city and optional check-in/check-out dates (YYYY-MM-DD).      A, Book a hotel room.      Args:         hotel_id: Hotel identifier from search/lis (+1 more)

### Community 15 - "mcp_config.py"
Cohesion: 0.13
Nodes (26): ChatOpenAI, main(), build_agent_mcp(), build_orchestrator(), In-process ``HotelTool`` / ``FlightTool`` (debug without MCP subprocesses)., Assessment path — agents call Convex only through MCP stdio servers., _build_google_llm(), _build_llm() (+18 more)

### Community 16 - "frontend.py"
Cohesion: 0.60
Nodes (5): call_chat_api(), format_flights(), format_hotels(), main(), respond()

### Community 20 - "infrastructure/__init__.py"
Cohesion: 0.26
Nodes (11): ChatResult, _noop_emit(), Any, EmitFn, Single async entry for one chat turn: decision graph → orchestrator (or OOS shor, One user turn — maps cleanly to ``api.schemas.ChatResponse``., Run decision graph, then orchestrator unless ``verdict == out_of_scope``.      L, _result_from_orchestrator_final() (+3 more)

### Community 21 - "decision_graph.py"
Cohesion: 0.18
Nodes (8): LogRecord, Infrastructure layer — pure plumbing (config, logging, LLM clients, observabilit, Backward-compatible re-export — prefer ``from infrastructure.llm import ...``., _InterceptHandler, Centralised logging — powered by **loguru**.  Usage (any module)::      from log, Route stdlib ``logging`` records into loguru so third-party libs     (uvicorn, h, Configure loguru for the current process. Call once at each entry-point.      Ar, setup_logging()

### Community 22 - "build_mcp_server_config"
Cohesion: 0.25
Nodes (6): main(), _text(), MCP servers — standardised bridge between agents and Convex travel APIs.    hote, build_mcp_server_config(), MCP client configuration — stdio subprocess launch for BookMe AI.  Consumed by `, Dict suitable for ``MultiServerMCPClient(server_config)``.

## Knowledge Gaps
- **46 isolated node(s):** `1. Create Virtual Environment`, `2. Install Dependencies`, `3. Configure API Key`, `4. Run the Backend`, `5. Run the Frontend` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_orchestrator()` connect `mcp_config.py` to `http_client.py`, `BookMe AI — Development Roadmap & Phase Log`, `infrastructure/llm.py`, `main.py`, `flight_server.py`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Why does `SessionStore` connect `infrastructure/llm.py` to `mcp_config.py`, `BookMe AI — Development Roadmap & Phase Log`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `AgentOrchestrator` connect `BookMe AI — Development Roadmap & Phase Log` to `infrastructure/llm.py`, `infrastructure/__init__.py`, `router.py`, `mcp_config.py`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `AgentOrchestrator` (e.g. with `_RecordingOrchestrator` and `.__init__()`) actually correct?**
  _`AgentOrchestrator` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `AgentState` (e.g. with `_RecordingOrchestrator` and `AgentOrchestrator`) actually correct?**
  _`AgentState` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `QueryRouter` (e.g. with `AgentOrchestrator` and `AgentResponse`) actually correct?**
  _`QueryRouter` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `SessionStore` (e.g. with `main()` and `_RecordingOrchestrator`) actually correct?**
  _`SessionStore` has 11 INFERRED edges - model-reasoned connections that need verification._