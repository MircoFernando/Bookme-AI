# BookMe AI — Development Roadmap & Phase Log

**Project:** MCP-Based Multi-Agent Travel Planner (assessment: BookMe AI)  
**Baseline:** FastAPI + LangGraph + Gradio chat with hardcoded Convex HTTP tools  
**Target architecture:** Week 13 (Nawaloka) reference project — `src/` layout, MCP stdio servers, intent-routed orchestrator, streaming API, deployment  

**Last updated:** 2026-07-27  

---

## How to read this document

| Status | Meaning |
|--------|---------|
| ✅ **Completed** | Merged or done on branch; listed deliverables exist in repo |
| 🔄 **In progress** | Started but not fully integrated (e.g. not yet in production API) |
| ⏳ **Planned** | Not started; scope defined below |

Each completed phase includes **what was done** and **decisions** (for viva / PR defence).

---

## High-level phase map

```text
Phase 0  Baseline (starter repo)                    ✅
Phase 1  Infrastructure & project skeleton         ✅
Phase 1b LangFuse prompts + observability plumbing   ✅
Phase 2  Travel tool layer (Convex HTTP)             ✅
Phase 3  MCP servers + client config                 ✅
Phase 3b Web search (Tavily) tool + MCP server         ✅
Phase 4  Guardrail + router + decision graph         ✅
Phase 5  Orchestrator (fan-out, merge, MCP adapters) ✅
Phase 6  FastAPI backend (streaming, sessions)       🔄
Phase 7  Frontend (Clerk web app + chat UX)          ⏳
Phase 8  Deployment & documentation                  ⏳
Phase 9  Stretch (LT memory, CI/Docker)              ⏳
```

---

## Phase 0 — Baseline starter ✅

**Goal:** Working demo from course/starter code (not the final deliverable).

**What existed:**

- Root-level `main.py`, `frontend.py`, `agents/{graph,nodes,tools,prompts,llm,entity}.py`
- Intent-ish routing: router node → hotel / flight / unknown
- Direct `requests` to Convex: `standing-fish-574.convex.site` (hotels/flights)
- Global in-memory `conversation_history_messages` (shared across all users)
- Gradio frontend, blocking HTTP to `/chat`

**Decision:** Keep root baseline **unchanged** until Phase 6; new work lives under `src/` to avoid breaking the starter while rebuilding.

---

## Phase 1 — Infrastructure & project skeleton ✅

**Branch / PR:** `feat/infra-restructure` → merged (#1)  
**Commits:** `15f0309` (infra scaffold)

**Goal:** Week-13-style layout and shared plumbing for agents, API, and MCP.

**Deliverables:**

| Area | Files |
|------|--------|
| Layout | `src/infrastructure/`, `src/agents/`, `src/mcp_servers/` (stubs) |
| Config | `config/models.yaml`, `config/params.yaml`, `infrastructure/config.py` |
| LLM | `infrastructure/llm.py` — router / guardrail / extractor / chat factories; `max_retries`; optional cross-provider `with_fallbacks` on chat LLM |
| Logging | `infrastructure/log.py` — loguru → **stderr** (stdio-safe for MCP subprocesses) |
| Observability (tracing) | `infrastructure/observability.py` — `@observe` no-op when disabled |
| Session memory | `infrastructure/session_store.py` — per-`session_id` thread-safe history (replaces global list bug) |
| Agent state | `agents/state.py` — `AgentState` with `operator.add` on `agent_outputs` for parallel fan-in |
| Tooling | `.env.example`, `.gitignore`, `Makefile`, `requirements.txt` |

**Decisions:**

1. **Provider-default OpenAI** (`gpt-4o-mini`) so the app runs with only `OPENAI_API_KEY`; Groq/OpenRouter optional via YAML + env for router speed and LLM fallbacks.
2. **YAML for behaviour, `.env` for secrets** — no API keys in repo.
3. **Python 3.11+ required** (`mcp`, `langchain-mcp-adapters`); project uses `.venv` with 3.11 (system Python 3.9 is insufficient).
4. **In-memory `SessionStore` for MVP** — keyed by **`(user_id, session_id)`**; window from `config/params.yaml` (`session.max_turns`, `session.history_window`).
5. **Architecture north star:** Week 13 (guardrail ∥ router → orchestrator fan-out → merge → MCP tools).

**Acceptance:** `PYTHONPATH=src` imports; session isolation test; config dump runs.

---

## Phase 1b — LangFuse prompt management & observability ✅

**Commits:** `ea185b8`, `6eda5e5`, `fa4de57` merge path

**Goal:** Edit prompts in LangFuse without redeploying; tracing ready for later phases.

**Deliverables:**

| Area | Files |
|------|--------|
| Prompt registry | `src/agents/prompts/agent_prompts.py` — LangFuse names + local fallbacks (incl. `web_search_agent_system`) |
| Prompt fetch | `fetch_prompt`, `prefetch_prompts`, `langfuse_prompts_enabled()` in `observability.py` |
| Config | `observability.prompts_enabled`, `prompt_cache_ttl_seconds` in `params.yaml` |
| Env | `LANGFUSE_PROMPTS=true` documented in `.env.example` |

**Decisions:**

1. **Tracing and prompts are separate toggles** — `observability.enabled` (spans) vs `LANGFUSE_PROMPTS` / `prompts_enabled` (Prompt Management), matching Week 13.
2. **Local fallbacks always ship** — app works before prompts exist in LangFuse dashboard.
3. **LangFuse Mustache `{{var}}` in cloud; Python `{var}` in fallbacks** — compiled via `fetch_prompt(..., **vars)`.
4. **Instrument with `@observe` as we build** nodes (Phase 4–6); enable tracing for demo/viva screenshots.
5. **Prefetch prompts in API lifespan** — `api/main.py` calls `prefetch_prompts(ALL_LANGFUSE_PROMPT_NAMES)` at startup.

**Prompt names to create in LangFuse:** see `LANGFUSE_PROMPT_NAMES` in `agent_prompts.py` (prefix `bookme-ai-*`).

---

## Phase 2 — Travel tool layer (Convex HTTP) ✅

**Commits:** `6eda5e5` (http_client), `e9a082a` (tools)

**Goal:** Week-13-style `HotelTool` / `FlightTool` with `dispatch(action, params)`; no silent failures.

**Deliverables:**

| File | Role |
|------|------|
| `src/infrastructure/http_client.py` | Shared GET/POST, retries (`tenacity`), envelope `{ok, data}` / `{ok, error, code}` |
| `src/agents/tools/hotel_tool.py` | `list_hotels`, `search_hotels`, `book_hotel` |
| `src/agents/tools/flight_tool.py` | `list_flights`, `search_flights`, `book_flight` |
| `src/agents/tools/__init__.py` | Exports |

**Decisions:**

1. **`http_client.py` is BookMe AI-specific**, not copied from Week 13 (Nawaloka uses DB/RAG per tool). Justified because **both** hotel and flight share the same Convex REST pattern; avoids duplicating retry logic.
2. **`dispatch` returns JSON strings** — one contract for MCP tools and future agent adapters.
3. **Param aliasing** in `_clean_params` (`check_in` ↔ `checkIn`, `flight_date` ↔ `date`) so router output does not have to match Convex field names exactly.
4. **Booking validation** returns `"code": "VALIDATION"` instead of crashing or inventing emails (fixes baseline prompt risk).
5. **Convex URLs** in `config/params.yaml` (`services.hotels_base_url`, `flights_base_url`) — swap provider without touching MCP or agent nodes.

**Verified:** Live API — ~178 hotels, ~270 flights on list actions.

---

## Phase 3 — MCP servers & client config ✅

**Commit:** `b75f19e`

**Goal:** Assessment **E1** — agents reach external services only through MCP; decoupled from Convex HTTP in nodes.

**Deliverables:**

| File | Role |
|------|------|
| `src/mcp_servers/hotel_server.py` | FastMCP `bookme-ai-hotels` — 3 tools → `HotelTool.dispatch` |
| `src/mcp_servers/flight_server.py` | FastMCP `bookme-ai-flights` — 3 tools → `FlightTool.dispatch` |
| `src/mcp_servers/web_search_server.py` | FastMCP `bookme-ai-web-search` — `search_web` → `WebSearchTool` (Tavily) |
| `src/mcp_servers/mcp_config.py` | `build_mcp_server_config()` for `MultiServerMCPClient` (stdio, `cwd=src/`) |
| `scripts/test_mcp_client.py` | Smoke: **7** tools |
| `Makefile` | `test-mcp`, `inspect-hotel`, `inspect-flight`, `inspect-web-search` |

**MCP tool names:** `list_hotels`, `search_hotels`, `book_hotel`, `list_flights`, `search_flights`, `book_flight`, **`search_web`**.

**Decisions:**

1. **Transport: stdio subprocesses** (Week 13 default) — simple to run locally and defend in viva; HTTP MCP optional later for remote deploy.
2. **MCP servers are thin** — no HTTP, no routing; only `@mcp.tool()` → `dispatch`.
3. **Three servers** (hotel + flight + web search) — domain split; orchestrator uses `build_agent_mcp()`.
4. **Decoupling proof:** change Convex URL or Tavily env → tools change; MCP tool schemas unchanged; orchestrator adapters unchanged.

**Verified:** `make test-mcp` passes (7 tools).

---

## Phase 3b — Web search (Tavily) ✅

**Goal:** Tourism / destination Q&A via MCP, routed as `web_search` agent.

**Deliverables:**

| File | Role |
|------|------|
| `src/agents/tools/web_search_tool.py` | Tavily API, `dispatch("search", {query})` |
| `src/mcp_servers/web_search_server.py` | MCP wrapper |
| Router + prompts | `web_search` route; `build_web_search_agent_system_prompt()` |
| `scripts/test_orchestrator_web_search.py` | `make test-orchestrator-web-search` |

**Env:** `TAVILY_API_KEY` in `.env`; Tavily settings in `config/params.yaml` (`tavily.*`).

---

## Phase 4 — Guardrail + router + decision graph ✅

**Goal:** Parallel **guardrail** (fail-open) and **router** (multi-intent JSON) → **decide** → bridge to orchestrator.

**Deliverables:**

- `src/agents/guardrail.py` — scope classifier; receives **`router_context`** (same ST memory as router); LangFuse system prompt via `build_guardrail_system_prompt()`
- `src/agents/router.py` — routes: `hotel` \| `flight` \| `general_qa` \| **`web_search`**
- `src/agents/decision_state.py`, `decision_graph.py`, `decision_bridge.py`
- **`decide_node`:** OOS from guardrail **unless** router primary is `hotel` \| `flight` \| `web_search` (avoids false blocks on tourism/food queries)
- `scripts/test_decision_graph.py` — `make test-decision`

**Design notes:** [DECISION_GRAPH_NOTES.md](./DECISION_GRAPH_NOTES.md)

**Acceptance (verified via `make test-decision`):**

1. Off-topic trivia → `verdict=out_of_scope`
2. Hotel + flight in one message → `proceed`, ≥2 routes
3. Router: tourism → `web_search`; chitchat → `general_qa`

---

## Phase 5 — Orchestrator (fan-out, merge, MCP adapters) ✅

**Goal:** Assessment **E1/E2** — agents call MCP, not root `agents/tools.py`.

**Deliverables:**

- `src/agents/orchestrator.py` — recall → supervisor → parallel **`hotel_agent` \| `flight_agent` \| `general_qa_agent` \| `web_search_agent`** → merge → save_memory
- `_MCP*ToolAdapter` + `build_agent_mcp()` — `MultiServerMCPClient`, 7 tools
- `src/agents/chat_pipeline.py` — `run_chat_turn()`: decision graph → orchestrator or OOS; loads/saves `SessionStore`
- Scripts: `make test-orchestrator`, `make test-chat-pipeline` (mock orch), `make test-session-store`

**Decisions:**

1. **Single-route merge:** pass-through; **multi-route:** merge LLM (`build_merge_system_prompt()`).
2. **`agent_outputs` reducer** on `AgentState`.
3. MCP failures → JSON error in `tool_output`; graph continues (E3).

---

## Phase 6 — FastAPI backend 🔄

**Goal:** Async API, SSE streaming, session identity, LangFuse warmup.

**Completed:**

| Area | Files |
|------|--------|
| App | `src/api/main.py` — lifespan: `SessionStore`, `build_decision_graph()`, `await build_agent_mcp()`, prompt prefetch, router warmup |
| Chat | `src/api/routers/chat.py` — `POST /chat`, `POST /chat/stream`, `POST /chat/reset` |
| Health | `src/api/routers/health.py` — `/health`, `/ready`, `/config` |
| Schemas / labels | `schemas.py`, `event_labels.py`, `utils.chat_result_to_response` |
| Auth (dev) | `deps.py` — `AUTH_DISABLED=1` + `DEV_USER_ID`; Clerk path when disabled flag off |
| Observability | LangFuse SDK **v4**: `langfuse_turn_attributes` + `update_current_span` (no `update_current_trace`) |

**Remaining for Phase 6 “done”:**

- Production **Clerk** enabled (`AUTH_DISABLED=0`, `clerk-backend-api`)
- Optional: pytest for HTTP layer; log `memory_context` on trace metadata for debugging

**Run:** `make run-api` (uses `.venv/bin/uvicorn`).

**Session memory:** `config/params.yaml` → `session.max_turns` (storage cap), `session.history_window` (pairs injected into prompts each turn). In-memory only until Phase 9 Redis/LT memory.

---

## Phase 7 — Frontend (Clerk web app + chat) ⏳

**Goal:** Sign-in required; streaming chat; travel-themed UX (assessment FE core).

**Planned:**

- Web app (not only Gradio) with Clerk session; attach Bearer token to API
- Consume `/chat/stream` — tokens + activity stages
- Stable `session_id` per thread (server-created or client UUID registered on first message)
- Friendly errors when MCP/Convex fails (no stack traces)

**Decision:** Gradio may remain for quick demos; **primary submission UI** = Clerk web app aligned with your product plan.

---

## Phase 8 — Deployment & documentation ⏳

**Goal:** Public backend + frontend URLs; README, MCP guide, env handling.

**Planned:**

- Docker / compose (stretch but recommended)
- Deploy API (Render/Fly/Railway/HF Docker Space) + frontend (Vercel/HF)
- `docs/MCP_SETUP.md` (Inspector, `make test-mcp`, architecture diagram)
- Updated root `README.md` — setup, env, links to deployed apps
- PR history visible on GitHub (incremental phases)

---

## Phase 9 — Stretch (optional, for top marks) ⏳

| Item | Notes |
|------|--------|
| LangFuse tracing enabled | Screenshots of guardrail → router → tool spans |
| Combined itinerary node | Richer multi-step hotel+flight plan |
| Persistent memory | Redis ST and/or semantic LT by `user_id` |
| Docker + CI | Reproducible builds, pytest on push |
| Result cards in UI | Structured hotel/flight presentation |

---

## Decision log (consolidated)

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Reference architecture | Week 13 Nawaloka | Production patterns: MCP, orchestrator, SSE, lifespan |
| Repo layout | `src/` package | Separates new system from root baseline |
| MCP transport | stdio | Matches course reference; easy local + viva |
| External APIs | Convex via tools only | MCP → tools → http_client → Convex |
| HTTP layer | Shared `http_client.py` | DRY for hotel+flight; explicit errors vs baseline `None` |
| LLM provider | OpenAI default | Simplest setup; YAML switch to Groq/OpenRouter |
| Prompts | LangFuse + local fallback | Edit without redeploy; works offline |
| Tracing | LangFuse SDK v4 (`@observe`, `propagate_attributes`, `update_current_span`) |
| Chat memory | In-memory `SessionStore`; `(user_id, session_id)`; YAML window |
| ST vs LangGraph checkpoint | Custom ST store (Week 13 style); no checkpointer in MVP |
| Auth | Clerk in prod; `AUTH_DISABLED=1` for local API | JWT `sub` → `user_id`; app-owned `session_id` |
| Legacy root code | Kept for reference; **`make run-api`** is production path |
| Python version | 3.11+ | MCP package requirement |

---

## Repository map (current `src/`)

```text
src/
  api/                  main, deps, routers/chat|health, schemas, event_labels
  infrastructure/       config, llm, log, observability, http_client, session_store
  agents/
    chat_pipeline.py    run_chat_turn (API hot path)
    orchestrator.py     MCP orchestrator + build_agent_mcp
    state.py            AgentState
    decision_*.py       Decision subgraph + bridge
    guardrail.py, router.py
    prompts/            LangFuse-backed builders
    tools/              HotelTool, FlightTool, WebSearchTool
  mcp_servers/          hotel, flight, web_search, mcp_config
scripts/
  test_mcp_client.py, test_decision_graph.py, test_orchestrator*.py
  test_chat_pipeline.py, test_session_store.py
config/
  models.yaml, params.yaml
docs/
  DEVELOPMENT_ROADMAP.md
  DECISION_GRAPH_NOTES.md
```

**Legacy (root):** `main.py`, `frontend.py`, `agents/*` — starter demo only.

---

## Commands cheat sheet

```bash
# Setup
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add OPENAI_API_KEY, optional LANGFUSE_*

# Config
make config
make check-config

# MCP (Phase 3–3b)
make test-mcp
make inspect-web-search

# Agents
make test-decision
make test-orchestrator
make test-orchestrator-web-search
make test-session-store
make test-chat-pipeline

# API
make run-api
```

---

## Assessment mapping (SRS)

| Requirement | Phase | Status |
|-------------|-------|--------|
| E1 MCP servers | 2–3b, wired in 5 | ✅ |
| E2 Intent routing | 4–5 | ✅ |
| E3 Graceful failures | 2–3 (tools), 5 (agents) | ✅ |
| FE streaming + activity | 6 (API SSE), 7 (UI) | 🔄 API ✅; UI ⏳ |
| Deploy + docs | 8 | ⏳ |
| Git branches / PRs | Ongoing | ✅ #1 merged; feature work on branch |

---

## Next recommended step

**Phase 7** — Clerk web app consuming `POST /chat/stream`, stable `session_id` per thread.

Then **Phase 8** — deploy API + UI, `docs/MCP_SETUP.md`, refresh deployment URLs in README.
