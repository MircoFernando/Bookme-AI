# =============================================================================
# BookMe AI — Makefile
# =============================================================================
# All Python targets run with PYTHONPATH=src so imports resolve from the
# src/ layout (infrastructure.*, agents.*, mcp_servers.*, api.*).
# =============================================================================

PYTHON ?= .venv/bin/python
PY := PYTHONPATH=src $(PYTHON)

.PHONY: help install config check-config run-api run-ui \
        inspect-hotel inspect-flight test-mcp test-decision test-orchestrator test clean

# ── Help (default) ────────────────────────────────────────────────────────────
help:
	@echo "BookMe AI — available commands:"
	@echo ""
	@echo "  make install        Install Python dependencies"
	@echo "  make config         Print active (non-secret) configuration"
	@echo "  make check-config   Validate OPENAI + GOOGLE keys for configured roles"
	@echo "  make run-api        Run the FastAPI backend        (Day 5)"
	@echo "  make run-ui         Run the Gradio frontend         (Day 6)"
	@echo "  make inspect-hotel  Open MCP Inspector on hotel server"
	@echo "  make inspect-flight Open MCP Inspector on flight server"
	@echo "  make test-mcp       Smoke test MultiServerMCPClient + 6 tools"
	@echo "  make test-decision  Decision subgraph + bridge (OPENAI_API_KEY)"
	@echo "  make test-orchestrator  Orchestrator E2E (OPENAI + GOOGLE + network)"
	@echo "  make test           Run the test suite              (Day 7)"
	@echo "  make clean          Remove caches and __pycache__"

# ── Setup ─────────────────────────────────────────────────────────────────────
install:
	pip install -r requirements.txt

# ── Config ──────────────────────────────────────────────────────────────────────
config:
	@$(PY) -c "from infrastructure import config; config.dump()"

check-config:
	@$(PY) -c "from infrastructure import config; config.validate(); print('Config OK — provider:', config.PROVIDER, '| chat model:', config.CHAT_MODEL)"

# ── Run (wired on later days) ────────────────────────────────────────────────────
run-api:
	cd src && PYTHONPATH=. uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

run-ui:
	$(PY) frontend/app.py

# ── MCP inspection (Day 2) ────────────────────────────────────────────────────────
inspect-hotel:
	cd src && npx @modelcontextprotocol/inspector ../.venv/bin/python -m mcp_servers.hotel_server

inspect-flight:
	cd src && npx @modelcontextprotocol/inspector ../.venv/bin/python -m mcp_servers.flight_server

test-mcp:
	PYTHONPATH=src .venv/bin/python scripts/test_mcp_client.py

test-decision:
	PYTHONPATH=src .venv/bin/python scripts/test_decision_graph.py

test-orchestrator:
	PYTHONPATH=src .venv/bin/python scripts/test_orchestrator.py

# ── Tests ─────────────────────────────────────────────────────────────────────────
test:
	PYTHONPATH=src pytest -q

# ── Cleanup ────────────────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	@echo "Cleaned."

.DEFAULT_GOAL := help
