"""
Domain Guardrail — BookMe AI scope filter for the decision subgraph.

Binary classifier used by ``decision_graph`` (``DecisionState``), not the
orchestrator ``AgentState``. Fails open on LLM errors.
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from loguru import logger

from agents.prompts import build_guardrail_system_prompt, get_out_of_scope_reply
from infrastructure.llm import get_guardrail_llm
from infrastructure.observability import observe, update_current_observation

GuardrailVerdict = Literal["in_scope", "out_of_scope"]

_default_guardrail: Optional["Guardrail"] = None


# Few-shot examples baked into the user-prompt template — keeps small
# router/guardrail models honest without a separate fine-tune.
_GUARDRAIL_EXAMPLES = """\
Examples:
  USER: "Find hotels in Colombo check-in Aug 10"     → in_scope
  USER: "Flights from Mumbai to Delhi tomorrow"     → in_scope
  USER: "Book hotel H-42 for Jane jane@example.com"  → in_scope
  USER: "What should I pack for Sri Lanka in monsoon?" → in_scope
  USER: "Best food and restaurants in London?"        → in_scope
  USER: "Where should I eat in Paris on a budget?"      → in_scope
  USER: "Top things to do in Tokyo for 3 days"         → in_scope
  USER: "Tourist attractions in England"               → in_scope
  USER: "Hey, I'm planning a trip"                  → in_scope
  USER: "Thanks, that helps"                         → in_scope
  USER: "What is my name?" (recent chat: user said they are Mirco, planning London) → in_scope
  USER: "What destination were we talking about?" (recent chat mentions London trip) → in_scope
  USER: "Who is the president of the USA?"           → out_of_scope
  USER: "What's the capital of France?"             → out_of_scope
  USER: "Write me a Python function"                → out_of_scope
  USER: "Who won the cricket match yesterday?"      → out_of_scope
  USER: "asdfghjkl"                                 → out_of_scope
"""

_MEMORY_CONTEXT_MAX = 2000


def _build_user_prompt(message: str, memory_context: str = "") -> str:
    parts = [_GUARDRAIL_EXAMPLES]
    ctx = (memory_context or "").strip()
    if ctx:
        if len(ctx) > _MEMORY_CONTEXT_MAX:
            ctx = "…" + ctx[-_MEMORY_CONTEXT_MAX:]
        parts.append("\nRecent conversation (use for follow-up scope only):\n")
        parts.append(ctx)
        parts.append("\n")
    parts.append(f'USER: "{(message or "").strip()}"\n→')
    return "".join(parts)


class Guardrail:
    """Binary in_scope / out_of_scope classifier."""

    def __init__(self, llm: Any) -> None:
        self.llm = llm

    @observe(name="guardrail", as_type="generation")
    async def aclassify(
        self,
        message: str,
        memory_context: str = "",
    ) -> GuardrailVerdict:
        """Classify *message* as ``in_scope`` or ``out_of_scope``.

        *memory_context* is the same short-term thread the router sees so
        follow-ups ("what is my name?", "what city did I mention?") stay
        in scope during an active travel conversation.

        Fails open: any LLM error returns ``in_scope`` so transient
        provider issues don't lock real users out of the assistant.
        """
        msgs = [
            {"role": "system", "content": build_guardrail_system_prompt()},
            {
                "role": "user",
                "content": _build_user_prompt(message, memory_context),
            },
        ]
        try:
            response = await self.llm.ainvoke(msgs)
        except Exception as exc:
            logger.warning("Guardrail LLM error (failing open): {}", exc)
            return "in_scope"

        raw = (
            response.content if hasattr(response, "content") else str(response)
        ).strip().lower()

        # Be permissive in parsing — the model occasionally adds quotes,
        # backticks, or trailing punctuation despite the instruction.
        verdict: GuardrailVerdict
        if "out_of_scope" in raw or "out-of-scope" in raw or "out of scope" in raw:
            verdict = "out_of_scope"
        elif "in_scope" in raw or "in-scope" in raw or "in scope" in raw:
            verdict = "in_scope"
        else:
            # Unrecognised response — safest default is to let the
            # normal pipeline handle it.
            logger.debug("Guardrail unparsable response {!r} → defaulting in_scope", raw[:50])
            verdict = "in_scope"

        update_current_observation(
            input=(message or "")[:200],
            output=verdict,
        )
        return verdict


def get_guardrail() -> Guardrail:
    global _default_guardrail
    if _default_guardrail is None:
        _default_guardrail = Guardrail(get_guardrail_llm())
    return _default_guardrail


# Polite refusal when guardrail returns out_of_scope (LangFuse + local fallback).
OUT_OF_SCOPE_REPLY = get_out_of_scope_reply()
