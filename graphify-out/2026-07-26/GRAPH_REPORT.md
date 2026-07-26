# Graph Report - Bookme AI  (2026-07-26)

## Corpus Check
- 42 files · ~19,402 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 434 nodes · 789 edges · 20 communities (16 shown, 4 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 79 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7b7918d6`
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
- TripWeaver — Development Roadmap & Phase Log
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

## God Nodes (most connected - your core abstractions)
1. `AgentOrchestrator` - 25 edges
2. `AgentState` - 25 edges
3. `QueryRouter` - 21 edges
4. `TripWeaver — Development Roadmap & Phase Log` - 19 edges
5. `observe()` - 16 edges
6. `SessionStore` - 15 edges
7. `fetch_prompt()` - 14 edges
8. `Decision graph & routing — architecture notes` - 13 edges
9. `build_decision_graph()` - 12 edges
10. `MultiRouteDecision` - 12 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `build_agent_mcp()`  [INFERRED]
  scripts/test_orchestrator.py → src/agents/orchestrator.py
- `_run()` --calls--> `map_decision_to_agent_state()`  [INFERRED]
  scripts/test_decision_graph.py → src/agents/decision_bridge.py
- `_run()` --calls--> `build_decision_graph()`  [INFERRED]
  scripts/test_decision_graph.py → src/agents/decision_graph.py
- `_run()` --calls--> `build_decision_input()`  [INFERRED]
  scripts/test_decision_graph.py → src/agents/decision_graph.py
- `main()` --calls--> `build_mcp_server_config()`  [INFERRED]
  scripts/test_mcp_client.py → src/mcp_servers/mcp_config.py

## Import Cycles
- None detected.

## Communities (20 total, 4 thin omitted)

### Community 0 - "decision_graph.py"
Cohesion: 0.06
Nodes (35): AnyMessage, EmitFn, GuardrailVerdict, RunnableConfig, main(), _run(), main(), map_decision_to_agent_state() (+27 more)

### Community 1 - "router.py"
Cohesion: 0.12
Nodes (19): _fallback_multi(), get_query_router(), _last_user_text(), MultiRouteDecision, _normalize_action(), _normalize_params(), Any, QueryRouter (+11 more)

### Community 2 - "nodes.py"
Cohesion: 0.12
Nodes (30): GraphState, TypedDict, build_graph(), flight_node(), _format_flight(), _format_hotel(), generate_response(), hotel_node() (+22 more)

### Community 3 - "observability.py"
Cohesion: 0.11
Nodes (30): build_extractor_system_prompt(), build_flight_agent_system_prompt(), build_general_qa_system_prompt(), build_guardrail_system_prompt(), build_hotel_agent_system_prompt(), build_merge_system_prompt(), build_router_prompt(), build_router_system_prompt() (+22 more)

### Community 4 - "http_client.py"
Cohesion: 0.12
Nodes (21): Exception, retry, _dumps(), _extract_flights(), FlightTool, _normalize_airport(), Any, Flight tool — Convex flight API (list / search / book).  Same contract as ``Hote (+13 more)

### Community 5 - "SessionStore"
Cohesion: 0.10
Nodes (19): Assessment mapping (SRS), Commands cheat sheet, Decision log (consolidated), High-level phase map, How to read this document, Next recommended step, Phase 0 — Baseline starter ✅, Phase 1 — Infrastructure & project skeleton ✅ (+11 more)

### Community 6 - "Decision graph & routing — architecture notes"
Cohesion: 0.08
Nodes (24): 10. Phase 4 status & acceptance, 11. Repository map (Phase 4 agents), 12. Questions for Week 13 / instructor (optional prompt), 1. Two-stage pipeline (mental model), 2. Week 13 architecture choice (two state types), 3. Decision graph topology (TripWeaver), 4.1 Both branches always start, 4.2 Fan-in before `decide` (+16 more)

### Community 7 - "TripWeaver — Development Roadmap & Phase Log"
Cohesion: 0.09
Nodes (25): AgentOrchestrator, AgentResponse, _async_mcp_dispatch(), _format_session_memory(), _last_user_text(), _llm_content_to_str(), _mcp_result_to_str(), _MCPFlightToolAdapter (+17 more)

### Community 8 - "config.py"
Cohesion: 0.12
Nodes (26): dump(), get_api_key(), get_models(), _get_nested(), get_params(), _load_yaml(), _model_for(), provider_base_url() (+18 more)

### Community 9 - "infrastructure/llm.py"
Cohesion: 0.07
Nodes (19): LogRecord, Infrastructure layer — pure plumbing (config, logging, LLM clients, observabilit, Backward-compatible re-export — prefer ``from infrastructure.llm import ...``., _InterceptHandler, Centralised logging — powered by **loguru**.  Usage (any module)::      from log, Route stdlib ``logging`` records into loguru so third-party libs     (uvicorn, h, Configure loguru for the current process. Call once at each entry-point.      Ar, setup_logging() (+11 more)

### Community 11 - "Setup"
Cohesion: 0.17
Nodes (11): 1. Create Virtual Environment, 2. Install Dependencies, 3. Configure API Key, 4. Run the Backend, 5. Run the Frontend, API Endpoints, Booking Agents Backend, Chat Example (+3 more)

### Community 12 - "main.py"
Cohesion: 0.33
Nodes (9): ChatRequest, ChatResponse, BaseModel, get, chat(), hello(), list_flights(), list_hotels() (+1 more)

### Community 13 - "flight_server.py"
Cohesion: 0.31
Nodes (9): book_flight(), _get_flight(), list_flights(), tool, Flight MCP server — exposes FlightTool over the Model Context Protocol.  Run sta, List all available flights from the travel service., Search flights by origin, destination, and optional date (YYYY-MM-DD).      Args, Book a flight.      Args:         flight_id: Flight identifier from search/list (+1 more)

### Community 14 - "hotel_server.py"
Cohesion: 0.14
Nodes (16): _dumps(), _extract_hotels(), HotelTool, Any, Hotel tool — Convex hotel API (list / search / book).  Week 13 pattern: business, Hotel service actions routed by ``dispatch``., Map router aliases and drop Nones., book_hotel() (+8 more)

### Community 15 - "mcp_config.py"
Cohesion: 0.10
Nodes (30): ChatOpenAI, main(), build_agent_mcp(), build_orchestrator(), In-process ``HotelTool`` / ``FlightTool`` (debug without MCP subprocesses)., Assessment path — agents call Convex only through MCP stdio servers., _build_google_llm(), _build_llm() (+22 more)

### Community 16 - "frontend.py"
Cohesion: 0.60
Nodes (5): call_chat_api(), format_flights(), format_hotels(), main(), respond()

## Knowledge Gaps
- **46 isolated node(s):** `1. Create Virtual Environment`, `2. Install Dependencies`, `3. Configure API Key`, `4. Run the Backend`, `5. Run the Frontend` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_orchestrator()` connect `mcp_config.py` to `infrastructure/llm.py`, `http_client.py`, `hotel_server.py`, `TripWeaver — Development Roadmap & Phase Log`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `SessionStore` connect `infrastructure/llm.py` to `mcp_config.py`, `TripWeaver — Development Roadmap & Phase Log`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `AgentOrchestrator` connect `TripWeaver — Development Roadmap & Phase Log` to `router.py`, `infrastructure/llm.py`, `mcp_config.py`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `AgentOrchestrator` (e.g. with `QueryRouter` and `AgentState`) actually correct?**
  _`AgentOrchestrator` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `AgentState` (e.g. with `AgentOrchestrator` and `AgentResponse`) actually correct?**
  _`AgentState` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `QueryRouter` (e.g. with `AgentOrchestrator` and `AgentResponse`) actually correct?**
  _`QueryRouter` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `1. Create Virtual Environment`, `2. Install Dependencies`, `3. Configure API Key` to the rest of the system?**
  _46 weakly-connected nodes found - possible documentation gaps or missing edges._