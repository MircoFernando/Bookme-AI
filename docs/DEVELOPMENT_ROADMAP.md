# BookMe AI — Development Roadmap & Phase Log

**Project:** MCP-Based Multi-Agent Travel Planner (assessment: BookMe AI)  
**Baseline:** FastAPI + LangGraph + Gradio chat with hardcoded Convex HTTP tools  
**Target architecture:** `src/` layout, MCP stdio servers, intent-routed orchestrator, streaming API, deployment  

**Last updated:** 2026-07-28  

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
Phase 6  FastAPI backend (streaming, sessions)       ✅
Phase 7  Frontend (Clerk web app + chat UX)          🔄
Phase 8  Deployment & documentation                  🔄
Phase 9  Stretch (LT memory, CI/Docker, cards)       🔄
Phase 10 Final delivery — polish, deploy, articles   ⏳
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

**Goal:** Production-style `src/` layout and shared plumbing for agents, API, and MCP.

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
5. **Architecture north star:** guardrail ∥ router → orchestrator fan-out → merge → MCP tools.

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

1. **Tracing and prompts are separate toggles** — `observability.enabled` (spans) vs `LANGFUSE_PROMPTS` / `prompts_enabled` (Prompt Management).
2. **Local fallbacks always ship** — app works before prompts exist in LangFuse dashboard.
3. **LangFuse Mustache `{{var}}` in cloud; Python `{var}` in fallbacks** — compiled via `fetch_prompt(..., **vars)`.
4. **Instrument with `@observe` as we build** nodes (Phase 4–6); enable tracing for demo/viva screenshots.
5. **Prefetch prompts in API lifespan** — `api/main.py` calls `prefetch_prompts(ALL_LANGFUSE_PROMPT_NAMES)` at startup.

**Prompt names to create in LangFuse:** see `LANGFUSE_PROMPT_NAMES` in `agent_prompts.py` (prefix `bookme-ai-*`).

---

## Phase 2 — Travel tool layer (Convex HTTP) ✅

**Commits:** `6eda5e5` (http_client), `e9a082a` (tools)

**Goal:** `HotelTool` / `FlightTool` with `dispatch(action, params)`; no silent failures.

**Deliverables:**

| File | Role |
|------|------|
| `src/infrastructure/http_client.py` | Shared GET/POST, retries (`tenacity`), envelope `{ok, data}` / `{ok, error, code}` |
| `src/agents/tools/hotel_tool.py` | `list_hotels`, `search_hotels`, `book_hotel` |
| `src/agents/tools/flight_tool.py` | `list_flights`, `search_flights`, `book_flight` |
| `src/agents/tools/__init__.py` | Exports |

**Decisions:**

1. **`http_client.py` is shared by hotel and flight tools** — both use the same Convex REST pattern; avoids duplicating retry logic.
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

1. **Transport: stdio subprocesses** — simple to run locally and defend in viva; HTTP MCP optional later for remote deploy.
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

## Phase 6 — FastAPI backend ✅

**Goal:** Async API, SSE streaming, session identity, LangFuse warmup.

**Deliverables:**

| Area | Files |
|------|--------|
| App | `src/api/main.py` — lifespan: `SessionStore`, `build_decision_graph()`, `await build_agent_mcp()`, prompt prefetch, router warmup |
| Chat | `src/api/routers/chat.py` — `POST /chat`, `POST /chat/stream`, `POST /chat/reset` |
| Health | `src/api/routers/health.py` — `/health`, `/ready`, `/config` |
| Schemas / labels | `schemas.py`, `event_labels.py`, `utils.chat_result_to_response` |
| Auth | `deps.py` — `AUTH_DISABLED=1` + `DEV_USER_ID` for local; Clerk JWT when `AUTH_DISABLED=0` |
| Observability | LangFuse SDK **v4**: `langfuse_turn_attributes` + `update_current_span` |
| Pipeline | `agents/chat_pipeline.py` — decision graph → orchestrator; SSE `emit` for stages/tools |

**SSE behaviour:** `/chat/stream` emits **stage/tool progress**, then **LLM token deltas** (`token_start` / `token_delta` / `token_end`) during the user-visible synthesis step, then **`final`** with metadata. See [STREAMING.md](./STREAMING.md).

**Token streaming rules:**

- Single route → stream from the active agent node (`_generate_agent_response`).
- Multi route → agents synthesize with `ainvoke`; only **merge** streams tokens.
- Toggle: `config/params.yaml` → `chat.stream_tokens` (`CHAT_STREAM_TOKENS`).

**Production hardening (defer to Phase 8/10):**

- Clerk enabled end-to-end on deployed URLs (`CLERK_AUTHORIZED_PARTIES`, `CORS_ORIGINS`)
- Optional: pytest for HTTP layer; redact generic 500 messages in stream errors

**Run:** `make run-api` (uses `.venv/bin/uvicorn`).

**Session memory:** `config/params.yaml` → `session.max_turns`, `session.history_window`. In-memory until Phase 9 Redis/LT memory.

---

## Phase 7 — Frontend (Clerk web app + chat) 🔄

**Goal:** Sign-in required; streaming chat; travel-themed UX (assessment FE core).

**Completed:**

| Area | Location |
|------|----------|
| Chat UI | `frontend/` — Vite + React + Tailwind |
| SSE chat | `useChatStream` → `POST /chat/stream` + chain-of-thought |
| Sessions | `useSessions` — localStorage threads + API `(user_id, session_id)` memory |
| Clerk | `@clerk/clerk-react`; Bearer via `getToken()` when `VITE_AUTH_DISABLED=false` |
| Dev bypass | `VITE_AUTH_DISABLED=true` + API `AUTH_DISABLED=1` |

**Run:** `make run-ui` (port 5173, proxies `/api` → backend).

**Remaining (Phase 7 → folded into Phase 10 UI polish):**

- Production Clerk smoke test against live API
- Optional: hotel/flight **result cards** (stretch)
- Optional: LLM token streaming on final answer (SRS wording) — **done** ([STREAMING.md](./STREAMING.md))
- Legacy **`frontend.py` (Gradio)** — minimal blocking client; **not** the submitted UI (`frontend/` React app). Upgrade or document as deprecated in README.

---

## Phase 8 — Deployment & documentation 🔄

**Goal:** Public backend + frontend URLs; README, MCP guide, env handling; assessment submission links.

**Completed / in repo:**

| Area | Location |
|------|----------|
| API Docker image | `docker/api/Dockerfile` |
| Prod compose (API only) | `compose.prod.api.yaml` — pull `bookme-ai-api:latest`, bind `127.0.0.1:8000` |
| Local compose | `docker-compose.yml` |
| CI deploy | `.github/workflows/docker-publish.yml` — build/push Hub → SSH deploy to droplet |
| DO runbooks | [DEPLOY_DO_API.md](./DEPLOY_DO_API.md), [DEPLOY_DO_VERCEL.md](./DEPLOY_DO_VERCEL.md) |

**Target topology (single droplet):**

- **One DigitalOcean droplet** runs BookMe API via Docker Compose (same pattern as booking-platform-api on the same VM if desired).
- **Caddy** (or existing reverse proxy) terminates HTTPS → `127.0.0.1:8000`.
- **Frontend** on **Vercel** (separate host); `VITE_API_URL` points at the droplet HTTPS URL.
- MCP stdio servers spawn **inside** the API container/process at lifespan — no separate MCP VM required.

**Remaining:**

- [ ] Droplet `.env` populated (secrets only on server); first successful `docker compose -f compose.prod.api.yaml pull && up -d`
- [ ] `/ready` returns MCP tools OK from production
- [ ] Vercel project wired; CORS + Clerk authorized parties include production origins
- [ ] **Live URLs** at top of root `README.md` (API + UI) for submission
- [ ] `docs/MCP_SETUP.md` — Inspector, `make test-mcp`, stdio architecture, env vars
- [ ] Short **user guide** (screenshots): chat, chain-of-thought, book flow, service-unavailable message
- [ ] Fix or add missing [DEPLOY_RENDER_VERCEL.md](./DEPLOY_RENDER_VERCEL.md) (linked from README) or remove broken link
- [ ] README banner: **`make run-api` / `src/api`** = production; root `main.py` = legacy baseline

---

## Phase 9 — Stretch (optional, for top marks) 🔄

| Item | Status | Notes |
|------|--------|--------|
| LangFuse tracing enabled | 🔄 | Plumbing done; capture viva screenshots when enabled |
| Combined itinerary / merge | ✅ | Multi-route + merge LLM |
| Web search MCP | ✅ | Phase 3b |
| Memory / context | ✅ | `SessionStore` + prompt `memory_context` |
| Docker + CI | ✅ | `docker-publish.yml`, prod compose |
| Persistent memory (Redis/LT) | ⏳ | Phase 9+ if time |
| Result cards in UI | ⏳ | Structured hotel/flight presentation |
| pytest on push | ⏳ | HTTP/agent smoke in CI |

---

## Phase 10 — Final delivery sequence ⏳

Ordered work to close the assessment and portfolio. Do these **in sequence** so deploy and docs reflect a stable codebase.

### Step 1 — Polish the codebase

**Goal:** One clear production path; no confusion at viva.

| Task | Detail |
|------|--------|
| Legacy boundary | Document root `main.py`, `agents/*`, `frontend.py` as **starter only**; never wire new features there |
| MCP path | Confirm production always uses `build_agent_mcp()` in `src/api/main.py` |
| Error surfaces | Ensure stream `{type: "error"}` and tool JSON errors become user-readable assistant text |
| Scripts | All `make test-*` green before deploy |
| Optional cleanup | Trim dead imports, align `.env.example` with droplet `.env` template in DEPLOY_DO_API |

**Exit criteria:** Reviewer can clone → `make run-api` + `make run-ui` → successful hotel search without reading legacy tree.

---

### Step 2 — Deploy backend on a single droplet

**Goal:** Public HTTPS API (assessment: hosted backend, MCP reachable at runtime).

| Task | Detail |
|------|--------|
| Secrets | GitHub Actions: `DOCKER_*`, `DROPLET_HOST`, `SSH_PRIVATE_KEY` |
| Server | `~/bookme-ai`, `compose.prod.api.yaml`, server-side `.env` |
| Proxy | Caddy site block → API; TLS (custom domain or sslip.io per [DEPLOY_DO_API.md](./DEPLOY_DO_API.md)) |
| Verify | `curl https://<api>/health`, `curl https://<api>/ready`, one `POST /chat` from local |
| CI | Push to `main` triggers image publish + deploy |

**Exit criteria:** `/ready` OK; chat works with production keys; no localhost-only backend for submission.

---

### Step 3 — Polish the UI

**Goal:** Assessment FE core on the **React** app (`frontend/`).

| Task | Detail |
|------|--------|
| Deploy | Vercel production; env: Clerk keys, `VITE_API_URL` → droplet API |
| UX | Travel theme, mobile layout, chain-of-thought + loading states |
| Errors | Friendly copy for 503/MCP/auth (already in `useChatStream`; verify against live API) |
| Optional | Result cards, copy-plan button, quick replies |
| Gradio | Either enhance `frontend.py` for course Gradio requirement **or** state in README that React is the submitted chat UI |

**Exit criteria:** Shareable frontend URL; signed-in (or dev-bypass) stream chat against production API.

---

### Step 4 — Polish documentation

**Goal:** Setup, MCP, deploy, and user paths are submission-ready.

| Deliverable | Content |
|-------------|---------|
| Root `README.md` | Live links, quick start, architecture, assessment mapping |
| `docs/MCP_SETUP.md` | Servers, tools, `make test-mcp`, Inspector, troubleshooting |
| Deploy docs | DO droplet + Vercel cross-links; env tables |
| User guide | `docs/USER_GUIDE.md` or README section with screenshots |
| Roadmap | This file — phases marked ✅ when each step completes |

**Exit criteria:** New developer can run MCP smoke test and find deployed apps without asking.

---

### Step 5 — Write articles about the project

**Goal:** Public narrative for portfolio and viva prep (architecture decisions in prose).

**Suggested topics (pick 2–4):**

1. **MCP as the travel tool boundary** — stdio servers, adapters, swapping Convex without touching orchestrator nodes  
2. **Two-graph design** — parallel guardrail/router decision graph vs orchestrator fan-out  
3. **SSE chain-of-thought** — stage/tool events vs full answer; UX tradeoffs  
4. **Deploying LangGraph + MCP on one droplet** — Docker, lifespan MCP spawn, Caddy  
5. **From linear baseline to intent-routed agents** — what changed in BookMe AI vs starter repo  

**Formats:** Dev.to / Medium / LinkedIn article, or repo `docs/articles/` as Markdown (link from README).

**Exit criteria:** At least one published or repo-hosted article with diagrams and links to live demo + GitHub.

---

## Decision log (consolidated)

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Reference architecture | Parallel decision graph + MCP orchestrator | MCP, orchestrator, SSE, lifespan |
| Repo layout | `src/` package | Separates new system from root baseline |
| MCP transport | stdio | Matches course reference; easy local + viva |
| External APIs | Convex via tools only | MCP → tools → http_client → Convex |
| HTTP layer | Shared `http_client.py` | DRY for hotel+flight; explicit errors vs baseline `None` |
| LLM provider | OpenAI default | Simplest setup; YAML switch to Groq/OpenRouter |
| Prompts | LangFuse + local fallback | Edit without redeploy; works offline |
| Tracing | LangFuse SDK v4 (`@observe`, `propagate_attributes`, `update_current_span`) |
| Chat memory | In-memory `SessionStore`; `(user_id, session_id)`; YAML window |
| ST vs LangGraph checkpoint | Custom ST store; no checkpointer in MVP |
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
  STREAMING.md          # SSE + token streaming
  DEPLOY_DO_API.md
  DEPLOY_DO_VERCEL.md
  MCP_SETUP.md          (Phase 8 — to add)
  USER_GUIDE.md         (Phase 10 — optional)
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

# API + UI
make run-api
make run-ui

# Deploy (see DEPLOY_DO_API.md)
# GitHub Actions → Docker Hub → droplet compose.prod.api.yaml
```

---

## Assessment mapping (SRS)

| Requirement | Phase | Status |
|-------------|-------|--------|
| E1 MCP servers | 2–3b, wired in 5–6 | ✅ |
| E2 Intent routing | 4–5 | ✅ |
| E3 Graceful failures | 2–3 (tools), 5 (agents) | ✅ |
| FE streaming + activity | 6 (API SSE), 7 (UI) | ✅ stages + CoT + token deltas |
| FE Gradio (SRS literal) | 0 baseline `frontend.py` | ⚠️ React is primary; Gradio minimal |
| Deploy + docs | 8, 10 | 🔄 Docker/CI ✅; live URLs + MCP guide ⏳ |
| Git branches / PRs | Ongoing | ✅ incremental history |
| Stretch (memory, Docker, observability) | 9 | 🔄 largely done |

---

## Next recommended step

Start **Phase 10, Step 1** (codebase polish), then **Step 2** (single-droplet backend deploy per [DEPLOY_DO_API.md](./DEPLOY_DO_API.md)).

After API is live: **Step 3** (UI on Vercel) → **Step 4** (docs + MCP_SETUP + submission URLs) → **Step 5** (articles).

Track completion by checking boxes in Phase 8 and Phase 10 sections above.
