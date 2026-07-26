"""
Domain Guardrail — BookMe AI scope filter (Week 13 decision subgraph).

Binary classifier used by ``decision_graph`` (``DecisionState``), not the
orchestrator ``AgentState``. Fails open on LLM errors.
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from loguru import logger

from agents.prompts import get_out_of_scope_reply
from infrastructure.llm import get_guardrail_llm
from infrastructure.observability import observe, update_current_observation

GuardrailVerdict = Literal["in_scope", "out_of_scope"]

_default_guardrail: Optional["Guardrail"] = None


_GUARDRAIL_SYSTEM = """\
You are a scope filter for BookMe AI, a multi-agent travel planning assistant.

Decide whether the user's message is within the assistant's domain.

IN-SCOPE — the assistant should help with:
  • Hotels: search, list, book, rooms, stays, cities, check-in/out dates
  • Flights: search, list, book, routes, airlines, tickets, airport codes
  • Trip planning tied to hotels or flights (itineraries, what to pack,
    visa/logistics for a trip, best time to visit a destination)
  • Weather or local info when clearly tied to planning a trip the user
    is discussing (not standalone trivia)
  • Greetings, thanks, small talk, follow-ups on an in-progress trip plan
    (the router and agents handle these)

OUT-OF-SCOPE — politely refuse:
  • General world knowledge (presidents, capitals, sports, history,
    celebrities, politics, science trivia)
  • Coding help, math homework, jokes, riddles, role-play unrelated to travel
  • Other businesses, products, or services unrelated to travel booking
  • Generic news, stock prices, sports scores with no travel intent
  • Gibberish or random non-questions
  • Anything you cannot tie to hotels, flights, or travel planning

Answer with ONE WORD ONLY: in_scope or out_of_scope.
No explanation, no punctuation, no other tokens.
"""


# Few-shot examples baked into the user-prompt template — keeps small
# router/guardrail models honest without a separate fine-tune.
_GUARDRAIL_EXAMPLES = """\
Examples:
  USER: "Find hotels in Colombo check-in Aug 10"     → in_scope
  USER: "Flights from Mumbai to Delhi tomorrow"     → in_scope
  USER: "Book hotel H-42 for Jane jane@example.com"  → in_scope
  USER: "What should I pack for Sri Lanka in monsoon?" → in_scope
  USER: "Hey, I'm planning a trip"                  → in_scope
  USER: "Thanks, that helps"                         → in_scope
  USER: "Who is the president of the USA?"           → out_of_scope
  USER: "What's the capital of France?"             → out_of_scope
  USER: "Write me a Python function"                → out_of_scope
  USER: "Who won the cricket match yesterday?"      → out_of_scope
  USER: "asdfghjkl"                                 → out_of_scope
"""


def _build_user_prompt(message: str) -> str:
    return f"{_GUARDRAIL_EXAMPLES}\n\nUSER: \"{(message or '').strip()}\"\n→"


class Guardrail:
    """Binary in_scope / out_of_scope classifier."""

    def __init__(self, llm: Any) -> None:
        self.llm = llm

    @observe(name="guardrail", as_type="generation")
    async def aclassify(self, message: str) -> GuardrailVerdict:
        """Classify *message* as ``in_scope`` or ``out_of_scope``.

        Fails open: any LLM error returns ``in_scope`` so transient
        provider issues don't lock real users out of the assistant.
        """
        msgs = [
            {"role": "system", "content": _GUARDRAIL_SYSTEM},
            {"role": "user", "content": _build_user_prompt(message)},
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
