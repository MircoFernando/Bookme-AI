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
- [AWS Deployment](#-aws-deployment)
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
| **Streaming API** | Server-Sent Events (SSE) enabled FastAPI endpoint delivering real-time chain-of-thought and agent tool usage to the frontend. |
| **Multi-Provider LLMs** | Unified and configurable access to OpenAI and Google models via YAML settings, featuring fallback configurations. |
| **Observability** | End-to-end tracing with LangFuse — prompt management, cost tracking, and detailed span analysis without needing a redeploy. |
| **Secure Authentication** | Integration with Clerk for secure JWT-based API access (easily toggleable for local development). |

---

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                     │
│   React SPA (Vite + Clerk)  │  REST API / SSE Streams               │
└──────────────┬──────────────┴─────┬─────────────────────────────────┘
               │                    │
               ▼                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      GATEWAY LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ FastAPI App (REST + SSE Streaming, Session Management)      │   │
│  └───────────────────────────────┬─────────────────────────────┘   │
└──────────────────────────────────┼───────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER (LangGraph)                    │
│                                                                      │
│   ┌────────────┐    ┌─────────────┐                                  │
│   │ Guardrail  │    │   Router    │  (Parallel Decision Graph)       │
│   │ (Scope     │───▶│  (Intent    │                                  │
│   │  Filter)   │    │ Classifier) │                                  │
│   └──────┬─────┘    └──────┬──────┘                                  │
│          │                 │                                         │
│          ▼                 ▼                                         │
│   ┌────────────────────────────────┐                                 │
│   │  Bridge & Orchestrator Fan-out │                                 │
│   └────────────────────────────────┘                                 │
└──────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       TOOL LAYER (MCP Servers)                       │
│                                                                      │
│   ┌───────────────┐   ┌────────────────┐   ┌─────────────────┐       │
│   │  Hotel Server │   │  Flight Server │   │ Web Search (Tavily) │     │
│   │  (Convex API) │   │  (Convex API)  │   │     Server      │       │
│   └───────────────┘   └────────────────┘   └─────────────────┘       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Agent Pipeline

The core orchestration relies on a dual-state LangGraph implementation:

| Layer | Role | What It Does |
|---|---|---|
| **Gate (Decision Graph)** | Scope & Intent | Evaluates `in_scope` vs `out_of_scope`. If valid, routes to appropriate actions (`hotel`, `flight`, `web_search`, `general_qa`). Guardrail and routing happen in parallel for zero added latency. |
| **Orchestrator** | Agent Execution | Takes the routed decisions and fans out to specialized MCP-backed agents. Combines their results using a merge model. |
| **Agents** | Tool usage | The Hotel agent fetches accommodations, the Flight agent books flights, and the Web Search agent handles live queries (e.g., tourist spots). |

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
├── docs/                         # 📚 Architecture and setup documentation
├── Makefile                      # 🛠️ Task runner (tests, run commands)
└── requirements.txt              #    Python dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js (for the React frontend)
- Convex backend configured (for Travel APIs)

### 1. Clone & Install Backend

```bash
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # fill keys
```

### 2. Configure Environment

Fill out `.env` with the following variables:
- `OPENAI_API_KEY` (Required for router, guardrail, agents)
- `GOOGLE_API_KEY` (Optional for merging model)
- `TAVILY_API_KEY` (Required for Web Search MCP)
- `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` (Optional, for observability)

*(See `docs/CLERK_SETUP.md` for `AUTH_DISABLED` toggles for local dev.)*

### 3. Run the API

```bash
make run-api
```
- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

### 4. Run the React UI

In a separate terminal:
```bash
cd frontend
cp .env.example .env
npm install
make run-ui    # Navigates to http://127.0.0.1:5173
```

---

## ☁️ AWS Deployment

*This feature is currently **Under Development**.*
Deployment instructions for AWS (ECS Fargate / API Gateway) will be added in Phase 8.

---

## 🔄 CI/CD Pipeline

*This feature is currently **Under Development**.*
Automated testing and container deployment pipelines will be detailed upon completion of Docker integration.

---

## ⚙️ Configuration

Runtime behavior is easily controlled via YAML:

### `config/params.yaml`
- Service URLs (Convex base endpoints).
- Session memory configurations (max turns, window size).
- Observability and prompt cache TTL settings.

### `config/models.yaml`
- Maps roles (router, guardrail, chat) to specific LLM models (e.g., `gpt-4o-mini`).
- Temperature and fallback controls.

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
