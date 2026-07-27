# Graph Report - Bookme AI  (2026-07-28)

## Corpus Check
- 93 files · ~203,131 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 840 nodes · 1408 edges · 57 communities (46 shown, 11 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 126 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `21b117c3`
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
- types.ts
- orchestrator.py
- Clerk production auth (BookMe AI)
- devDependencies
- dependencies
- useSessions.ts
- build_decision_graph
- ChatWindow.tsx
- ChatApp.tsx
- _RecordingOrchestrator
- ResponseMeta.tsx
- compilerOptions
- build_orchestrator
- auth.ts
- decision_graph.py
- main
- middleware.py
- useChatStream.ts
- api/main.py
- package.json
- scripts
- event_labels.py
- AgentResponse
- shadcn
- vite-env.d.ts
- vite.config.ts
- react
- postcss
- @types/react-dom

## God Nodes (most connected - your core abstractions)
1. `AgentOrchestrator` - 33 edges
2. `AgentState` - 30 edges
3. `QueryRouter` - 23 edges
4. `SessionStore` - 21 edges
5. `BookMe AI — Development Roadmap & Phase Log` - 20 edges
6. `compilerOptions` - 19 edges
7. `observe()` - 19 edges
8. `BookMe AI` - 18 edges
9. `fetch_prompt()` - 16 edges
10. `build_decision_graph()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `_RecordingOrchestrator` --uses--> `AgentOrchestrator`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/orchestrator.py
- `_RecordingOrchestrator` --uses--> `AgentState`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/state.py
- `_RecordingOrchestrator` --uses--> `SessionStore`  [INFERRED]
  scripts/test_chat_pipeline.py → src/infrastructure/session_store.py
- `main()` --calls--> `run_chat_turn()`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/chat_pipeline.py
- `main()` --calls--> `build_decision_graph()`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/decision_graph.py

## Import Cycles
- None detected.

## Communities (57 total, 11 thin omitted)

### Community 0 - "decision_graph.py"
Cohesion: 0.16
Nodes (14): AnyMessage, main(), _router_primary_route(), _run(), main(), map_decision_to_agent_state(), Bridge decision subgraph output → orchestrator ``AgentState`` (Week 13).  The ch, Copy classification results into fields the orchestrator expects. (+6 more)

### Community 1 - "router.py"
Cohesion: 0.12
Nodes (20): make_router_node(), _fallback_multi(), get_query_router(), _last_user_text(), MultiRouteDecision, _normalize_action(), _normalize_params(), Any (+12 more)

### Community 2 - "nodes.py"
Cohesion: 0.09
Nodes (40): GraphState, TypedDict, build_graph(), flight_node(), _format_flight(), _format_hotel(), generate_response(), hotel_node() (+32 more)

### Community 3 - "observability.py"
Cohesion: 0.09
Nodes (37): build_extractor_system_prompt(), build_flight_agent_system_prompt(), build_general_qa_system_prompt(), build_guardrail_system_prompt(), build_hotel_agent_system_prompt(), build_merge_system_prompt(), build_router_hard_rules_prompt(), build_router_prompt() (+29 more)

### Community 4 - "http_client.py"
Cohesion: 0.14
Nodes (16): _dumps(), _extract_hotels(), HotelTool, Any, Hotel tool — Convex hotel API (list / search / book).  Week 13 pattern: business, Hotel service actions routed by ``dispatch``., Map router aliases and drop Nones., book_hotel() (+8 more)

### Community 5 - "SessionStore"
Cohesion: 0.06
Nodes (54): ConfigResponse, HealthResponse, ReadinessResponse, RouteLiteral, _clerk_user_id(), get_decision_graph(), get_orchestrator(), get_session_store() (+46 more)

### Community 6 - "Decision graph & routing — architecture notes"
Cohesion: 0.04
Nodes (44): 10. Phase 4–6 status & acceptance, 11. Repository map (agents + API), 12. Questions for Week 13 / instructor (optional prompt), 1. Two-stage pipeline (mental model), 2. Week 13 architecture choice (two state types), 3. Decision graph topology (BookMe AI), 4.1 Both branches always start, 4.2 Fan-in before `decide` (+36 more)

### Community 7 - "BookMe AI — Development Roadmap & Phase Log"
Cohesion: 0.19
Nodes (14): AgentOrchestrator, _format_session_memory(), _last_user_text(), _llm_content_to_str(), _parse_inventory(), Any, Supervisor–worker LangGraph with parallel hotel / flight / general_qa / web_sear, Invoke with a bridged ``AgentState`` patch (Phase 6 path). (+6 more)

### Community 8 - "config.py"
Cohesion: 0.07
Nodes (40): _compact_results(), _dumps(), Any, Web search tool — Tavily Search API (travel / tourism Q&A).  Business logic live, Sync entry for scripts/tests., Tavily-backed web search for destination and tourism questions., WebSearchTool, dump() (+32 more)

### Community 9 - "infrastructure/llm.py"
Cohesion: 0.12
Nodes (14): main(), Per-session conversation memory — kills the global-history bug.  The baseline ke, Clear a single thread's history., Number of active threads (debug/health)., A single conversation turn., Stable composite key; isolates threads per authenticated user., Thread-safe, per-(user, session) rolling conversation history., Append a turn to a session's history (bounded window). (+6 more)

### Community 11 - "Setup"
Cohesion: 0.07
Nodes (28): 1. Clone & Install Backend, 2. Configure Environment, 3. Run the API, 4. Run the React UI, 🤖 Agent Pipeline, 📡 API Reference, ☁️ AWS Deployment, Backend (+20 more)

### Community 12 - "main.py"
Cohesion: 0.07
Nodes (16): App(), AuthMode, AuroraField(), LandingNav(), Reveal(), Stagger(), StaggerItem(), variants (+8 more)

### Community 13 - "flight_server.py"
Cohesion: 0.09
Nodes (30): Exception, retry, _dumps(), _extract_flights(), FlightTool, _normalize_airport(), Any, Flight tool — Convex flight API (list / search / book).  Same contract as ``Hote (+22 more)

### Community 15 - "mcp_config.py"
Cohesion: 0.19
Nodes (21): ChatOpenAI, _build_google_llm(), _build_llm(), get_chat_llm(), get_extractor_llm(), get_fast_chat_llm(), get_guardrail_llm(), get_merge_llm() (+13 more)

### Community 16 - "frontend.py"
Cohesion: 0.60
Nodes (5): call_chat_api(), format_flights(), format_hotels(), main(), respond()

### Community 20 - "infrastructure/__init__.py"
Cohesion: 0.30
Nodes (11): ChatResult, _noop_emit(), Any, EmitFn, Single async entry for one chat turn: decision graph → orchestrator (or OOS shor, One user turn — maps cleanly to ``api.schemas.ChatResponse``., Run decision graph, then orchestrator unless ``verdict == out_of_scope``.      L, _result_from_orchestrator_final() (+3 more)

### Community 21 - "decision_graph.py"
Cohesion: 0.18
Nodes (8): LogRecord, Infrastructure layer — pure plumbing (config, logging, LLM clients, observabilit, Backward-compatible re-export — prefer ``from infrastructure.llm import ...``., _InterceptHandler, Centralised logging — powered by **loguru**.  Usage (any module)::      from log, Route stdlib ``logging`` records into loguru so third-party libs     (uvicorn, h, Configure loguru for the current process. Call once at each entry-point.      Ar, setup_logging()

### Community 23 - "flight_server.py"
Cohesion: 0.08
Nodes (25): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleDetection (+17 more)

### Community 24 - "types.ts"
Cohesion: 0.13
Nodes (20): chatApi, systemApi, Props, STATUS_META, StatusBar(), ChatRequest, ChatResponse, ConfigResponse (+12 more)

### Community 25 - "orchestrator.py"
Cohesion: 0.13
Nodes (13): main(), _async_mcp_dispatch(), build_agent_mcp(), _mcp_result_to_str(), _MCPFlightToolAdapter, _MCPHotelToolAdapter, _MCPWebSearchToolAdapter, BookMe AI orchestrator — LangGraph fan-out after the decision subgraph.  Phase 6 (+5 more)

### Community 26 - "Clerk production auth (BookMe AI)"
Cohesion: 0.11
Nodes (17): 1. Clerk Dashboard, 2. Environment, 3. Verify, 4. Deploy (Phase 8), API (repo root `.env`), Chat returns 401 after sign-in, Clerk production auth (BookMe AI), `CLERK_SECRET_KEY is required` / API won't start (+9 more)

### Community 27 - "devDependencies"
Cohesion: 0.12
Nodes (17): autoprefixer, devDependencies, autoprefixer, shadcn, tailwindcss, @types/node, @types/react, typescript (+9 more)

### Community 28 - "dependencies"
Cohesion: 0.12
Nodes (17): @clerk/clerk-react, clsx, framer-motion, dependencies, @clerk/clerk-react, clsx, framer-motion, lucide-react (+9 more)

### Community 29 - "useSessions.ts"
Cohesion: 0.19
Nodes (10): Props, Sidebar(), Props, TravelToolsInfo(), loadSessions(), newSession(), saveSessions(), SessionMeta (+2 more)

### Community 30 - "build_decision_graph"
Cohesion: 0.17
Nodes (12): GuardrailVerdict, build_decision_graph(), make_guardrail_node(), Compile the decision subgraph (inject instances for tests)., _build_user_prompt(), get_guardrail(), Guardrail, Any (+4 more)

### Community 31 - "ChatWindow.tsx"
Cohesion: 0.24
Nodes (9): ChainOfThought(), pickIcon(), Props, StatusBadge(), ChatWindow(), Props, SAMPLE_PROMPTS, MessageBubble() (+1 more)

### Community 32 - "ChatApp.tsx"
Cohesion: 0.24
Nodes (7): setAuthTokenProvider(), InputBox(), Props, useHealth(), AppShell(), AuthMode, ChatAppClerk()

### Community 33 - "_RecordingOrchestrator"
Cohesion: 0.20
Nodes (5): main(), Minimal stand-in — records whether MCP path would run., _RecordingOrchestrator, Agent layer — LangGraph orchestration, routing, guardrail, and agent nodes.  Wee, AgentState — the shared state for the BookMe AI LangGraph.  Every node reads fro

### Community 34 - "ResponseMeta.tsx"
Cohesion: 0.29
Nodes (7): Props, Props, ResponseMeta(), ROUTE_ICONS, ROUTE_LABELS, Route, UIMessage

### Community 35 - "compilerOptions"
Cohesion: 0.20
Nodes (9): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, strict, include (+1 more)

### Community 36 - "build_orchestrator"
Cohesion: 0.24
Nodes (4): build_orchestrator(), _DirectWebSearchToolAdapter, In-process ``WebSearchTool`` for ``build_orchestrator`` debug path., In-process ``HotelTool`` / ``FlightTool`` (debug without MCP subprocesses).

### Community 37 - "auth.ts"
Cohesion: 0.31
Nodes (7): authHeaders(), AuthTokenProvider, isApiAuthDisabled(), chatPayload(), request(), AuthGate(), DevGateProps

### Community 38 - "decision_graph.py"
Cohesion: 0.25
Nodes (7): RunnableConfig, decide_node(), _emit_from_config(), Any, EmitFn, Decision LangGraph — Week 13 architecture (BookMe AI).  Small ``DecisionState``, Gate on guardrail; router can override a false-negative guardrail for tool route

### Community 39 - "main"
Cohesion: 0.25
Nodes (6): main(), _text(), MCP servers — standardised bridge between agents and Convex travel APIs.    hote, build_mcp_server_config(), MCP client configuration — stdio subprocess launch for BookMe AI.  Consumed by `, Dict suitable for ``MultiServerMCPClient(server_config)``.

### Community 40 - "middleware.py"
Cohesion: 0.29
Nodes (6): BaseHTTPMiddleware, install_middleware(), FastAPI, Request, HTTP middleware — request id, latency header, JSON 500 handler., RequestContextMiddleware

### Community 41 - "useChatStream.ts"
Cohesion: 0.36
Nodes (6): ApiError, formatStageDetail(), friendlyError(), stageLabelFromId(), useChatStream(), UseChatStreamArgs

### Community 42 - "api/main.py"
Cohesion: 0.33
Nodes (5): lifespan(), FastAPI, get, FastAPI application — BookMe AI travel assistant (Phase 6).  Start::      make r, root()

### Community 43 - "package.json"
Cohesion: 0.33
Nodes (5): description, name, private, type, version

### Community 44 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, preview

### Community 45 - "event_labels.py"
Cohesion: 0.40
Nodes (3): _stage_label_safe(), Friendly labels for streaming chain-of-thought events.  Maps internal stage / to, stage_label()

### Community 46 - "AgentResponse"
Cohesion: 0.50
Nodes (3): AgentResponse, Standalone turn: no decision graph (supervisor runs router)., One orchestrator turn — metadata for API / scripts.

## Knowledge Gaps
- **164 isolated node(s):** `npx`, `name`, `private`, `version`, `type` (+159 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_orchestrator()` connect `build_orchestrator` to `http_client.py`, `BookMe AI — Development Roadmap & Phase Log`, `config.py`, `infrastructure/llm.py`, `flight_server.py`, `mcp_config.py`, `orchestrator.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `AgentOrchestrator` connect `BookMe AI — Development Roadmap & Phase Log` to `_RecordingOrchestrator`, `router.py`, `build_orchestrator`, `infrastructure/llm.py`, `AgentResponse`, `infrastructure/__init__.py`, `orchestrator.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `SessionStore` connect `infrastructure/llm.py` to `_RecordingOrchestrator`, `build_orchestrator`, `BookMe AI — Development Roadmap & Phase Log`, `api/main.py`, `AgentResponse`, `orchestrator.py`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `AgentOrchestrator` (e.g. with `_RecordingOrchestrator` and `.__init__()`) actually correct?**
  _`AgentOrchestrator` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `AgentState` (e.g. with `_RecordingOrchestrator` and `AgentOrchestrator`) actually correct?**
  _`AgentState` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `QueryRouter` (e.g. with `AgentOrchestrator` and `AgentResponse`) actually correct?**
  _`QueryRouter` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `SessionStore` (e.g. with `main()` and `_RecordingOrchestrator`) actually correct?**
  _`SessionStore` has 12 INFERRED edges - model-reasoned connections that need verification._