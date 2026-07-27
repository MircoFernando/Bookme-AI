# Graph Report - Bookme AI  (2026-07-27)

## Corpus Check
- 49 files · ~21,687 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 485 nodes · 896 edges · 24 communities (20 shown, 4 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 100 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e6a16f34`
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
- decision_bridge.py

## God Nodes (most connected - your core abstractions)
1. `AgentOrchestrator` - 31 edges
2. `AgentState` - 27 edges
3. `QueryRouter` - 21 edges
4. `BookMe AI — Development Roadmap & Phase Log` - 19 edges
5. `observe()` - 18 edges
6. `SessionStore` - 18 edges
7. `fetch_prompt()` - 15 edges
8. `run_chat_turn()` - 14 edges
9. `build_decision_graph()` - 13 edges
10. `Decision graph & routing — architecture notes` - 13 edges

## Surprising Connections (you probably didn't know these)
- `_RecordingOrchestrator` --uses--> `AgentOrchestrator`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/orchestrator.py
- `_RecordingOrchestrator` --uses--> `AgentState`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/state.py
- `main()` --calls--> `run_chat_turn()`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/chat_pipeline.py
- `main()` --calls--> `build_decision_graph()`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/decision_graph.py
- `main()` --calls--> `build_agent_mcp()`  [INFERRED]
  scripts/test_orchestrator.py → src/agents/orchestrator.py

## Import Cycles
- None detected.

## Communities (24 total, 4 thin omitted)

### Community 0 - "decision_graph.py"
Cohesion: 0.07
Nodes (32): AnyMessage, GuardrailVerdict, RunnableConfig, main(), _run(), main(), map_decision_to_agent_state(), Bridge decision subgraph output → orchestrator ``AgentState`` (Week 13).  The ch (+24 more)

### Community 1 - "router.py"
Cohesion: 0.12
Nodes (20): make_router_node(), _fallback_multi(), get_query_router(), _last_user_text(), MultiRouteDecision, _normalize_action(), _normalize_params(), Any (+12 more)

### Community 2 - "nodes.py"
Cohesion: 0.09
Nodes (39): GraphState, TypedDict, build_graph(), flight_node(), _format_flight(), _format_hotel(), generate_response(), hotel_node() (+31 more)

### Community 3 - "observability.py"
Cohesion: 0.10
Nodes (32): build_extractor_system_prompt(), build_flight_agent_system_prompt(), build_general_qa_system_prompt(), build_guardrail_system_prompt(), build_hotel_agent_system_prompt(), build_merge_system_prompt(), build_router_hard_rules_prompt(), build_router_prompt() (+24 more)

### Community 4 - "http_client.py"
Cohesion: 0.12
Nodes (21): Exception, retry, _dumps(), _extract_flights(), FlightTool, _normalize_airport(), Any, Flight tool — Convex flight API (list / search / book).  Same contract as ``Hote (+13 more)

### Community 5 - "SessionStore"
Cohesion: 0.10
Nodes (19): Assessment mapping (SRS), BookMe AI — Development Roadmap & Phase Log, Commands cheat sheet, Decision log (consolidated), High-level phase map, How to read this document, Next recommended step, Phase 0 — Baseline starter ✅ (+11 more)

### Community 6 - "Decision graph & routing — architecture notes"
Cohesion: 0.08
Nodes (24): 10. Phase 4 status & acceptance, 11. Repository map (Phase 4 agents), 12. Questions for Week 13 / instructor (optional prompt), 1. Two-stage pipeline (mental model), 2. Week 13 architecture choice (two state types), 3. Decision graph topology (BookMe AI), 4.1 Both branches always start, 4.2 Fan-in before `decide` (+16 more)

### Community 7 - "BookMe AI — Development Roadmap & Phase Log"
Cohesion: 0.08
Nodes (32): Agent layer — LangGraph orchestration, routing, guardrail, and agent nodes.  Wee, AgentOrchestrator, AgentResponse, _async_mcp_dispatch(), build_agent_mcp(), build_orchestrator(), _format_session_memory(), _last_user_text() (+24 more)

### Community 8 - "config.py"
Cohesion: 0.12
Nodes (26): dump(), get_api_key(), get_models(), _get_nested(), get_params(), _load_yaml(), _model_for(), provider_base_url() (+18 more)

### Community 9 - "infrastructure/llm.py"
Cohesion: 0.09
Nodes (17): main(), Minimal stand-in — records whether MCP path would run., _RecordingOrchestrator, main(), Per-session conversation memory — kills the global-history bug.  The baseline ke, Clear a single thread's history., Number of active threads (debug/health)., A single conversation turn. (+9 more)

### Community 11 - "Setup"
Cohesion: 0.17
Nodes (11): 1. Create Virtual Environment, 2. Install Dependencies, 3. Configure API Key, 4. Run the Backend, 5. Run the Frontend, API Endpoints, BookMe AI, Chat Example (+3 more)

### Community 12 - "main.py"
Cohesion: 0.23
Nodes (8): main(), _compact_results(), _dumps(), Any, Web search tool — Tavily Search API for general travel / tourism Q&A.  Returns a, Sync wrapper for scripts/tests., Tavily-backed web search for travel and destination questions., WebSearchTool

### Community 13 - "flight_server.py"
Cohesion: 0.31
Nodes (9): book_flight(), _get_flight(), list_flights(), tool, Flight MCP server — exposes FlightTool over the Model Context Protocol.  Run sta, List all available flights from the travel service., Search flights by origin, destination, and optional date (YYYY-MM-DD).      Args, Book a flight.      Args:         flight_id: Flight identifier from search/list (+1 more)

### Community 14 - "hotel_server.py"
Cohesion: 0.14
Nodes (16): _dumps(), _extract_hotels(), HotelTool, Any, Hotel tool — Convex hotel API (list / search / book).  Week 13 pattern: business, Hotel service actions routed by ``dispatch``., Map router aliases and drop Nones., book_hotel() (+8 more)

### Community 15 - "mcp_config.py"
Cohesion: 0.19
Nodes (21): ChatOpenAI, _build_google_llm(), _build_llm(), get_chat_llm(), get_extractor_llm(), get_fast_chat_llm(), get_guardrail_llm(), get_merge_llm() (+13 more)

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
Nodes (5): main(), MCP servers — standardised bridge between agents and Convex travel APIs.    hote, build_mcp_server_config(), MCP client configuration — stdio subprocess launch for BookMe AI.  Consumed by `, Dict suitable for ``MultiServerMCPClient(server_config)``.

### Community 23 - "decision_bridge.py"
Cohesion: 0.24
Nodes (10): _check(), main(), _for_pattern_match(), general_qa_needs_web_search(), _normalize(), Deterministic Tavily gate for ``general_qa_agent_node``.  Skips web search on pu, JSON placeholder when Tavily is intentionally skipped., Lowercase single line, no trailing punctuation. (+2 more)

## Knowledge Gaps
- **46 isolated node(s):** `1. Create Virtual Environment`, `2. Install Dependencies`, `3. Configure API Key`, `4. Run the Backend`, `5. Run the Frontend` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_orchestrator()` connect `BookMe AI — Development Roadmap & Phase Log` to `http_client.py`, `infrastructure/llm.py`, `main.py`, `hotel_server.py`, `mcp_config.py`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `AgentOrchestrator` connect `BookMe AI — Development Roadmap & Phase Log` to `decision_graph.py`, `infrastructure/llm.py`, `infrastructure/__init__.py`, `router.py`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `SessionStore` connect `infrastructure/llm.py` to `BookMe AI — Development Roadmap & Phase Log`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `AgentOrchestrator` (e.g. with `_RecordingOrchestrator` and `.__init__()`) actually correct?**
  _`AgentOrchestrator` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `AgentState` (e.g. with `_RecordingOrchestrator` and `AgentOrchestrator`) actually correct?**
  _`AgentState` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `QueryRouter` (e.g. with `AgentOrchestrator` and `AgentResponse`) actually correct?**
  _`QueryRouter` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `1. Create Virtual Environment`, `2. Install Dependencies`, `3. Configure API Key` to the rest of the system?**
  _46 weakly-connected nodes found - possible documentation gaps or missing edges._