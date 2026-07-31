# Graph Report - Bookme AI  (2026-07-31)

## Corpus Check
- 100 files · ~212,668 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 921 nodes · 1526 edges · 55 communities (44 shown, 11 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 131 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5b159fb7`
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
- shadcn
- vite-env.d.ts
- vite.config.ts
- react
- postcss
- @types/react-dom

## God Nodes (most connected - your core abstractions)
1. `AgentOrchestrator` - 33 edges
2. `AgentState` - 31 edges
3. `QueryRouter` - 23 edges
4. `SessionStore` - 21 edges
5. `BookMe AI — Development Roadmap & Phase Log` - 21 edges
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
- `main()` --calls--> `run_chat_turn()`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/chat_pipeline.py
- `main()` --calls--> `build_decision_graph()`  [INFERRED]
  scripts/test_chat_pipeline.py → src/agents/decision_graph.py
- `_router_primary_route()` --calls--> `get_query_router()`  [INFERRED]
  scripts/test_decision_graph.py → src/agents/router.py

## Import Cycles
- None detected.

## Communities (55 total, 11 thin omitted)

### Community 0 - "decision_graph.py"
Cohesion: 0.06
Nodes (37): AnyMessage, GuardrailVerdict, main(), _router_primary_route(), _run(), main(), map_decision_to_agent_state(), Bridge decision subgraph output → orchestrator ``AgentState``.  The chat/API lay (+29 more)

### Community 1 - "router.py"
Cohesion: 0.12
Nodes (19): _fallback_multi(), get_query_router(), _last_user_text(), MultiRouteDecision, _normalize_action(), _normalize_params(), Any, QueryRouter (+11 more)

### Community 2 - "nodes.py"
Cohesion: 0.09
Nodes (40): GraphState, TypedDict, build_graph(), flight_node(), _format_flight(), _format_hotel(), generate_response(), hotel_node() (+32 more)

### Community 3 - "observability.py"
Cohesion: 0.08
Nodes (39): RouteLiteral, ChatResult, _noop_emit(), Any, EmitFn, Single async entry for one chat turn: decision graph → orchestrator (or OOS shor, One user turn — maps cleanly to ``api.schemas.ChatResponse``., Run decision graph, then orchestrator unless ``verdict == out_of_scope``.      L (+31 more)

### Community 4 - "http_client.py"
Cohesion: 0.31
Nodes (9): book_hotel(), _get_hotel(), list_hotels(), tool, Hotel MCP server — exposes HotelTool over the Model Context Protocol.  Thin tran, List all available hotels from the travel service., Search hotels by city and optional check-in/check-out dates (YYYY-MM-DD).      A, Book a hotel room.      Args:         hotel_id: Hotel identifier from search/lis (+1 more)

### Community 5 - "SessionStore"
Cohesion: 0.06
Nodes (51): ConfigResponse, HealthResponse, ReadinessResponse, _clerk_user_id(), get_decision_graph(), get_orchestrator(), get_session_store(), is_auth_disabled() (+43 more)

### Community 6 - "Decision graph & routing — architecture notes"
Cohesion: 0.08
Nodes (26): Assessment mapping (SRS), BookMe AI — Development Roadmap & Phase Log, Commands cheat sheet, Decision log (consolidated), High-level phase map, How to read this document, Next recommended step, Phase 0 — Baseline starter ✅ (+18 more)

### Community 7 - "BookMe AI — Development Roadmap & Phase Log"
Cohesion: 0.06
Nodes (50): main(), test_gemini_signature_only_block(), test_mixed_text_and_signature_blocks(), test_openai_style_text_blocks(), test_plain_string(), main(), Agent layer — LangGraph orchestration, routing, guardrail, and agent nodes.  Lay, AgentOrchestrator (+42 more)

### Community 8 - "config.py"
Cohesion: 0.05
Nodes (46): main(), _text(), _compact_results(), _dumps(), Any, Web search tool — Tavily Search API (travel / tourism Q&A).  Business logic live, Sync entry for scripts/tests., Tavily-backed web search for destination and tourism questions. (+38 more)

### Community 9 - "infrastructure/llm.py"
Cohesion: 0.06
Nodes (26): LogRecord, main(), Any, Minimal stand-in — records whether MCP path would run., _RecordingOrchestrator, main(), Infrastructure layer — pure plumbing (config, logging, LLM clients, observabilit, Backward-compatible re-export — prefer ``from infrastructure.llm import ...``. (+18 more)

### Community 11 - "Setup"
Cohesion: 0.06
Nodes (34): 1. One-time install, 1. Root `.env`, 2. Environment files, 2. Start stack, 3. Auth mode (pick one), 4. Run (two terminals), 5. Smoke test, 🤖 Agent Pipeline (+26 more)

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
Cohesion: 0.07
Nodes (27): 1. Build your hostname from the droplet IP, 2.1 Install Docker, 2.2 Clone repo (path must match the workflow), 2.3 Configure environment, 2.4 Pull and start API (first deploy), 2.5 HTTPS (before browsers / Vercel), 2. Caddy on the same droplet (second block), 3. Same droplet checklist (no domain) (+19 more)

### Community 21 - "SessionStore"
Cohesion: 0.18
Nodes (17): build_extractor_system_prompt(), build_flight_agent_system_prompt(), build_general_qa_system_prompt(), build_guardrail_system_prompt(), build_hotel_agent_system_prompt(), build_merge_system_prompt(), build_router_hard_rules_prompt(), build_router_prompt() (+9 more)

### Community 23 - "flight_server.py"
Cohesion: 0.08
Nodes (25): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleDetection (+17 more)

### Community 24 - "types.ts"
Cohesion: 0.10
Nodes (23): BASE, systemApi, Props, STATUS_META, StatusBar(), ChatRequest, ChatResponse, ConfigResponse (+15 more)

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
Cohesion: 0.17
Nodes (10): setAuthTokenProvider(), App(), AuthMode, InputBox(), Props, useHealth(), AppShell(), AuthMode (+2 more)

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
Cohesion: 0.31
Nodes (7): authHeaders(), AuthTokenProvider, isApiAuthDisabled(), chatPayload(), request(), AuthGate(), DevGateProps

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
Nodes (7): ApiError, chatApi, formatStageDetail(), friendlyError(), stageLabelFromId(), useChatStream(), UseChatStreamArgs

### Community 42 - "4. Parallel guardrail + router — runtime behavior"
Cohesion: 0.40
Nodes (5): 4.1 Both branches always start, 4.2 Fan-in before `decide`, 4.3 Off-topic example: “Who is the president?”, 4.4 Two meanings of “instant return”, 4. Parallel guardrail + router — runtime behavior

### Community 43 - "package.json"
Cohesion: 0.33
Nodes (5): description, name, private, type, version

### Community 44 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, preview

## Knowledge Gaps
- **215 isolated node(s):** `npx`, `name`, `private`, `version`, `type` (+210 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_orchestrator()` connect `BookMe AI — Development Roadmap & Phase Log` to `config.py`, `infrastructure/llm.py`, `flight_server.py`, `mcp_config.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `AgentOrchestrator` connect `BookMe AI — Development Roadmap & Phase Log` to `infrastructure/llm.py`, `observability.py`, `router.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `SessionStore` connect `infrastructure/llm.py` to `SessionStore`, `BookMe AI — Development Roadmap & Phase Log`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `AgentOrchestrator` (e.g. with `_RecordingOrchestrator` and `.__init__()`) actually correct?**
  _`AgentOrchestrator` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `AgentState` (e.g. with `_RecordingOrchestrator` and `AgentOrchestrator`) actually correct?**
  _`AgentState` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `QueryRouter` (e.g. with `AgentOrchestrator` and `AgentResponse`) actually correct?**
  _`QueryRouter` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `SessionStore` (e.g. with `main()` and `_RecordingOrchestrator`) actually correct?**
  _`SessionStore` has 12 INFERRED edges - model-reasoned connections that need verification._