<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/LangGraph-0.4+-FF6F00?logo=langchain&logoColor=white" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/MCP-Protocol-4B32C3?logo=json&logoColor=white" />
</p>

# BookMe AI

> **MCP-based multi-agent travel assistant powered by a parallel decision graph, LangGraph orchestrator, and real-time streaming API.**

BookMe AI is an intelligent travel planning system built on a modern AI architecture. It orchestrates multiple specialized AI agents through a LangGraph state machine to handle hotel bookings, flight searches, and general travel inquiries. By utilizing the Model Context Protocol (MCP) and a parallel guardrail/router decision graph, BookMe AI delivers robust, scalable, and secure AI interactions.

---

## Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Agent Pipeline](#-agent-pipeline)
- [Memory System](#-memory-system)
- [Retrieval Strategies](#-retrieval-strategies)
- [Voice Pipeline](#-voice-pipeline)
- [MCP Servers (Tool Layer)](#-mcp-servers-tool-layer)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Deployment](#-deployment)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [Observability](#-observability)
- [License](#-license)

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **Multi-Agent Orchestrator** | LangGraph fan-out to specialized agents (Hotel, Flight, Web Search, General Q&A) to handle diverse user queries concurrently. |
| **Guardrail System** | Parallel LangGraph sub-graph that runs scope-filtering and routing simultaneously, rejecting out-of-scope non-travel queries instantly. |
| **Model Context Protocol (MCP)** | Standardized tool access via MCP stdio servers, decoupling LLM nodes from raw HTTP clients for external integrations (Convex, Tavily). |
| **Streaming API** | Server-Sent Events (SSE): chain-of-thought stages, MCP tool progress, and **LLM token deltas** on the final answer. See [docs/STREAMING.md](docs/STREAMING.md). |
| **Multi-Provider LLMs** | Unified and configurable access to OpenAI and Google models via YAML settings, featuring fallback configurations. |
| **Observability** | End-to-end tracing with LangFuse — prompt management, cost tracking, and detailed span analysis without needing a redeploy. |
| **Secure Authentication** | Integration with Clerk for secure JWT-based API access (easily toggleable for local development). |

---

## 🏗️ System Architecture

### High-Level Overview

```mermaid
graph TD
    subgraph Clients["Clients"]
        SPA["React SPA (Vite + Clerk)"]
        API_Client["REST API / SSE Streams"]
    end

    subgraph Gateway["Gateway Layer"]
        FastAPI["FastAPI App (REST + SSE Streaming)"]
    end

    subgraph Orchestration["Orchestration Layer (LangGraph)"]
        Guardrail["Guardrail (Scope Filter)"]
        Router["Router (Intent Classifier)"]
        Bridge["Bridge & Orchestrator Fan-out"]
    end

    subgraph Tools["Tool Layer (MCP Servers)"]
        Hotel["Hotel Server (Convex API)"]
        Flight["Flight Server (Convex API)"]
        Tavily["Web Search Server (Tavily API)"]
    end

    SPA --> FastAPI
    API_Client --> FastAPI
    
    FastAPI --> Guardrail
    FastAPI --> Router
    
    Guardrail --> Bridge
    Router --> Bridge
    
    Bridge --> Hotel
    Bridge --> Flight
    Bridge --> Tavily
```

---

## 🤖 Agent Pipeline

The core orchestration relies on a dual-state LangGraph implementation:

```mermaid
graph LR
    User["User Message + Memory"] --> Guardrail
    User --> Router
    
    subgraph DecisionGraph["Gate (Decision Graph)"]
        Guardrail["Guardrail Node"]
        Router["Router Node"]
        Guardrail --> Decide{"Decide"}
        Router --> Decide
    end
    
    Decide -->|"proceed"| Orch["Orchestrator Fan-out"]
    Decide -->|"out_of_scope"| OOS["Out of Scope Template"]
    
    subgraph Agents["Agents"]
        Hotel["Hotel Agent"]
        Flight["Flight Agent"]
        WebSearch["Web Search Agent"]
        GeneralQA["General Q&A"]
    end
    
    Orch -.-> Hotel
    Orch -.-> Flight
    Orch -.-> WebSearch
    Orch -.-> GeneralQA
    
    Hotel --> Merge["Merge Model"]
    Flight --> Merge
    WebSearch --> Merge
    GeneralQA --> Merge
    
    Merge --> Output["Final Output"]
    OOS --> Output
```
| Layer | Role | What It Does |
|---|---|---|
| **Gate (Decision Graph)** | Scope & Intent | Evaluates `in_scope` vs `out_of_scope`. If valid, routes to appropriate actions (`hotel`, `flight`, `web_search`, `general_qa`). Guardrail and routing happen in parallel for zero added latency. |
| **Orchestrator** | Agent Execution | Takes the routed decisions and fans out to specialized MCP-backed agents. Combines their results using a merge model. |
| **Agents** | Tool usage | Hotel and Flight agents search **and book** via Convex MCP tools; Web Search handles live destination queries (e.g., tourist spots). |

---

## 🧠 Memory System

BookMe AI relies on an efficient, thread-safe memory architecture:

- **SessionStore**: Context is isolated by `(user_id, session_id)` ensuring complete privacy between concurrent users.
- **Configurable Context**: Controlled by `config/params.yaml`, the system dictates `max_turns` and `history_window` to stay well within token limits.

*(Note: Advanced Long-Term/Procedural memory systems like Vector DBs are currently **Under Development** for future phases).*

---

## 🔍 Retrieval Strategies

| Strategy | Description | Use Case |
|---|---|---|
| **API Tool Calling** | Direct REST lookup via MCP servers to live data (Convex). | Live flight availability, hotel searching/booking |
| **Web Search** | Live web scraping and indexing using Tavily. | Exploring tourist spots, weather, or real-time events |

---

## 🎙️ Voice Pipeline

*This feature is currently **Under Development**.*
Future iterations will introduce a LiveKit-powered real-time voice pipeline for hands-free travel orchestration.

---

## 🔧 MCP Servers (Tool Layer)

The agent's tools are securely exposed via **Model Context Protocol (MCP)** stdio servers:

| MCP Server | Tools | Backend |
|---|---|---|
| **Hotel Server** | `list_hotels`, `search_hotels`, `book_hotel` | Convex HTTP endpoint |
| **Flight Server** | `list_flights`, `search_flights`, `book_flight` | Convex HTTP endpoint |
| **Web Search Server** | `search` | Tavily API |

---

## 🛠️ Tech Stack

### Backend
| Component | Technology |
|---|---|
| Framework | **FastAPI** (async, ASGI, SSE) |
| Agent Orchestration | **LangGraph** & **LangChain** |
| Tool Standard | **MCP** (`langchain-mcp-adapters`) |
| Observability | **LangFuse** (tracing, prompt management) |
| HTTP Clients | **httpx**, **requests**, **tenacity** (retries) |

### Frontend
| Component | Technology |
|---|---|
| Framework | **React 19** + **TypeScript** |
| Build Tool | **Vite** |
| Authentication | **Clerk** (JWT tokens) |

---

## 📁 Project Structure

```
BookMe AI/
│
├── src/                          # Backend source code
│   ├── agents/                   # 🤖 Agent orchestration layer
│   │   ├── chat_pipeline.py      #    Main entry for chat turn
│   │   ├── decision_graph.py     #    Parallel guardrail + router sub-graph
│   │   ├── orchestrator.py       #    Agent fan-out logic
│   │   ├── router.py             #    Intent query classifier
│   │   ├── state.py              #    AgentState TypedDict
│   │   ├── prompts/              #    LangFuse-managed prompt integration
│   │   └── tools/                #    Internal tools (HTTP implementations)
│   │
│   ├── api/                      # 🌐 FastAPI application
│   │   ├── main.py               #    App factory, lifespan
│   │   ├── middleware.py         #    CORS, Auth
│   │   ├── schemas.py            #    Pydantic models
│   │   └── routers/              #    API endpoints (chat.py, etc.)
│   │
│   ├── mcp_servers/              # 🔌 Model Context Protocol servers
│   │   ├── flight_server.py      #    Flight MCP interface
│   │   ├── hotel_server.py       #    Hotel MCP interface
│   │   ├── mcp_config.py         #    Server orchestration
│   │   └── web_search_server.py  #    Tavily MCP interface
│   │
│   └── infrastructure/           # 🏗️ Infrastructure layer
│       ├── config.py             #    YAML config loader
│       ├── llm.py                #    LLM provider factory
│       ├── log.py                #    Loguru setup
│       ├── observability.py      #    LangFuse integration
│       └── session_store.py      #    In-memory chat state
│
├── frontend/                     # 💻 React frontend (Vite)
│   └── src/                      #    React components & UI
│
├── config/                       # ⚙️ Configuration files
│   ├── params.yaml               #    System parameters (context, API URLs)
│   └── models.yaml               #    LLM configurations
│
├── compose.prod.api.yaml         # 🐳 Production API only (DO droplet + Vercel UI)
├── compose.prod.yaml             #    Production API + nginx UI (single VM)
├── docker-compose.yml            #    Local dev stack (`make docker-up`)
│
├── docs/                         # 📚 Architecture and setup documentation
├── Makefile                      # 🛠️ Task runner (tests, run commands)
└── requirements.txt              #    Python dependencies
```

---

## 🚀 Getting Started

Run all `make` commands from the **repository root** (`BookMe AI/`).

### Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Node.js | 18+ (npm) |
| Make | GNU Make or BSD make |
| Docker | Optional — for `make docker-up` |

Hotel and flight tools call the Convex URLs in `config/params.yaml` (no separate Convex setup for local dev).

---

### Option A — Native dev (recommended)

Best for day-to-day work: hot-reload API + Vite dev server.

#### 1. One-time install

```bash
git clone <your-repo-url> "BookMe AI"
cd "BookMe AI"
make setup
```

`make setup` creates `.venv`, installs `requirements.txt`, and runs `npm install` in `frontend/`.

#### 2. Environment files

**API** — copy and edit the repo root env:

```bash
cp .env.example .env
```

Minimum keys for a working chat:

| Variable | Required | Notes |
|----------|----------|--------|
| `OPENAI_API_KEY` | Yes | Router, guardrail, agents |
| `TAVILY_API_KEY` | Yes | Web search MCP (`tourist spots`, etc.) |
| `GOOGLE_API_KEY` | Recommended | Multi-agent merge model in `config/models.yaml` |

**Frontend** — copy and edit:

```bash
cp frontend/.env.example frontend/.env
```

Keep `VITE_API_URL=http://127.0.0.1:8000` (Vite proxies browser requests from `/api/*` to this host).

#### 3. Auth mode (pick one)

**Local dev without Clerk** (fastest — no sign-in):

Root `.env`:

```bash
AUTH_DISABLED=1
# optional: DEV_USER_ID=dev-user
```

`frontend/.env`:

```bash
VITE_AUTH_DISABLED=true
# optional: VITE_DEV_USER_ID=dev-user
```

**Production-style Clerk** (sign-in on localhost):

Root `.env`: `AUTH_DISABLED=0`, `CLERK_SECRET_KEY=sk_test_…`, and origins including `http://localhost:5173` in `CLERK_AUTHORIZED_PARTIES` and `CORS_ORIGINS`.

`frontend/.env`: `VITE_AUTH_DISABLED=false`, `VITE_CLERK_PUBLISHABLE_KEY=pk_test_…`.

Full checklist: [docs/CLERK_SETUP.md](docs/CLERK_SETUP.md). After editing env, run `make check-clerk` when Clerk is enabled.

#### 4. Run (two terminals)

**Terminal 1 — API**

```bash
source .venv/bin/activate   # Windows: .venv\Scripts\activate
make run-api
```

- API: http://127.0.0.1:8000  
- OpenAPI: http://127.0.0.1:8000/docs  
- Readiness (MCP tools): http://127.0.0.1:8000/ready  

**Terminal 2 — UI**

```bash
make run-ui
```

- App: http://127.0.0.1:5173  
- Chat: http://127.0.0.1:5173/app  

#### 5. Smoke test

```bash
make check-config
curl -fsS http://127.0.0.1:8000/health
curl -N http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"session_id":"demo-1","user_id":"dev-user","message":"tourist spots in London"}'
```

(With `AUTH_DISABLED=1`, `user_id` in the JSON body is used; with Clerk, use the signed-in UI instead.)

---

### Option B — Docker Compose (API + nginx UI)

Single command stack; UI on port **8080** with `/api` proxied to the API container.

#### 1. Root `.env`

Same API keys as Option A. Docker build reads these from `.env`:

- **No Clerk:** `AUTH_DISABLED=1` and `VITE_AUTH_DISABLED=true`
- **With Clerk:** `AUTH_DISABLED=0`, `CLERK_SECRET_KEY`, and `VITE_CLERK_PUBLISHABLE_KEY=pk_test_…` (baked into the web image at build time)

Optional image namespace:

```bash
export DOCKER_REGISTRY_USER=your_dockerhub_username   # default tag prefix: bookme/*
```

#### 2. Start stack

```bash
make docker-up
```

- UI: http://localhost:8080 (chat at `/app`)  
- API (direct): http://localhost:8000  

Stop: `make docker-down`.

Images: `docker/api/Dockerfile`, `docker/web/Dockerfile`. Production pull-only: `compose.prod.yaml`.

---

### Makefile reference

| Command | Purpose |
|---------|---------|
| `make setup` | One-time `.venv` + Python deps + `frontend` npm install |
| `make install` | Re-install Python deps (uses `.venv/bin/pip` when present) |
| `make install-ui` | `npm install` in `frontend/` only |
| `make run-api` | FastAPI with reload on `:8000` |
| `make run-ui` | Vite dev server on `:5173` |
| `make docker-up` | `docker compose up -d --build` |
| `make check-config` | Validate provider keys vs `config/models.yaml` |
| `make check-clerk` | Validate Clerk env when `AUTH_DISABLED=0` |

Run `make` or `make help` for tests, MCP inspectors, and LangFuse seeding.

---

## ☁️ Deployment

Production uses a **split stack**: the React UI on **Vercel**, the FastAPI + MCP backend on a **DigitalOcean Droplet** (Docker). This matches the booking-platform-api pattern (Docker Hub image → SSH pull on the server).

### Architecture

| Layer | Platform | How it runs |
|-------|----------|-------------|
| **Frontend** | [Vercel](https://vercel.com) | Root directory `frontend/`; connects to API via `VITE_API_URL` |
| **API + MCP** | DigitalOcean Droplet | `compose.prod.api.yaml` — API on `127.0.0.1:8000` only |
| **HTTPS** | Caddy (on droplet) | Reverse proxy `:443` → localhost (custom domain or [sslip.io](https://sslip.io)) |
| **Images** | Docker Hub | `DOCKER_USERNAME/bookme-ai-api:latest` built by GitHub Actions |

```text
Browser (https://your-app.vercel.app)
    → VITE_API_URL (https://api.example.com or https://IP-DASHED.sslip.io)
        → Caddy :443
            → bookme-ai-api container :8000
                → MCP stdio (hotel / flight / web search)
```

Vercel does **not** run the API. The droplet does **not** serve the React app when using Vercel (no `web` container in prod).

### Same droplet as booking-platform-api

BookMe can share one VM with booking-platform-api. Typical layout:

| App | Directory | Compose file | Internal port |
|-----|-----------|--------------|---------------|
| booking-platform-api | `~/booking-platform-api` | `compose.prod.yaml` | `:3000` |
| BookMe AI | `~/Bookme-AI` | `compose.prod.api.yaml` | `127.0.0.1:8000` |

Add a **second Caddy site block** for BookMe; do not remove booking’s block. See [docs/DEPLOY_DO_API.md](docs/DEPLOY_DO_API.md).

### Environment variables (production)

**Vercel** (frontend — rebuild required after changes):

| Variable | Example |
|----------|---------|
| `VITE_API_URL` | `https://178-128-17-103.sslip.io` (HTTPS API URL, no trailing slash) |
| `VITE_CLERK_PUBLISHABLE_KEY` | `pk_live_…` |
| `VITE_AUTH_DISABLED` | `false` |

**Droplet** (`~/Bookme-AI/.env` — restart container after edits):

| Variable | Example |
|----------|---------|
| `OPENAI_API_KEY`, `TAVILY_API_KEY`, `GOOGLE_API_KEY` | LLM + merge + web search |
| `DOCKER_REGISTRY_USER` | Same as GitHub `DOCKER_USERNAME` |
| `CLERK_SECRET_KEY` | Clerk secret key |
| `CORS_ORIGINS` | `https://your-app.vercel.app` (**frontend** origin, not the API URL) |
| `CLERK_AUTHORIZED_PARTIES` | Same Vercel URL(s) as `CORS_ORIGINS` |
| `AUTH_DISABLED` | `0` in production |

Also allow the Vercel origin in the **Clerk Dashboard**. Full checklist: [docs/CLERK_SETUP.md](docs/CLERK_SETUP.md).

### One-time droplet setup

```bash
git clone https://github.com/YOUR_USER/Bookme-AI.git ~/Bookme-AI
cd ~/Bookme-AI
cp .env.example .env   # fill keys + CORS / Clerk origins
export DOCKER_REGISTRY_USER=your_dockerhub_username
docker compose -f compose.prod.api.yaml pull
docker compose -f compose.prod.api.yaml up -d
curl -sS http://127.0.0.1:8000/health
```

Install **Caddy** for TLS, bind API to localhost only (`compose.prod.api.yaml` already does), open firewall **22 / 80 / 443**. Without HTTPS, a Vercel app cannot call the API (mixed content).

**No domain?** Use sslip.io: IP `178.128.17.103` → `https://178-128-17-103.sslip.io`. Details: [docs/DEPLOY_DO_API.md](docs/DEPLOY_DO_API.md#no-custom-domain-https-without-buying-a-domain).

### Local / single-VM alternatives

| Goal | Command / file |
|------|----------------|
| Dev (hot reload) | `make run-api` + `make run-ui` — [Getting Started](#-getting-started) |
| Local Docker (API + nginx UI) | `make docker-up` → `compose.prod.yaml` / `docker-compose.yml` |
| Manual image push | `make docker-push` (sets Hub tags from `DOCKER_REGISTRY_USER`) |

### Detailed guides

| Doc | When to use |
|-----|-------------|
| [docs/DEPLOY_DO_API.md](docs/DEPLOY_DO_API.md) | First API deploy on DO, Caddy, sslip.io, GitHub secrets, troubleshooting |
| [docs/DEPLOY_DO_VERCEL.md](docs/DEPLOY_DO_VERCEL.md) | Wire Vercel frontend to the droplet API |
| [docs/STREAMING.md](docs/STREAMING.md) | SSE / chain-of-thought in production |

---

## 🔄 CI/CD Pipeline

Workflow: [`.github/workflows/docker-publish.yml`](.github/workflows/docker-publish.yml) — runs on **push to `main`** or **manual dispatch**.

| Job | What it does |
|-----|----------------|
| `push_to_registry` | Build `docker/api/Dockerfile` → push `bookme-ai-api:latest` and `:sha` to Docker Hub |
| `push_web` | Build `docker/web/Dockerfile` → push `bookme-ai-web:latest` (optional; prod UI is on Vercel) |
| `deploy` | SSH to droplet → `git pull` → `compose.prod.api.yaml pull` → `up -d` → `docker image prune -f` |

**GitHub Actions secrets** (BookMe repo → Settings → Secrets):

| Secret | Purpose |
|--------|---------|
| `DOCKER_USERNAME` | Docker Hub user |
| `DOCKER_TOKEN` | Hub access token |
| `DROPLET_HOST` | Droplet public IP |
| `SSH_PRIVATE_KEY` | Private key whose `.pub` is in droplet `authorized_keys` |
| `VITE_CLERK_PUBLISHABLE_KEY` | Optional — baked into `push_web` image only |

Deploy script path on the server: **`~/Bookme-AI`** (must match clone location).

**Vercel** deploys the frontend separately (connect Git repo, root `frontend/`). After changing `VITE_API_URL`, trigger a Vercel redeploy.

**Storage note:** each run tags `bookme-ai-api:${{ github.sha }}` on Hub; droplet `image prune -f` removes dangling layers only. Prune old Hub tags or use `docker image prune -af` on the droplet occasionally if disk is tight.

---

## ⚙️ Configuration

Runtime behavior is easily controlled via YAML:

### `config/params.yaml`
- Service URLs (Convex base endpoints).
- Session memory configurations (max turns, window size).
- Observability and prompt cache TTL settings.

### `config/models.yaml`
- Maps roles (router, guardrail, chat, **merge**) to LLM models — e.g. OpenAI `gpt-4o-mini` for agents, Google Gemini for multi-route merge.
- Temperature and fallback controls.

### Root `.env` (secrets)
- API keys, Clerk, `CORS_ORIGINS`, `DOCKER_REGISTRY_USER` — see `.env.example`.
- Production droplet uses the same variables via `compose.prod.api.yaml` `env_file: .env`.

---

## 📡 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/health` | `GET` | API Liveness check |
| `/ready` | `GET` | Config + MCP tool readiness check |
| `/config` | `GET` | Active models list (non-secret) |
| `/chat/reset` | `POST` | Clear session memory for `(user_id, session_id)` |
| `/chat` | `POST` | Standard blocking chat turn |
| `/chat/stream`| `POST` | Server-Sent Events (SSE) streaming chat turn |

You can test chat locally via curl:
```bash
curl -N http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"session_id":"demo-1","user_id":"dev-user","message":"tourist spots in London"}'
```

---

## 📊 Observability

BookMe AI uses **LangFuse** (`@observe`) for comprehensive observability:
- **Prompt Management:** System prompts are fetched from LangFuse (or local fallbacks) to allow hot-editing without redeploys.
- **Tracing:** Complete span visibility across the decision graph and MCP agent fan-out.
- **Token Tracking:** Usage tracked for every LLM interaction.

---

## 📄 License

This project is proprietary software. All rights reserved.

---

<p align="center">
  Built with ❤️
</p>
