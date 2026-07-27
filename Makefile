# =============================================================================
# BookMe AI — Makefile
# =============================================================================
# All Python targets run with PYTHONPATH=src so imports resolve from the
# src/ layout (infrastructure.*, agents.*, mcp_servers.*, api.*).
# =============================================================================

PYTHON ?= .venv/bin/python
UVICORN ?= .venv/bin/uvicorn
PY := PYTHONPATH=src $(PYTHON)

.PHONY: help setup install install-ui config check-config check-clerk run-api run-ui \
        docker-build docker-up docker-down docker-push \
        inspect-hotel inspect-flight inspect-web-search test-mcp test-decision test-orchestrator test-orchestrator-web-search test-session-store test-chat-pipeline \
        seed-langfuse test clean

# ── Help (default) ────────────────────────────────────────────────────────────
help:
	@echo "BookMe AI — available commands:"
	@echo ""
	@echo "Local development (from repo root):"
	@echo "  make setup          One-time: .venv + pip + frontend npm install"
	@echo "  make run-api        Terminal 1 — API  http://127.0.0.1:8000"
	@echo "  make run-ui         Terminal 2 — UI   http://127.0.0.1:5173  (chat at /app)"
	@echo "  make docker-up      Docker — UI http://localhost:8080, API :8000"
	@echo ""
	@echo "  make install        pip install -r requirements.txt (uses .venv if present)"
	@echo "  make install-ui     npm install in frontend/"
	@echo "  make config         Print active (non-secret) configuration"
	@echo "  make check-config   Validate OPENAI + GOOGLE keys for configured roles"
	@echo "  make check-clerk   Validate Clerk env when AUTH_DISABLED=0"
	@echo "  make docker-build   Build api + web images (docker compose build)"
	@echo "  make docker-down    Stop docker compose stack"
	@echo "  make docker-push    Tag & push images to Docker Hub (DOCKER_REGISTRY_USER)"
	@echo "  make inspect-hotel  Open MCP Inspector on hotel server"
	@echo "  make inspect-flight Open MCP Inspector on flight server"
	@echo "  make inspect-web-search Open MCP Inspector on web search server"
	@echo "  make test-mcp       Smoke test MultiServerMCPClient + 7 tools"
	@echo "  make test-decision  Decision subgraph + bridge (OPENAI_API_KEY)"
	@echo "  make test-orchestrator  Orchestrator E2E (OPENAI + GOOGLE + network)"
	@echo "  make test-orchestrator-web-search  Tourism → web_search MCP + Tavily"
	@echo "  make test-session-store SessionStore (user_id + session_id) isolation"
	@echo "  make test-chat-pipeline Decision + chat_pipeline (OPENAI_API_KEY)"
	@echo "  make seed-langfuse      Upload bookme-ai-* prompts to LangFuse (production label)"
	@echo "  make test           Run the test suite              (Day 7)"
	@echo "  make clean          Remove caches and __pycache__"

# ── Setup ─────────────────────────────────────────────────────────────────────
setup:
	python3.11 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -r requirements.txt
	cd frontend && npm install
	@echo ""
	@echo "Next steps:"
	@echo "  cp .env.example .env          # fill OPENAI_API_KEY, TAVILY_API_KEY, etc."
	@echo "  cp frontend/.env.example frontend/.env"
	@echo "  For local dev without Clerk: AUTH_DISABLED=1 in .env, VITE_AUTH_DISABLED=true in frontend/.env"
	@echo "  make run-api   # terminal 1"
	@echo "  make run-ui    # terminal 2 → http://127.0.0.1:5173/app"

install:
	@if [ -x .venv/bin/pip ]; then .venv/bin/pip install -r requirements.txt; else pip install -r requirements.txt; fi

install-ui:
	cd frontend && npm install

# ── Config ──────────────────────────────────────────────────────────────────────
config:
	@$(PY) -c "from infrastructure import config; config.dump()"

check-config:
	@$(PY) -c "from infrastructure import config; config.validate(); print('Config OK — provider:', config.PROVIDER, '| chat model:', config.CHAT_MODEL)"

check-clerk:
	@PYTHONPATH=src $(PYTHON) scripts/check_clerk_env.py

# ── Run (wired on later days) ────────────────────────────────────────────────────
run-api:
	cd src && PYTHONPATH=. ../$(UVICORN) api.main:app --reload --host 0.0.0.0 --port 8000

run-ui:
	cd frontend && npm run dev

# ── Docker (images under docker/) ─────────────────────────────────────────────
docker-build:
	docker compose build

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-push:
	@test -n "$(DOCKER_REGISTRY_USER)" || (echo "Set DOCKER_REGISTRY_USER (Docker Hub namespace)" && exit 1)
	docker compose build
	docker tag $(DOCKER_REGISTRY_USER)/bookme-ai-api:local $(DOCKER_REGISTRY_USER)/bookme-ai-api:latest
	docker tag $(DOCKER_REGISTRY_USER)/bookme-ai-web:local $(DOCKER_REGISTRY_USER)/bookme-ai-web:latest
	docker push $(DOCKER_REGISTRY_USER)/bookme-ai-api:latest
	docker push $(DOCKER_REGISTRY_USER)/bookme-ai-web:latest

# ── MCP inspection (Day 2) ────────────────────────────────────────────────────────
inspect-hotel:
	cd src && npx @modelcontextprotocol/inspector ../.venv/bin/python -m mcp_servers.hotel_server

inspect-flight:
	cd src && npx @modelcontextprotocol/inspector ../.venv/bin/python -m mcp_servers.flight_server

inspect-web-search:
	cd src && npx @modelcontextprotocol/inspector ../.venv/bin/python -m mcp_servers.web_search_server

test-mcp:
	PYTHONPATH=src .venv/bin/python scripts/test_mcp_client.py

test-decision:
	PYTHONPATH=src .venv/bin/python scripts/test_decision_graph.py

test-orchestrator:
	PYTHONPATH=src .venv/bin/python scripts/test_orchestrator.py

test-orchestrator-web-search:
	PYTHONPATH=src .venv/bin/python scripts/test_orchestrator_web_search.py

test-session-store:
	PYTHONPATH=src .venv/bin/python scripts/test_session_store.py

test-chat-pipeline:
	PYTHONPATH=src .venv/bin/python scripts/test_chat_pipeline.py

seed-langfuse:
	PYTHONPATH=src .venv/bin/python scripts/seed_langfuse_prompts.py

# ── Tests ─────────────────────────────────────────────────────────────────────────
test:
	PYTHONPATH=src pytest -q

# ── Cleanup ────────────────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	@echo "Cleaned."

.DEFAULT_GOAL := help
