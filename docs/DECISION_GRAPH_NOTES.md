# Decision graph & routing — architecture notes

**Purpose:** Design log for Phase 4 (guardrail, router, decision graph, bridge). Captures engineering discussions, latency/cost tradeoffs, and viva talking points.

**Related:** [DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md) Phase 4–5.

---

## 1. Two-stage pipeline (mental model)

BookMe AI uses **two logical stages**, not two interchangeable “routers”:

| Stage | Component | Question answered | Output |
|-------|-----------|-------------------|--------|
| **1 — Gate** | Decision graph (guardrail + decide) | Is this message allowed for BookMe AI? | `verdict`: `out_of_scope` \| `proceed` |
| **2 — Intent** | Router inside same graph (parallel) | Which agents/tools for this in-scope turn? | `decision` → `route_decisions` after bridge |

**Phase 5 orchestrator** reads `AgentState` after the bridge: if `verdict != proceed`, return `final_answer`; else fan-out on `route_decisions` → MCP agents → merge.

```text
User message
     │
     ▼
chat_pipeline.run_chat_turn  (loads SessionStore → router_context)
     │
     ▼
DecisionState  ── decision_graph (guardrail ∥ router → decide)
     │
     ▼
decision_bridge.map_decision_to_agent_state()
     │
     ▼
AgentState  ── orchestrator (MCP agents) → final_answer
```

**Phase 6 API:** `src/api/routers/chat.py` calls `run_chat_turn`; SSE emits decision/orchestrator stages via `emit` in `RunnableConfig`.

---

## 2. Two state types

We **intentionally** use two TypedDicts — clearer split than a single `AgentState` for everything:

| State | File | Used by |
|-------|------|---------|
| `DecisionState` | `src/agents/decision_state.py` | Decision subgraph only |
| `AgentState` | `src/agents/state.py` | Orchestrator + full conversation |

**Why two states?**

- Classification needs only `message` + `router_context` (memory string).
- Orchestrator needs `messages`, `route_decisions`, `agent_outputs`, session ids, etc.
- Decision graph stays small, testable, and trace-friendly without SSE/MCP noise on minimal state.

Handoff from decision output to orchestrator input lives in **`decision_bridge.py`** (see §7).

---

## 3. Decision graph topology (BookMe AI)

```text
START
  ├── guardrail   (Guardrail.aclassify → in_scope | out_of_scope)
  ├── router      (QueryRouter.aroute → MultiRouteDecision)
          │ fan-in (LangGraph waits for ALL incoming edges)
          ▼
      decide        (guardrail OOS unless router chose hotel|flight|web_search; else proceed)
          ▼
         END
```

**Guardrail inputs:** latest `message` + **`router_context`** (formatted `SessionStore` history, same as router).

**Routes:** `hotel`, `flight`, `general_qa`, **`web_search`** (Tavily via MCP).

**Files:**

- `src/agents/decision_graph.py` — graph builder, nodes, optional SSE `emit` via `RunnableConfig`
- `src/agents/guardrail.py` — scope classifier, fail-open
- `src/agents/router.py` — `QueryRouter`, parse/normalize JSON routes

**Invoke:**

```python
await decision_graph.ainvoke({
    "message": user_text,
    "router_context": memory_context,
})
```

---

## 4. Parallel guardrail + router — runtime behavior

### 4.1 Both branches always start

Guardrail and router **do not** see each other’s results mid-flight. Each turn pays **two LLM calls** (guardrail model + router model) unless the graph is changed later.

### 4.2 Fan-in before `decide`

LangGraph runs `decide` only after **both** branches complete. Wall-clock to `decide` ≈ **max(guardrail_ms, route_ms)**, not the faster branch alone.

Example (typical rough numbers):

- Guardrail ~150 ms, router ~800 ms → user waits ~800 ms until `decide`, not ~150 ms.

### 4.3 Off-topic example: “Who is the president?”

| Time | What happens |
|------|----------------|
| t=0 | Guardrail + router LLM calls start |
| t≈150 | Guardrail → `out_of_scope`; **router still running** |
| t≈800 | Router finishes (may return e.g. `general_qa` — ignored for reply) |
| t≈800 | `decide` → `verdict=out_of_scope`, `final_answer=template` |

**Important:**

- Router does **not** “fail” because the question isn’t travel — it still emits JSON.
- **`decide` gates on guardrail only** for proceed vs out-of-scope.
- Router output is **discarded** for the user response (bridge does not set `route_decisions` on OOS).
- **No orchestrator / MCP / synthesis** on OOS — that is the meaningful “short-circuit.”

The chat handler returns the refusal after the **full decision graph** completes (both parallel branches).

### 4.4 Two meanings of “instant return”

| Meaning | BookMe AI? |
|---------|------------|
| **A — Product short-circuit** | Skip tools, orchestrator, synth → template answer | **Yes** |
| **B — HTTP at guardrail time, cancel router** | Response at ~150 ms, one LLM call | **No** (not implemented) |

Comments about “no router on OOS” in downstream code mean **no downstream tool path**, not that the router node was skipped inside the graph.

---

## 5. Router (BookMe AI domain)

**Valid routes:** `hotel` | `flight` | `general_qa` | `web_search`

**Valid actions:** `search` | `list_all` | `book` | `general`

**Outputs:** `MultiRouteDecision` on `DecisionState.decision`; bridge converts to `AgentState.route_decisions` (list of dicts).

**Two entry points (by design):**

| Entry | State | Use |
|-------|-------|-----|
| `QueryRouter.aroute` in decision graph | `DecisionState` | Primary chat path |
| `router_node` in `router.py` | `AgentState` | Optional orchestrator graph / alternate wiring |

**Prompts:** `build_router_prompt()` = LangFuse/base system + LangFuse hard rules + user template.

---

## 6. Guardrail

- Binary: `in_scope` | `out_of_scope`
- **Fail open** on LLM/parse errors → `in_scope`
- Refusal copy: `get_out_of_scope_reply()` (LangFuse + fallback)
- LLM: `get_guardrail_llm()` (role from `config/models.yaml`)

---

## 7. Bridge module (`decision_bridge.py`)

Explicit handoff from decision subgraph output to orchestrator input.

`map_decision_to_agent_state(decision_out, messages=..., memory_context=..., user_id=..., session_id=...)`:

- Always: `guardrail`, `verdict`, session fields, `messages`
- If `verdict == out_of_scope`: `final_answer` only (no `route_decisions`)
- If `verdict == proceed`: `route_decisions` from `asdict(decision.decisions)`

**Chat flow:**

1. `decision_out = await decision_graph.ainvoke(...)`
2. `patch = map_decision_to_agent_state(decision_out, ...)`
3. If OOS → return `patch["final_answer"]`
4. Else → `await orchestrator.ainvoke({**patch, ...})`

---

## 8. BookMe AI design choices

- **Parallel classifiers** from `START`, fan-in to `decide` (guardrail + router only — no FAQ cache branch).
- **`decide` verdicts:** `out_of_scope` | `proceed`.
- **Travel routes:** `hotel`, `flight`, `general_qa`, `web_search` with actions `search`, `list_all`, `book`, `general`.
- **Tools:** Convex HTTP hotels/flights via MCP stdio servers; Tavily for web search.
- **Bridge:** dedicated `decision_bridge.py` module (not inlined in the chat router).
- **OOS:** no orchestrator/tools; downstream prep tasks in chat may be cancelled once verdict is known.

**Viva one-liner:**

> Two-state decision subgraph with parallel guardrail and router fan-in; travel MCP behind orchestrator agents; explicit bridge into `AgentState`.

---

## 9. Latency vs cost — engineering tradeoffs

### 9.1 What current design optimizes

- **In-scope latency:** ≈ max(guardrail, router), not sum
- **Downstream cost:** OOS skips orchestrator, MCP, synthesis
- **Sacrifices:** Router LLM on off-topic; wall-clock OOS ≈ router time, not guardrail alone

### 9.2 Alternatives (if requirements change)

| Approach | Latency (in-scope) | Cost (off-topic) | Notes |
|----------|-------------------|------------------|-------|
| **Parallel guardrail + router (current)** | Best | Higher (2 LLMs) | Default for this project |
| **Sequential guardrail → router** | Slower in-scope | Lower off-topic (1 LLM) | Simple graph change |
| **Single LLM scope + routes** | One call | Lowest calls | Harder prompts, weaker separation |
| **Rules pre-filter + LLM guardrail** | Medium | Medium | Obvious junk without LLM |
| **Faster/smaller guardrail model** | Slightly better parallel floor | Same 2 calls | e.g. Groq 8B on guardrail role |
| **FAQ / response cache after graph** | Saves synth after graph | Still pays router in graph | Only if FAQ volume justifies it |

**Recommendation:** Keep parallel graph for assessment demo; measure traffic in production; consider sequential guardrail→router only if off-topic volume dominates cost.

---

## 10. Phase 4–6 status & acceptance

**Phase 4 — decision graph ✅**

- Deliverables: `guardrail.py`, `router.py`, `decision_state.py`, `decision_graph.py`, `decision_bridge.py`
- `make test-decision`

**Acceptance:**

1. Off-topic → `verdict=out_of_scope`
2. Hotel + flight in one message → `proceed`, ≥2 routes
3. Tourism / food in a destination → router `web_search`; guardrail should not block when router selects a tool route (see `decide_node` override)

**Phase 5 — orchestrator ✅**

- `orchestrator.py`, `build_agent_mcp()`, four agent nodes + merge
- `make test-orchestrator`, `make test-orchestrator-web-search`

**Phase 6 — API ✅**

- `src/api/*`, `chat_pipeline.py`, `make run-api`
- Optional: production Clerk-only auth; HTTP tests

**Session memory (not LangGraph checkpointer):**

- `SessionStore` keyed by `(user_id, session_id)`
- `session.history_window` in `params.yaml` = how many **(user, assistant) pairs** are injected as `router_context` each turn
- `session.max_turns` = rolling storage cap (in-memory; lost on API restart)

---

## 11. Repository map (agents + API)

```text
src/agents/
  chat_pipeline.py     run_chat_turn
  decision_state.py    DecisionState
  decision_graph.py    LangGraph compile + nodes
  decision_bridge.py   map_decision_to_agent_state()
  guardrail.py
  router.py            QueryRouter
  orchestrator.py
  state.py             AgentState
  prompts/agent_prompts.py
src/api/
  main.py, routers/chat.py, ...
src/infrastructure/
  session_store.py, observability.py
```

---

*Last updated: 2026-07-28 — Phases 4–6 complete; web_search + SessionStore documented.*
