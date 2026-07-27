# BookMe AI

MCP-based multi-agent travel assistant: parallel **guardrail + router** decision graph, orchestrator fan-out (hotel / flight / general Q&A / **web search** via Tavily), and FastAPI chat with SSE.

**Production path:** `src/` (Week 13–style layout). Root `main.py` / `frontend.py` are legacy starter demos.

## Requirements

- **Python 3.11+** (MCP / `langchain-mcp-adapters`)
- **OPENAI_API_KEY** (router, guardrail, agents)
- **GOOGLE_API_KEY** (multi-route merge model in `config/models.yaml`)
- **TAVILY_API_KEY** (web search MCP agent)
- Optional: **LANGFUSE_*** for tracing and prompt management

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # fill keys
```

See `.env.example` and [docs/CLERK_SETUP.md](docs/CLERK_SETUP.md) for `AUTH_DISABLED`, Clerk, and LangFuse toggles.

## Run the API (recommended)

```bash
make run-api
```

- API: http://127.0.0.1:8000  
- Docs: http://127.0.0.1:8000/docs  

Local dev uses **`AUTH_DISABLED=1`** by default; send `user_id` in the JSON body or set `DEV_USER_ID`.

### React UI (recommended)

```bash
cd frontend && cp .env.example .env && npm install
make run-api   # terminal 1
make run-ui    # terminal 2 → http://127.0.0.1:5173
```

With **`VITE_AUTH_DISABLED=false`** (default in `frontend/.env.example`), sign in with Clerk. Run `make check-clerk` after setting API keys.

### Chat (non-streaming)

```bash
curl -s http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo-1",
    "user_id": "dev-user",
    "message": "Find hotels in Colombo and a flight BOM to CMB"
  }'
```

### Chat (SSE chain-of-thought)

```bash
curl -N http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"session_id":"demo-1","user_id":"dev-user","message":"tourist spots in London"}'
```

### Other API routes

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Liveness |
| `GET /ready` | Config + MCP tool count |
| `GET /config` | Active models (non-secret) |
| `POST /chat/reset` | Clear session memory for `(user_id, session_id)` |

## Makefile smoke tests

```bash
make test-mcp                    # 7 MCP tools (hotels, flights, web search)
make test-decision               # Guardrail + router + bridge
make test-orchestrator           # Full orchestrator (network + keys)
make test-orchestrator-web-search
make test-session-store
make test-chat-pipeline
make config
```

## Architecture (short)

```text
POST /chat[/stream]
  → chat_pipeline.run_chat_turn
       → decision_graph (guardrail ∥ router → decide)
       → orchestrator (MCP agents → merge)  unless out_of_scope
  → SessionStore (user_id + session_id)
```

Details: [docs/DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md), [docs/DECISION_GRAPH_NOTES.md](docs/DECISION_GRAPH_NOTES.md).

## Legacy starter (optional)

```bash
python main.py      # root FastAPI + hardcoded tools
python frontend.py  # Gradio
```

## Tech stack

- FastAPI, LangGraph, LangChain  
- MCP (stdio): Convex hotel/flight APIs + Tavily web search  
- LangFuse (optional): `@observe` tracing + prompt management (SDK v4: `propagate_attributes`)
