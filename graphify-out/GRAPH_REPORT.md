# Graph Report - Bookme AI  (2026-08-01)

## Corpus Check
- 102 files · ~288,310 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 959 nodes · 1600 edges · 62 communities (51 shown, 11 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 132 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1ff1598a`
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
- compilerOptions
- vercel.json
- auth.ts
- AgentResponse
- BookMe AI — React UI
- middleware.py
- useChatStream.ts
- 4. Parallel guardrail + router — runtime behavior
- package.json
- scripts
- build_agent_mcp
- orchestrator.py
- shadcn
- vite-env.d.ts
- vite.config.ts
- react
- postcss
- @types/react-dom
- infrastructure/__init__.py
- _RecordingOrchestrator
- _llm_content_to_str
- BookMeLogo.tsx
- AgentResponse

## God Nodes (most connected - your core abstractions)
1. `AgentOrchestrator` - 32 edges
2. `AgentState` - 32 edges
3. `SessionStore` - 25 edges
4. `BookMe AI — Development Roadmap & Phase Log` - 21 edges
5. `compilerOptions` - 19 edges
6. `observe()` - 19 edges
7. `BookMe AI` - 18 edges
8. `QueryRouter` - 17 edges
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

## Communities (62 total, 11 thin omitted)

### Community 0 - "decision_graph.py"
Cohesion: 0.07
Nodes (35): AnyMessage, main(), _router_primary_route(), _run(), main(), map_decision_to_agent_state(), Bridge decision subgraph output → orchestrator ``AgentState``.  The chat/API lay, Copy classification results into fields the orchestrator expects. (+27 more)

### Community 1 - "router.py"
Cohesion: 0.11
Nodes (21): _fallback_multi(), get_query_router(), _last_user_text(), MultiRouteDecision, _normalize_action(), _normalize_params(), Any, QueryRouter (+13 more)

### Community 2 - "nodes.py"
Cohesion: 0.09
Nodes (40): GraphState, TypedDict, build_graph(), flight_node(), _format_flight(), _format_hotel(), generate_response(), hotel_node() (+32 more)

### Community 3 - "observability.py"
Cohesion: 0.15
Nodes (19): RouteLiteral, ChatResult, _noop_emit(), Any, EmitFn, Single async entry for one chat turn: decision graph → orchestrator (or OOS shor, One user turn — maps cleanly to ``api.schemas.ChatResponse``., Run decision graph, then orchestrator unless ``verdict == out_of_scope``.      L (+11 more)

### Community 4 - "http_client.py"
Cohesion: 0.09
Nodes (32): main(), Integration: book by flight number when candidates supplied., test_book_with_flight_number_mock_candidates(), test_convex_id_detection(), test_resolve_from_candidate_airline_label(), test_resolve_from_candidate_flight_number(), test_session_inventory_memory_format(), _dedupe_flights() (+24 more)

### Community 5 - "SessionStore"
Cohesion: 0.06
Nodes (51): ConfigResponse, HealthResponse, ReadinessResponse, _clerk_user_id(), get_decision_graph(), get_orchestrator(), get_session_store(), is_auth_disabled() (+43 more)

### Community 6 - "Decision graph & routing — architecture notes"
Cohesion: 0.08
Nodes (26): Assessment mapping (SRS), BookMe AI — Development Roadmap & Phase Log, Commands cheat sheet, Decision log (consolidated), High-level phase map, How to read this document, Next recommended step, Phase 0 — Baseline starter ✅ (+18 more)

### Community 7 - "BookMe AI — Development Roadmap & Phase Log"
Cohesion: 0.19
Nodes (14): AgentOrchestrator, _emit_from_config(), _last_user_text(), _parse_inventory(), _persist_flight_inventory(), RunnableConfig, Supervisor–worker LangGraph with parallel hotel / flight / general_qa / web_sear, Invoke with a bridged ``AgentState`` patch (Phase 6 path). (+6 more)

### Community 8 - "config.py"
Cohesion: 0.05
Nodes (46): main(), _text(), _compact_results(), _dumps(), Any, Web search tool — Tavily Search API (travel / tourism Q&A).  Business logic live, Sync entry for scripts/tests., Tavily-backed web search for destination and tourism questions. (+38 more)

### Community 9 - "infrastructure/llm.py"
Cohesion: 0.10
Nodes (16): main(), Per-session conversation memory — kills the global-history bug.  The baseline ke, Merge flight search/list results by ``_id`` for follow-up booking., Compact catalog for router/agents (includes Convex ``flight_id``)., Clear a single thread's history., Number of active threads (debug/health)., A single conversation turn., Stable composite key; isolates threads per authenticated user. (+8 more)

### Community 11 - "Setup"
Cohesion: 0.05
Nodes (41): 1. One-time install, 1. Root `.env`, 2. Environment files, 2. Start stack, 3. Auth mode (pick one), 4. Run (two terminals), 5. Smoke test, 🤖 Agent Pipeline (+33 more)

### Community 12 - "main.py"
Cohesion: 0.07
Nodes (16): App(), AuthMode, AuroraField(), LandingNav(), Reveal(), Stagger(), StaggerItem(), variants (+8 more)

### Community 13 - "flight_server.py"
Cohesion: 0.08
Nodes (30): Exception, retry, _dumps(), _extract_hotels(), HotelTool, Any, Hotel tool — Convex hotel API (list / search / book).  Business logic lives here, Hotel service actions routed by ``dispatch``. (+22 more)

### Community 15 - "mcp_config.py"
Cohesion: 0.19
Nodes (21): ChatOpenAI, _build_google_llm(), _build_llm(), get_chat_llm(), get_extractor_llm(), get_fast_chat_llm(), get_guardrail_llm(), get_merge_llm() (+13 more)

### Community 16 - "frontend.py"
Cohesion: 0.60
Nodes (5): call_chat_api(), format_flights(), format_hotels(), main(), respond()

### Community 20 - "infrastructure/__init__.py"
Cohesion: 0.07
Nodes (27): 1. Build your hostname from the droplet IP, 2.1 Install Docker, 2.2 Clone repo (path must match the workflow), 2.3 Configure environment, 2.4 Pull and start API (first deploy), 2.5 HTTPS (before browsers / Vercel), 2. Caddy on the same droplet (second block), 3. Same droplet checklist (no domain) (+19 more)

### Community 21 - "SessionStore"
Cohesion: 0.08
Nodes (37): GuardrailVerdict, _build_user_prompt(), Classify *message* as ``in_scope`` or ``out_of_scope``.          *memory_context, build_extractor_system_prompt(), build_flight_agent_system_prompt(), build_general_qa_system_prompt(), build_guardrail_system_prompt(), build_hotel_agent_system_prompt() (+29 more)

### Community 23 - "flight_server.py"
Cohesion: 0.08
Nodes (25): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleDetection (+17 more)

### Community 24 - "types.ts"
Cohesion: 0.12
Nodes (18): systemApi, Props, STATUS_META, StatusBar(), ConfigResponse, ErrorEvent, FinalEvent, ReadinessCheck (+10 more)

### Community 25 - "AgentOrchestrator"
Cohesion: 0.15
Nodes (13): 10. Phase 4–6 status & acceptance, 11. Repository map (agents + API), 1. Two-stage pipeline (mental model), 2. Two state types, 3. Decision graph topology (BookMe AI), 5. Router (BookMe AI domain), 6. Guardrail, 7. Bridge module (`decision_bridge.py`) (+5 more)

### Community 26 - "Clerk production auth (BookMe AI)"
Cohesion: 0.17
Nodes (12): 1. Clerk Dashboard, 2. Environment, 3. Verify, 4. Deploy (Phase 8), API (repo root `.env`), Chat returns 401 after sign-in, Clerk production auth (BookMe AI), `CLERK_SECRET_KEY is required` / API won't start (+4 more)

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
Cohesion: 0.20
Nodes (10): 1. DigitalOcean — API on a Droplet, 2. Vercel — frontend (unchanged), 3. Verify, 4. DO App Platform (alternative), App deploy (pull image), CI/CD (booking-platform-api pattern), Deploy BookMe AI — DigitalOcean (API) + Vercel (frontend), One-time server setup (+2 more)

### Community 31 - "ChatWindow.tsx"
Cohesion: 0.24
Nodes (9): ChainOfThought(), pickIcon(), Props, StatusBadge(), ChatWindow(), Props, SAMPLE_PROMPTS, MessageBubble() (+1 more)

### Community 32 - "ChatApp.tsx"
Cohesion: 0.24
Nodes (7): setAuthTokenProvider(), InputBox(), Props, useHealth(), AppShell(), AuthMode, ChatAppClerk()

### Community 33 - "main"
Cohesion: 0.29
Nodes (7): Props, Props, ResponseMeta(), ROUTE_ICONS, ROUTE_LABELS, Route, UIMessage

### Community 35 - "compilerOptions"
Cohesion: 0.20
Nodes (9): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, strict, include (+1 more)

### Community 36 - "vercel.json"
Cohesion: 0.33
Nodes (5): buildCommand, framework, outputDirectory, rewrites, $schema

### Community 37 - "auth.ts"
Cohesion: 0.20
Nodes (11): authHeaders(), AuthTokenProvider, isApiAuthDisabled(), BASE, chatApi, chatPayload(), request(), AuthGate() (+3 more)

### Community 38 - "AgentResponse"
Cohesion: 0.29
Nodes (7): Configuration, Disable token streaming, Event types, Frontend, Streaming — SSE progress + LLM token deltas, Viva talking points, Where tokens are streamed (backend)

### Community 39 - "BookMe AI — React UI"
Cohesion: 0.33
Nodes (6): Auth modes, BookMe AI — React UI, Deploy (Vercel), One-time setup (from repo root), Run locally (two terminals, repo root), Structure

### Community 40 - "middleware.py"
Cohesion: 0.29
Nodes (6): BaseHTTPMiddleware, install_middleware(), FastAPI, Request, HTTP middleware — request id, latency header, JSON 500 handler., RequestContextMiddleware

### Community 41 - "useChatStream.ts"
Cohesion: 0.31
Nodes (7): ApiError, formatStageDetail(), friendlyError(), stageLabelFromId(), useChatStream(), UseChatStreamArgs, StreamEvent

### Community 42 - "4. Parallel guardrail + router — runtime behavior"
Cohesion: 0.40
Nodes (5): 4.1 Both branches always start, 4.2 Fan-in before `decide`, 4.3 Off-topic example: “Who is the president?”, 4.4 Two meanings of “instant return”, 4. Parallel guardrail + router — runtime behavior

### Community 43 - "package.json"
Cohesion: 0.33
Nodes (5): description, name, private, type, version

### Community 44 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, preview

### Community 45 - "build_agent_mcp"
Cohesion: 0.10
Nodes (12): main(), _async_mcp_dispatch(), build_agent_mcp(), _mcp_result_to_str(), _MCPFlightToolAdapter, _MCPHotelToolAdapter, _MCPWebSearchToolAdapter, MCP hotel tools → ``dispatch(action, params)`` (sync or async). (+4 more)

### Community 46 - "orchestrator.py"
Cohesion: 0.19
Nodes (15): build_orchestrator(), _DirectWebSearchToolAdapter, _format_session_memory(), _invoke_llm_text(), _prepare_flight_book_params(), Any, EmitFn, BookMe AI orchestrator — LangGraph fan-out after the decision subgraph.  Phase 6 (+7 more)

### Community 57 - "infrastructure/__init__.py"
Cohesion: 0.18
Nodes (8): LogRecord, Infrastructure layer — pure plumbing (config, logging, LLM clients, observabilit, Backward-compatible re-export — prefer ``from infrastructure.llm import ...``., _InterceptHandler, Centralised logging — powered by **loguru**.  Usage (any module)::      from log, Route stdlib ``logging`` records into loguru so third-party libs     (uvicorn, h, Configure loguru for the current process. Call once at each entry-point.      Ar, setup_logging()

### Community 58 - "_RecordingOrchestrator"
Cohesion: 0.18
Nodes (6): main(), Any, Minimal stand-in — records whether MCP path would run., _RecordingOrchestrator, Agent layer — LangGraph orchestration, routing, guardrail, and agent nodes.  Lay, AgentState — the shared state for the BookMe AI LangGraph.  Every node reads fro

### Community 59 - "_llm_content_to_str"
Cohesion: 0.50
Nodes (7): main(), test_gemini_signature_only_block(), test_mixed_text_and_signature_blocks(), test_openai_style_text_blocks(), test_plain_string(), _llm_content_to_str(), Normalize OpenAI/Gemini message content to plain text.

### Community 60 - "BookMeLogo.tsx"
Cohesion: 0.40
Nodes (4): DevGateProps, BookMeLogo(), BookMeLogoSize, sizeClasses

### Community 61 - "AgentResponse"
Cohesion: 0.50
Nodes (3): AgentResponse, One orchestrator turn — metadata for API / scripts., Standalone turn: no decision graph (supervisor runs router).

## Knowledge Gaps
- **223 isolated node(s):** `npx`, `name`, `private`, `version`, `type` (+218 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_orchestrator()` connect `orchestrator.py` to `http_client.py`, `BookMe AI — Development Roadmap & Phase Log`, `config.py`, `infrastructure/llm.py`, `flight_server.py`, `mcp_config.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `SessionStore` connect `infrastructure/llm.py` to `http_client.py`, `SessionStore`, `BookMe AI — Development Roadmap & Phase Log`, `build_agent_mcp`, `orchestrator.py`, `_RecordingOrchestrator`, `AgentResponse`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `AgentOrchestrator` connect `BookMe AI — Development Roadmap & Phase Log` to `observability.py`, `infrastructure/llm.py`, `build_agent_mcp`, `orchestrator.py`, `_RecordingOrchestrator`, `AgentResponse`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `AgentOrchestrator` (e.g. with `_RecordingOrchestrator` and `.__init__()`) actually correct?**
  _`AgentOrchestrator` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `AgentState` (e.g. with `_RecordingOrchestrator` and `AgentOrchestrator`) actually correct?**
  _`AgentState` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `SessionStore` (e.g. with `main()` and `_RecordingOrchestrator`) actually correct?**
  _`SessionStore` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `npx`, `name`, `private` to the rest of the system?**
  _223 weakly-connected nodes found - possible documentation gaps or missing edges._