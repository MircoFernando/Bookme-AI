# Graph Report - Bookme AI  (2026-07-26)

## Corpus Check
- 38 files · ~16,828 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 367 nodes · 599 edges · 20 communities (17 shown, 3 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 48 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ec333709`
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
- HotelTool
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
1. `TripWeaver — Development Roadmap & Phase Log` - 19 edges
2. `QueryRouter` - 16 edges
3. `fetch_prompt()` - 14 edges
4. `Decision graph & routing — architecture notes` - 13 edges
5. `MultiRouteDecision` - 12 edges
6. `GraphState` - 11 edges
7. `build_decision_graph()` - 11 edges
8. `_request()` - 9 edges
9. `get_json()` - 9 edges
10. `_build_llm()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `_run()` --calls--> `map_decision_to_agent_state()`  [INFERRED]
  scripts/test_decision_graph.py → src/agents/decision_bridge.py
- `_run()` --calls--> `build_decision_graph()`  [INFERRED]
  scripts/test_decision_graph.py → src/agents/decision_graph.py
- `_run()` --calls--> `build_decision_input()`  [INFERRED]
  scripts/test_decision_graph.py → src/agents/decision_graph.py
- `main()` --calls--> `build_mcp_server_config()`  [INFERRED]
  scripts/test_mcp_client.py → src/mcp_servers/mcp_config.py
- `chat()` --references--> `ChatRequest`  [EXTRACTED]
  main.py → entity.py

## Import Cycles
- None detected.

## Communities (20 total, 3 thin omitted)

### Community 0 - "decision_graph.py"
Cohesion: 0.07
Nodes (32): AnyMessage, EmitFn, GuardrailVerdict, RunnableConfig, main(), _run(), map_decision_to_agent_state(), Bridge decision subgraph output → orchestrator ``AgentState`` (Week 13).  The ch (+24 more)

### Community 1 - "router.py"
Cohesion: 0.10
Nodes (25): make_router_node(), _fallback_multi(), get_query_router(), _last_user_text(), MultiRouteDecision, _normalize_action(), _normalize_params(), Any (+17 more)

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
Cohesion: 0.08
Nodes (18): LogRecord, Infrastructure layer — pure plumbing (config, logging, LLM clients, observabilit, _InterceptHandler, Centralised logging — powered by **loguru**.  Usage (any module)::      from log, Route stdlib ``logging`` records into loguru so third-party libs     (uvicorn, h, Configure loguru for the current process. Call once at each entry-point.      Ar, setup_logging(), Per-session conversation memory — kills the global-history bug.  The baseline ke (+10 more)

### Community 6 - "Decision graph & routing — architecture notes"
Cohesion: 0.08
Nodes (24): 10. Phase 4 status & acceptance, 11. Repository map (Phase 4 agents), 12. Questions for Week 13 / instructor (optional prompt), 1. Two-stage pipeline (mental model), 2. Week 13 architecture choice (two state types), 3. Decision graph topology (TripWeaver), 4.1 Both branches always start, 4.2 Fan-in before `decide` (+16 more)

### Community 7 - "TripWeaver — Development Roadmap & Phase Log"
Cohesion: 0.10
Nodes (19): Assessment mapping (SRS), Commands cheat sheet, Decision log (consolidated), High-level phase map, How to read this document, Next recommended step, Phase 0 — Baseline starter ✅, Phase 1 — Infrastructure & project skeleton ✅ (+11 more)

### Community 8 - "config.py"
Cohesion: 0.13
Nodes (19): dump(), get_api_key(), get_models(), _get_nested(), get_params(), _load_yaml(), _model_for(), provider_base_url() (+11 more)

### Community 9 - "infrastructure/llm.py"
Cohesion: 0.21
Nodes (17): ChatOpenAI, _build_llm(), get_chat_llm(), get_extractor_llm(), get_guardrail_llm(), get_router_llm(), _maybe_with_fallbacks(), Any (+9 more)

### Community 10 - "HotelTool"
Cohesion: 0.26
Nodes (7): _dumps(), _extract_hotels(), HotelTool, Any, Hotel tool — Convex hotel API (list / search / book).  Week 13 pattern: business, Hotel service actions routed by ``dispatch``., Map router aliases and drop Nones.

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
Cohesion: 0.31
Nodes (9): book_hotel(), _get_hotel(), list_hotels(), tool, Hotel MCP server — exposes HotelTool over the Model Context Protocol.  Thin tran, List all available hotels from the travel service., Search hotels by city and optional check-in/check-out dates (YYYY-MM-DD).      A, Book a hotel room.      Args:         hotel_id: Hotel identifier from search/lis (+1 more)

### Community 15 - "mcp_config.py"
Cohesion: 0.25
Nodes (5): main(), MCP servers — standardised bridge between agents and Convex travel APIs.    hote, build_mcp_server_config(), MCP client configuration — stdio subprocess launch for TripWeaver.  Consumed by, Dict suitable for ``MultiServerMCPClient(server_config)``.

### Community 16 - "frontend.py"
Cohesion: 0.60
Nodes (5): call_chat_api(), format_flights(), format_hotels(), main(), respond()

## Knowledge Gaps
- **46 isolated node(s):** `1. Create Virtual Environment`, `2. Install Dependencies`, `3. Configure API Key`, `4. Run the Backend`, `5. Run the Frontend` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HotelTool` connect `HotelTool` to `hotel_server.py`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `FlightTool` connect `http_client.py` to `flight_server.py`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `fetch_prompt()` (e.g. with `build_extractor_system_prompt()` and `build_flight_agent_system_prompt()`) actually correct?**
  _`fetch_prompt()` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `MultiRouteDecision` (e.g. with `DecisionState` and `AgentState`) actually correct?**
  _`MultiRouteDecision` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `1. Create Virtual Environment`, `2. Install Dependencies`, `3. Configure API Key` to the rest of the system?**
  _46 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `decision_graph.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06852497096399536 - nodes in this community are weakly interconnected._
- **Should `router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10121457489878542 - nodes in this community are weakly interconnected._