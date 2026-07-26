# BookMe AI — Development Roadmap & Phase Log

**Project:** MCP-Based Multi-Agent Travel Planner (assessment: BookMe AI)  
**Baseline:** FastAPI + LangGraph + Gradio chat with hardcoded Convex HTTP tools  
**Target architecture:** Week 13 (Nawaloka) reference project — `src/` layout, MCP stdio servers, intent-routed orchestrator, streaming API, deployment  

**Last updated:** 2026-07-26  

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
Phase 4  Guardrail + router + decision graph         ⏳
Phase 5  Orchestrator (fan-out, merge, MCP adapters) ⏳
Phase 6  FastAPI backend (Clerk, streaming, sessions)⏳
Phase 7  Frontend (Clerk web app + chat UX)          ⏳
Phase 8  Deployment & documentation                  ⏳
Phase 9  Stretch (memory, LangFuse traces, CI/Docker)⏳
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
4. **In-memory `SessionStore` for MVP** — conversation scoped to `session_id`; no cross-day persistence until stretch memory work.
5. **Architecture north star:** Week 13 (guardrail ∥ router → orchestrator fan-out → merge → MCP tools).

**Acceptance:** `PYTHONPATH=src` imports; session isolation test; config dump runs.

---

## Phase 1b — LangFuse prompt management & observability ✅

**Commits:** `ea185b8`, `6eda5e5`, `fa4de57` merge path

**Goal:** Edit prompts in LangFuse without redeploying; tracing ready for later phases.

**Deliverables:**

| Area | Files |
|------|--------|
| Prompt registry | `src/agents/prompts/agent_prompts.py` — 9 LangFuse names + local fallbacks + `build_*()` helpers |
| Prompt fetch | `fetch_prompt`, `prefetch_prompts`, `langfuse_prompts_enabled()` in `observability.py` |
| Config | `observability.prompts_enabled`, `prompt_cache_ttl_seconds` in `params.yaml` |
| Env | `LANGFUSE_PROMPTS=true` documented in `.env.example` |

**Decisions:**

1. **Tracing and prompts are separate toggles** — `observability.enabled` (spans) vs `LANGFUSE_PROMPTS` / `prompts_enabled` (Prompt Management), matching Week 13.
2. **Local fallbacks always ship** — app works before prompts exist in LangFuse dashboard.
3. **LangFuse Mustache `{{var}}` in cloud; Python `{var}` in fallbacks** — compiled via `fetch_prompt(..., **vars)`.
4. **Instrument with `@observe` as we build** nodes (Phase 4–6); enable tracing for demo/viva screenshots.
5. **Prefetch prompts in API lifespan** (planned Phase 6) to avoid first-request latency.

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
| `src/mcp_servers/mcp_config.py` | `build_mcp_server_config()` for `MultiServerMCPClient` (stdio, `cwd=src/`) |
| `scripts/test_mcp_client.py` | Smoke: 6 tools, `list_hotels` / `list_flights` |
| `Makefile` | `test-mcp`, `inspect-hotel`, `inspect-flight` |

**MCP tool names:** `list_hotels`, `search_hotels`, `book_hotel`, `list_flights`, `search_flights`, `book_flight`.

**Decisions:**

1. **Transport: stdio subprocesses** (Week 13 default) — simple to run locally and defend in viva; HTTP MCP optional later for remote deploy.
2. **MCP servers are thin** — no HTTP, no routing; only `@mcp.tool()` → `dispatch`.
3. **Two servers** (hotel + flight) — clear domain split; could merge later without changing tool names.
4. **Decoupling proof:** change Convex URL in YAML → tools change; MCP tool schemas unchanged; Phase 5 adapters unchanged.

**Verified:** `make test-mcp` passes.

---

## Phase 4 — Guardrail + router + decision graph ⏳

**Goal:** Parallel **guardrail** (fail-open) and **router** (multi-intent JSON) → **decide** node (`out_of_scope` | `proceed`).

**Planned files:**

- `src/agents/guardrail.py`
- `src/agents/router.py` — `RouteDecision`, `MultiRouteDecision` (`hotel` | `flight` | `general_qa`)
- `src/agents/decision_state.py` — **Week 13** minimal `DecisionState` (`message`, `router_context`, …)
- `src/agents/decision_graph.py` — LangGraph on `DecisionState`: START → guardrail ∥ router → decide → END
- `src/agents/decision_bridge.py` — `map_decision_to_agent_state()` → orchestrator `AgentState`
- Prompts via `build_guardrail_system_prompt()`, `build_router_*()` from LangFuse/fallbacks
- `@observe` on guardrail and router LLM calls

**Architecture (Week 13):** two state schemas — classification subgraph vs orchestrator graph; chat API runs decision graph first, then maps into `AgentState` for Phase 5 fan-out.

**Design notes (discussion log):** [DECISION_GRAPH_NOTES.md](./DECISION_GRAPH_NOTES.md) — parallel guardrail/router behavior, bridge vs Week 13 `chat.py`, CAG/cache timing, OOS “Who is the president?” walkthrough, latency vs cost, viva diffs.

**Decisions (already agreed):**

1. Guardrail **fails open** on LLM errors (Week 13).
2. Router supports **multiple routes** in one user message (hotel + flight → two agents in Phase 5).
3. Do **not** fabricate booking fields; router sets null → agent asks follow-up.

**Acceptance:** Unit tests or script: out-of-scope message → `out_of_scope`; “hotels in X and flight A→B” → two route decisions.

---

## Phase 5 — Orchestrator (fan-out, merge, MCP adapters) ⏳

**Goal:** Assessment **E2** + complete **E1** wiring — agents call MCP, not `agents/tools.py`.

**Planned files:**

- `src/agents/orchestrator.py` — recall (session context) → supervisor → conditional fan-out → `merge_responses` → END
- Agent nodes: `hotel_agent`, `flight_agent`, `general_qa_agent`
- `_MCPHotelToolAdapter` / `_MCPFlightToolAdapter` — `.dispatch(action, params)` → MCP `ainvoke` (Week 13 `_MCPCRMToolAdapter` pattern)
- `build_agent_mcp()` — `MultiServerMCPClient` + adapters

**Decisions (planned):**

1. **Single-route merge:** pass-through (no extra LLM). **Multi-route:** one synthesis LLM call (`build_merge_system_prompt()`).
2. **`agent_outputs` reducer** already in `AgentState` (Phase 1).
3. MCP tool failures surface as text in `tool_output`; graph continues (E3).

**Acceptance:** CLI or script: multi-intent query returns combined answer; killing one MCP server degrades gracefully for that domain only.

---

## Phase 6 — FastAPI backend ⏳

**Goal:** Efficient async API, streaming, session identity, LangFuse prefetch.

**Planned:**

- `src/api/main.py` — lifespan: build orchestrator, MCP client, warmup router LLM, `prefetch_prompts(ALL_LANGFUSE_PROMPT_NAMES)`
- `src/api/deps.py` — Clerk `authenticate_request` → `user_id` from JWT `sub`
- `src/api/routers/chat.py` — `POST /chat`, `POST /chat/stream` (SSE + `emit` / activity labels)
- `src/api/event_labels.py` — “Searching hotels…”, etc.
- **Session model:** mint `session_id` per conversation (UUID); memory keyed by **`(user_id, session_id)`** (extend `SessionStore` or composite key)
- Remove dependency on root `main.py` for production path

**Decisions (already agreed):**

1. **Clerk** for auth; **`user_id` from verified token**, never trust client body alone.
2. **`session_id` ≠ Clerk `sid`** — chat thread IDs are app-owned UUIDs (ChatGPT-style threads planned).
3. **Per-session ST memory** in Phase 6; **cross-day LT memory** = stretch (Redis/Supabase/LangGraph store — documented, not required for core).

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
| Tracing | LangFuse optional | `@observe` built-in; enable for demo |
| Chat memory | In-memory `SessionStore` | Core deliverable; durable memory = stretch |
| Auth (planned) | Clerk + composite session key | Stable `user_id`; app-owned `session_id` |
| Identity vs thread | Do not use Clerk `sid` as chat `session_id` | Auth lifecycle ≠ conversation lifecycle |
| Legacy root code | Keep until Phase 6 | Reference + fallback during rebuild |
| Python version | 3.11+ | MCP package requirement |

---

## Repository map (current `src/`)

```text
src/
  infrastructure/     config, llm, log, observability, http_client, session_store
  agents/
    state.py              AgentState (orchestrator)
    decision_state.py     DecisionState (subgraph)
    decision_graph.py
    decision_bridge.py
    guardrail.py
    router.py
    prompts/              LangFuse-backed builders
    tools/                HotelTool, FlightTool
  mcp_servers/        hotel_server, flight_server, mcp_config
  api/                (Phase 6)
scripts/
  test_mcp_client.py
  test_decision_graph.py
config/
  models.yaml, params.yaml
docs/
  DEVELOPMENT_ROADMAP.md   ← phase log
  DECISION_GRAPH_NOTES.md  ← architecture & Week 13 comparison notes
```

**Legacy (baseline, root):** `main.py`, `frontend.py`, `agents/*` — to be retired when `src/api` is live.

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

# MCP (Phase 3)
make test-mcp
make inspect-hotel

# Decision graph (Phase 4)
make test-decision

# Later
make run-api          # Phase 6
```

---

## Assessment mapping (SRS)

| Requirement | Phase | Status |
|-------------|-------|--------|
| E1 MCP servers | 2–3, wired in 5 | ✅ servers; ⏳ agent wiring |
| E2 Intent routing | 4–5 | ⏳ |
| E3 Graceful failures | 2–3 (tools), 5 (agents) | ✅ partial |
| FE streaming + activity | 6–7 | ⏳ |
| Deploy + docs | 8 | ⏳ |
| Git branches / PRs | Ongoing | ✅ #1 merged; MCP on branch |

---

## Next recommended step

**Phase 4** on branch `feat/decision-graph`: implement guardrail, router, and decision LangGraph; use existing prompts and `@observe`.

When Phase 4 starts, update this file’s status table and add a “Completed” subsection with commit SHAs.
