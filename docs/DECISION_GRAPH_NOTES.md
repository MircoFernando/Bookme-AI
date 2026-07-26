# Decision graph & routing — architecture notes

**Purpose:** Design log for Phase 4 (guardrail, router, decision graph, bridge). Captures engineering discussions, Week 13 parity, latency/cost tradeoffs, and viva talking points.

**Reference codebase:** Week 13 Nawaloka at `Documents/projects/Week 13` (verified 2026-07-26).

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
DecisionState  ── decision_graph (guardrail ∥ router → decide)
     │
     ▼
decision_bridge.map_decision_to_agent_state()
     │
     ▼
AgentState  ── orchestrator (Phase 5) → MCP → final_answer
```

---

## 2. Week 13 architecture choice (two state types)

We **intentionally** use two TypedDicts (same pattern as Week 13, clearer split than a single `AgentState` for everything):

| State | File | Used by |
|-------|------|---------|
| `DecisionState` | `src/agents/decision_state.py` | Decision subgraph only |
| `AgentState` | `src/agents/state.py` | Orchestrator + full conversation |

**Why two states?**

- Classification needs only `message` + `router_context` (memory string).
- Orchestrator needs `messages`, `route_decisions`, `agent_outputs`, session ids, etc.
- Decision graph stays small, testable, and trace-friendly without SSE/MCP noise on minimal state.

**Week 13** keeps the same split; handoff logic lives in `api/routers/chat.py`. **BookMe AI** extracts handoff to `decision_bridge.py` (same behavior, named module — see §7).

---

## 3. Decision graph topology (BookMe AI)

```text
START
  ├── guardrail   (Guardrail.aclassify → in_scope | out_of_scope)
  ├── router      (QueryRouter.aroute → MultiRouteDecision)
          │ fan-in (LangGraph waits for ALL incoming edges)
          ▼
      decide        (verdict from guardrail only; final_answer if OOS)
          ▼
         END
```

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

Week 13 **does the same** for the decision graph (see §8). Chat then returns refusal after `await decision_graph_task` completes.

### 4.4 Two meanings of “instant return”

| Meaning | BookMe AI / Week 13? |
|---------|------------------------|
| **A — Product short-circuit** | Skip tools, orchestrator, synth → template or cache answer | **Yes** |
| **B — HTTP at guardrail time, cancel router** | Response at ~150 ms, one LLM call | **No** (not implemented) |

Week 13 `chat.py` comments saying “no router LLM” on OOS mean **no downstream tool path**, not that the router node was skipped inside the graph.

---

## 5. Router (BookMe AI domain)

**Valid routes:** `hotel` | `flight` | `general_qa`

**Valid actions:** `search` | `list_all` | `book` | `general`

**Outputs:** `MultiRouteDecision` on `DecisionState.decision`; bridge converts to `AgentState.route_decisions` (list of dicts).

**Two entry points (by design):**

| Entry | State | Use |
|-------|-------|-----|
| `QueryRouter.aroute` in decision graph | `DecisionState` | Week 13 path |
| `router_node` in `router.py` | `AgentState` | Optional orchestrator graph / alternate wiring |

**Prompts:** `build_router_prompt()` = LangFuse/base system + `_ROUTER_HARD_RULES_TEMPLATE` + user template.

---

## 6. Guardrail

- Binary: `in_scope` | `out_of_scope`
- **Fail open** on LLM/parse errors → `in_scope`
- Refusal copy: `get_out_of_scope_reply()` (LangFuse + fallback)
- LLM: `get_guardrail_llm()` (role from `config/models.yaml`)

---

## 7. Bridge module (`decision_bridge.py`)

**Not a new layer** — explicit handoff Week 13 performs inside `chat.py`.

`map_decision_to_agent_state(decision_out, messages=..., memory_context=..., user_id=..., session_id=...)`:

- Always: `guardrail`, `verdict`, session fields, `messages`
- If `verdict == out_of_scope`: `final_answer` only (no `route_decisions`)
- If `verdict == proceed`: `route_decisions` from `asdict(decision.decisions)`

**Phase 6 chat flow (planned):**

1. `decision_out = await decision_graph.ainvoke(...)`
2. `patch = map_decision_to_agent_state(decision_out, ...)`
3. If OOS → return `patch["final_answer"]`
4. Else → `await orchestrator.ainvoke({**patch, ...})`

---

## 8. Week 13 vs BookMe AI (exact differences)

### 8.1 Same

- Parallel classifiers from `START`, fan-in to `decide`
- Full graph awaited before chat short-circuit
- Guardrail fail-open; multi-route router; MCP behind agents (Week 13 built, BookMe AI Phase 5)
- LangFuse prompts; `@observe` on LLM nodes
- OOS: no orchestrator/tools; cancel parallel **prep** tasks in chat (patient/recall in Week 13)

### 8.2 Different — decision subgraph

| | Week 13 | BookMe AI |
|---|---------|------------|
| Parallel branches | guardrail + router + **CAG** | guardrail + router |
| `decide` verdicts | `out_of_scope` \| **`cache_hit`** \| `proceed` | `out_of_scope` \| `proceed` |
| CAG gate | `cag_hit` + route ∈ `{rag, direct}` | N/A |

**CAG + cache:** Even when CAG hits in ~300 ms, Week 13 still **waits for router** (~800 ms) before `decide` and before returning cached FAQ — router route gates cache eligibility (prevents CRM questions matching generic FAQ).

Verified in Week 13:

- `src/agents/decision_graph.py` — three edges into `decide`; docstring “LangGraph waits for all three”
- `src/api/routers/chat.py` — `await decision_graph_task` then OOS / `cache_eligible` checks; “route already awaited above”

### 8.3 Different — routing domain

| Week 13 | BookMe AI |
|---------|------------|
| `crm`, `rag`, `web_search`, `direct` | `hotel`, `flight`, `general_qa` |
| CRM actions (bookings, doctors, …) | `search`, `list_all`, `book`, `general` |
| Router fallback `direct` | Fallback `general_qa` |

### 8.4 Different — tools & infra

| Week 13 | BookMe AI |
|---------|------------|
| Supabase CRM, Qdrant RAG, web, CAG MCP | Convex HTTP hotels/flights |
| MCP: crm, rag, web, cag, … | MCP: `bookme-ai-hotels`, `bookme-ai-flights` |
| `src/api/routers/chat.py` live | Phase 6 ⏳ |
| `orchestrator.py` live | Phase 5 ⏳ |
| Bridge in chat | `decision_bridge.py` |

### 8.5 Viva one-liner

> We kept Week 13’s two-state decision subgraph and parallel fan-in; we removed CAG and hospital routes, added Convex travel MCP, explicit bridge, and will wire chat + orchestrator in Phases 5–6.

---

## 9. Latency vs cost — engineering tradeoffs

### 9.1 What current design optimizes

- **In-scope latency:** ≈ max(guardrail, router), not sum
- **Downstream cost:** OOS skips orchestrator, MCP, synthesis
- **Sacrifices:** Router LLM on off-topic; wall-clock OOS ≈ router time, not guardrail alone

### 9.2 Alternatives (if requirements change)

| Approach | Latency (in-scope) | Cost (off-topic) | Notes |
|----------|-------------------|------------------|-------|
| **Parallel guardrail + router (current)** | Best | Higher (2 LLMs) | Week 13 aligned |
| **Sequential guardrail → router** | Slower in-scope | Lower off-topic (1 LLM) | Simple graph change |
| **Single LLM scope + routes** | One call | Lowest calls | Harder prompts, weaker separation |
| **Rules pre-filter + LLM guardrail** | Medium | Medium | Obvious junk without LLM |
| **Faster/smaller guardrail model** | Slightly better parallel floor | Same 2 calls | Groq 8B on guardrail (Week 13 style) |
| **Add CAG (Week 13)** | Saves synth/RAG after graph | Still pays router in graph | FAQ-heavy products |

**Recommendation for assessment:** Keep parallel graph for Week 13 parity; measure traffic in production; consider sequential guardrail→router only if off-topic volume dominates cost.

---

## 10. Phase 4 status & acceptance

**Deliverables:**

- `guardrail.py`, `router.py`, `decision_state.py`, `decision_graph.py`, `decision_bridge.py`
- `scripts/test_decision_graph.py` — `make test-decision` (requires `OPENAI_API_KEY`)

**Acceptance:**

1. “What is the capital of France?” → `verdict=out_of_scope`, `final_answer` set
2. “Hotels in X and flight A→B” → `verdict=proceed`, ≥2 routes (`hotel`, `flight`)

**Remaining after Phase 4:**

- Phase 5: `orchestrator.py`, hotel/flight/general_qa agents, MCP adapters, merge
- Phase 6: FastAPI chat (mirror Week 13: await graph, OOS return, parallel session recall + cancel on OOS)

---

## 11. Repository map (Phase 4 agents)

```text
src/agents/
  decision_state.py    DecisionState
  decision_graph.py    LangGraph compile + nodes
  decision_bridge.py   map_decision_to_agent_state()
  guardrail.py
  router.py            QueryRouter + optional router_node(AgentState)
  state.py             AgentState (orchestrator)
  prompts/agent_prompts.py
```

---

## 12. Questions for Week 13 / instructor (optional prompt)

> In Week 13, decision graph runs guardrail, router, and CAG in parallel with fan-in to `decide`. For (1) guardrail `out_of_scope` and (2) CAG cache hit, does the API always await the full graph including router before responding? Is the router ever cancelled mid-flight, or only downstream tasks (patient/ST recall)? Please cite `decision_graph.py` and `chat.py`.

---

*Last updated: 2026-07-26 — synced with implementation on branch feat/decision-graph / MCP work.*
