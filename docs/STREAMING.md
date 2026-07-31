# Streaming — SSE progress + LLM token deltas

BookMe AI uses **one SSE connection** (`POST /chat/stream`) for both agent activity and token-by-token reply text.

---

## Event types

| Event | When | UI effect |
|-------|------|-----------|
| `stage_start` / `stage_done` | Decision graph, orchestrator | Chain-of-thought panel |
| `tool_invoke` / `tool_done` | MCP tool calls (when wired) | Tool rows in CoT |
| **`token_start`** | User-visible LLM synthesis begins | Empty assistant bubble |
| **`token_delta`** | Each streamed text chunk | Append to bubble |
| **`token_end`** | Synthesis LLM finished | (optional marker) |
| **`final`** | Turn complete | Attach route/meta; authoritative `answer` |
| `error` | Failure | Friendly error message |

Progress events fire **before** tokens. Tokens fire **only** for the answer the user reads—not for guardrail/router JSON.

---

## Where tokens are streamed (backend)

```text
run_chat_turn(emit=...)
  → decision_graph.ainvoke(..., config={ emit })     # stages only
  → orchestrator.arun_state(..., config={ emit })
       → [parallel agents — tools + ainvoke synthesis if multi-route]
       → merge_responses_node
```

| Turn shape | Token source | Agent LLM |
|------------|--------------|-----------|
| **Single route** (hotel, flight, general_qa, web_search) | Matching agent’s `_generate_agent_response` | **`astream`** via `_stream_llm_text` |
| **Multi route** (e.g. hotel + flight) | `merge_responses_node` only | Agents use **`ainvoke`** (hidden); merge uses **`astream`** |
| **Out of scope** | None | Template in `final` only |

Implementation: `src/agents/orchestrator.py`

- `_stream_llm_text` — `llm.astream(messages)` → emit `token_delta`
- `_synthesize_llm_text` — chooses stream vs `ainvoke` using `CHAT_STREAM_TOKENS`
- `_generate_agent_response` — streams when `len(route_decisions) <= 1`
- `merge_responses_node` — streams when `len(agent_outputs) > 1`

`emit` is passed through LangGraph `RunnableConfig`:

```python
config = {"configurable": {"emit": emit_fn}}
await orchestrator.arun_state(patch, config=config)
```

Same pattern as the decision graph in `chat_pipeline.py`.

---

## Configuration

`config/params.yaml`:

```yaml
chat:
  stream_tokens: true   # set false to disable token events (full answer in final only)
```

Loaded as `infrastructure.config.CHAT_STREAM_TOKENS`.

`POST /chat` (non-streaming) is unchanged—no token events.

---

## Frontend

`frontend/src/hooks/useChatStream.ts`:

1. `token_start` → push assistant message with `content: ""`
2. `token_delta` → append to that message
3. `final` → set full `answer` + metadata on the same message (source of truth)

Types: `frontend/src/types.ts` (`TokenStartEvent`, `TokenDeltaEvent`, `TokenEndEvent`).

---

## Disable token streaming

Set `chat.stream_tokens: false` in `params.yaml` and restart the API. SSE stage/tool events still work; the assistant message appears only on `final`.

---

## Viva talking points

- **One stream sink per turn** avoids parallel agents writing into the same bubble.
- **`final` always carries the complete answer** for session memory and metadata.
- Guardrail/router stay non-streaming—they output structured routing, not chat copy.

---

*Added: 2026-07-30 — single-route agent + multi-route merge token streaming.*
