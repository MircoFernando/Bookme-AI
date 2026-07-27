# Graph Report - Bookme AI  (2026-07-28)

## Corpus Check
- 95 files · ~204,201 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 856 nodes · 1424 edges · 53 communities (42 shown, 11 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 126 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ace8879f`
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
- SessionStore
- flight_server.py
- types.ts
- AgentOrchestrator
- Clerk production auth (BookMe AI)
- devDependencies
- dependencies
- useSessions.ts
- chat_pipeline.py
- ChatWindow.tsx
- ChatApp.tsx
- main
- decision_bridge.py
- compilerOptions
- vercel.json
- auth.ts
- AgentResponse
- middleware.py
- useChatStream.ts
- package.json
- scripts
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
- `main()` --calls--> `SessionStore`  [INFERRED]
  scripts/test_session_store.py → src/infrastructure/session_store.py
- `_RecordingOrchestrator` --uses--> `AgentOrchestrator`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/orchestrator.py
- `_RecordingOrchestrator` --uses--> `AgentState`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/state.py
- `main()` --calls--> `run_chat_turn()`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/chat_pipeline.py
- `main()` --calls--> `build_decision_graph()`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/decision_graph.py

## Import Cycles
- None detected.

## Communities (53 total, 11 thin omitted)

### Community 0 - "decision_graph.py"
Cohesion: 0.06
Nodes (36): AnyMessage, GuardrailVerdict, RunnableConfig, main(), _router_primary_route(), _run(), map_decision_to_agent_state(), Copy classification results into fields the orchestrator expects. (+28 more)

### Community 1 - "router.py"
Cohesion: 0.11
Nodes (21): _fallback_multi(), get_query_router(), _last_user_text(), MultiRouteDecision, _normalize_action(), _normalize_params(), Any, QueryRouter (+13 more)

### Community 2 - "nodes.py"
Cohesion: 0.09
Nodes (40): GraphState, TypedDict, build_graph(), flight_node(), _format_flight(), _format_hotel(), generate_response(), hotel_node() (+32 more)

### Community 3 - "observability.py"
Cohesion: 0.09
Nodes (34): build_extractor_system_prompt(), build_flight_agent_system_prompt(), build_general_qa_system_prompt(), build_hotel_agent_system_prompt(), build_merge_system_prompt(), build_router_hard_rules_prompt(), build_router_prompt(), build_router_system_prompt() (+26 more)

### Community 4 - "http_client.py"
Cohesion: 0.31
Nodes (9): book_hotel(), _get_hotel(), list_hotels(), tool, Hotel MCP server — exposes HotelTool over the Model Context Protocol.  Thin tran, List all available hotels from the travel service., Search hotels by city and optional check-in/check-out dates (YYYY-MM-DD).      A, Book a hotel room.      Args:         hotel_id: Hotel identifier from search/lis (+1 more)

### Community 5 - "SessionStore"
Cohesion: 0.05
Nodes (58): ConfigResponse, HealthResponse, ReadinessResponse, RouteLiteral, _clerk_user_id(), get_decision_graph(), get_orchestrator(), get_session_store() (+50 more)

### Community 6 - "Decision graph & routing — architecture notes"
Cohesion: 0.04
Nodes (44): 10. Phase 4–6 status & acceptance, 11. Repository map (agents + API), 12. Questions for Week 13 / instructor (optional prompt), 1. Two-stage pipeline (mental model), 2. Week 13 architecture choice (two state types), 3. Decision graph topology (BookMe AI), 4.1 Both branches always start, 4.2 Fan-in before `decide` (+36 more)

### Community 7 - "BookMe AI — Development Roadmap & Phase Log"
Cohesion: 0.25
Nodes (11): _format_session_memory(), _last_user_text(), _llm_content_to_str(), _parse_inventory(), Any, Normalize OpenAI/Gemini message content to plain text., _tool_status(), AgentState (+3 more)

### Community 8 - "config.py"
Cohesion: 0.07
Nodes (40): _compact_results(), _dumps(), Any, Web search tool — Tavily Search API (travel / tourism Q&A).  Business logic live, Sync entry for scripts/tests., Tavily-backed web search for destination and tourism questions., WebSearchTool, dump() (+32 more)

### Community 9 - "infrastructure/llm.py"
Cohesion: 0.07
Nodes (19): LogRecord, main(), Infrastructure layer — pure plumbing (config, logging, LLM clients, observabilit, Backward-compatible re-export — prefer ``from infrastructure.llm import ...``., _InterceptHandler, Centralised logging — powered by **loguru**.  Usage (any module)::      from log, Route stdlib ``logging`` records into loguru so third-party libs     (uvicorn, h, Configure loguru for the current process. Call once at each entry-point.      Ar (+11 more)

### Community 11 - "Setup"
Cohesion: 0.07
Nodes (29): 1. Clone & Install Backend, 2. Configure Environment, 3. Run the API, 4. Run the React UI, 5. Docker (API + nginx UI), 🤖 Agent Pipeline, 📡 API Reference, Backend (+21 more)

### Community 12 - "main.py"
Cohesion: 0.09
Nodes (13): AuroraField(), LandingNav(), Reveal(), Stagger(), StaggerItem(), variants, AnimatedGradientBackground(), AnimatedGradientBackgroundProps (+5 more)

### Community 13 - "flight_server.py"
Cohesion: 0.07
Nodes (37): Exception, retry, _dumps(), _extract_flights(), FlightTool, _normalize_airport(), Any, Flight tool — Convex flight API (list / search / book).  Same contract as ``Hote (+29 more)

### Community 15 - "mcp_config.py"
Cohesion: 0.19
Nodes (21): ChatOpenAI, _build_google_llm(), _build_llm(), get_chat_llm(), get_extractor_llm(), get_fast_chat_llm(), get_guardrail_llm(), get_merge_llm() (+13 more)

### Community 16 - "frontend.py"
Cohesion: 0.60
Nodes (5): call_chat_api(), format_flights(), format_hotels(), main(), respond()

### Community 20 - "infrastructure/__init__.py"
Cohesion: 0.12
Nodes (14): main(), main(), _async_mcp_dispatch(), build_agent_mcp(), _mcp_result_to_str(), _MCPFlightToolAdapter, _MCPHotelToolAdapter, _MCPWebSearchToolAdapter (+6 more)

### Community 21 - "SessionStore"
Cohesion: 0.14
Nodes (10): main(), Minimal stand-in — records whether MCP path would run., _RecordingOrchestrator, build_orchestrator(), _DirectWebSearchToolAdapter, In-process ``WebSearchTool`` for ``build_orchestrator`` debug path., In-process ``HotelTool`` / ``FlightTool`` (debug without MCP subprocesses)., Number of active threads (debug/health). (+2 more)

### Community 23 - "flight_server.py"
Cohesion: 0.08
Nodes (25): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleDetection (+17 more)

### Community 24 - "types.ts"
Cohesion: 0.12
Nodes (20): BASE, systemApi, Props, STATUS_META, StatusBar(), ChatRequest, ChatResponse, ConfigResponse (+12 more)

### Community 25 - "AgentOrchestrator"
Cohesion: 0.22
Nodes (3): AgentOrchestrator, Supervisor–worker LangGraph with parallel hotel / flight / general_qa / web_sear, Invoke with a bridged ``AgentState`` patch (Phase 6 path).

### Community 26 - "Clerk production auth (BookMe AI)"
Cohesion: 0.07
Nodes (23): 1. Clerk Dashboard, 2. Environment, 3. Verify, 4. Deploy (Phase 8), API (repo root `.env`), Chat returns 401 after sign-in, Clerk production auth (BookMe AI), `CLERK_SECRET_KEY is required` / API won't start (+15 more)

### Community 27 - "devDependencies"
Cohesion: 0.12
Nodes (17): autoprefixer, devDependencies, autoprefixer, shadcn, tailwindcss, @types/node, @types/react, typescript (+9 more)

### Community 28 - "dependencies"
Cohesion: 0.12
Nodes (17): @clerk/clerk-react, clsx, framer-motion, dependencies, @clerk/clerk-react, clsx, framer-motion, lucide-react (+9 more)

### Community 29 - "useSessions.ts"
Cohesion: 0.19
Nodes (10): Props, Sidebar(), Props, TravelToolsInfo(), loadSessions(), newSession(), saveSessions(), SessionMeta (+2 more)

### Community 30 - "chat_pipeline.py"
Cohesion: 0.30
Nodes (11): ChatResult, _noop_emit(), Any, EmitFn, Single async entry for one chat turn: decision graph → orchestrator (or OOS shor, One user turn — maps cleanly to ``api.schemas.ChatResponse``., Run decision graph, then orchestrator unless ``verdict == out_of_scope``.      L, _result_from_orchestrator_final() (+3 more)

### Community 31 - "ChatWindow.tsx"
Cohesion: 0.14
Nodes (16): ChainOfThought(), pickIcon(), Props, StatusBadge(), ChatWindow(), Props, SAMPLE_PROMPTS, MessageBubble() (+8 more)

### Community 32 - "ChatApp.tsx"
Cohesion: 0.17
Nodes (10): setAuthTokenProvider(), App(), AuthMode, InputBox(), Props, useHealth(), AppShell(), AuthMode (+2 more)

### Community 33 - "main"
Cohesion: 0.25
Nodes (6): main(), _text(), MCP servers — standardised bridge between agents and Convex travel APIs.    hote, build_mcp_server_config(), MCP client configuration — stdio subprocess launch for BookMe AI.  Consumed by `, Dict suitable for ``MultiServerMCPClient(server_config)``.

### Community 34 - "decision_bridge.py"
Cohesion: 0.32
Nodes (4): Bridge decision subgraph output → orchestrator ``AgentState`` (Week 13).  The ch, Decision subgraph state (Week 13 pattern).  Separate from ``AgentState``: the de, Agent layer — LangGraph orchestration, routing, guardrail, and agent nodes.  Wee, AgentState — the shared state for the BookMe AI LangGraph.  Every node reads fro

### Community 35 - "compilerOptions"
Cohesion: 0.20
Nodes (9): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, strict, include (+1 more)

### Community 36 - "vercel.json"
Cohesion: 0.33
Nodes (5): buildCommand, framework, outputDirectory, rewrites, $schema

### Community 37 - "auth.ts"
Cohesion: 0.31
Nodes (7): authHeaders(), AuthTokenProvider, isApiAuthDisabled(), chatPayload(), request(), AuthGate(), DevGateProps

### Community 38 - "AgentResponse"
Cohesion: 0.50
Nodes (3): AgentResponse, Standalone turn: no decision graph (supervisor runs router)., One orchestrator turn — metadata for API / scripts.

### Community 40 - "middleware.py"
Cohesion: 0.29
Nodes (6): BaseHTTPMiddleware, install_middleware(), FastAPI, Request, HTTP middleware — request id, latency header, JSON 500 handler., RequestContextMiddleware

### Community 41 - "useChatStream.ts"
Cohesion: 0.31
Nodes (7): ApiError, chatApi, formatStageDetail(), friendlyError(), stageLabelFromId(), useChatStream(), UseChatStreamArgs

### Community 43 - "package.json"
Cohesion: 0.33
Nodes (5): description, name, private, type, version

### Community 44 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, preview

## Knowledge Gaps
- **176 isolated node(s):** `npx`, `name`, `private`, `version`, `type` (+171 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_orchestrator()` connect `SessionStore` to `BookMe AI — Development Roadmap & Phase Log`, `config.py`, `flight_server.py`, `mcp_config.py`, `infrastructure/__init__.py`, `AgentOrchestrator`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `AgentOrchestrator` connect `AgentOrchestrator` to `router.py`, `AgentResponse`, `BookMe AI — Development Roadmap & Phase Log`, `infrastructure/__init__.py`, `SessionStore`, `chat_pipeline.py`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `SessionStore` connect `SessionStore` to `SessionStore`, `AgentResponse`, `infrastructure/llm.py`, `infrastructure/__init__.py`, `AgentOrchestrator`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `AgentOrchestrator` (e.g. with `_RecordingOrchestrator` and `.__init__()`) actually correct?**
  _`AgentOrchestrator` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `AgentState` (e.g. with `_RecordingOrchestrator` and `AgentOrchestrator`) actually correct?**
  _`AgentState` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `QueryRouter` (e.g. with `AgentOrchestrator` and `AgentResponse`) actually correct?**
  _`QueryRouter` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `SessionStore` (e.g. with `main()` and `_RecordingOrchestrator`) actually correct?**
  _`SessionStore` has 12 INFERRED edges - model-reasoned connections that need verification._