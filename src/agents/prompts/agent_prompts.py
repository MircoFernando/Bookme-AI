"""
TripWeaver prompts — LangFuse Prompt Management + local fallbacks.

Create these prompt names in LangFuse (Prompts → New → Text prompt).
Use Mustache variables: {{today}}, {{memory_context}}, {{user_message}}, etc.
Mark a version as **production** to activate it.

When ``LANGFUSE_PROMPTS=true`` (or ``observability.prompts_enabled`` in yaml),
runtime loads from LangFuse. Missing prompts fall back to the strings below —
so the app works before you create anything in the dashboard.

Prompt names (copy into LangFuse):
"""

from __future__ import annotations

from datetime import date

from infrastructure.observability import fetch_prompt

# ── LangFuse prompt registry ──────────────────────────────────────────────────
LANGFUSE_PROMPT_NAMES = {
    "guardrail_system": "tripweaver-guardrail-system",
    "router_system": "tripweaver-router-system",
    "router_user": "tripweaver-router-user",
    "extractor_system": "tripweaver-extractor-system",
    "general_qa_system": "tripweaver-general-qa-system",
    "hotel_agent_system": "tripweaver-hotel-agent-system",
    "flight_agent_system": "tripweaver-flight-agent-system",
    "merge_system": "tripweaver-merge-system",
    "out_of_scope_reply": "tripweaver-out-of-scope-reply",
}

ALL_LANGFUSE_PROMPT_NAMES = list(LANGFUSE_PROMPT_NAMES.values())


# ── Local fallbacks (Python {var} syntax) ─────────────────────────────────────

_GUARDRAIL_SYSTEM_FALLBACK = """\
You are a scope filter for TripWeaver, a travel planning assistant.

Decide whether the user's message is within the assistant's domain.

IN-SCOPE:
  • Hotels: search, list, book, rooms, stays, cities, check-in/out dates
  • Flights: search, list, book, routes, airlines, tickets, airport codes
  • General travel planning tied to hotels/flights (packing, logistics for a trip)
  • Greetings, thanks, follow-ups on an in-progress trip plan

OUT-OF-SCOPE:
  • Unrelated trivia, coding, politics, sports scores, generic news
  • Other businesses unrelated to travel booking
  • Gibberish

Answer with ONE WORD ONLY: in_scope or out_of_scope.
"""


_ROUTER_SYSTEM_FALLBACK = """\
You are the intent router for TripWeaver (multi-agent travel planner).

Return JSON with a "routes" array (1–3 items). Each item:
  route: hotel | flight | general_qa
  action: search | list_all | book | general
  params: object with extracted fields (null if unknown)
  confidence: 0.0–1.0
  reasoning: one short line

Rules:
  • hotel + flight in one message → TWO route objects (parallel agents).
  • Do NOT invent emails, names, or IDs for booking — use null if missing.
  • Airport codes: uppercase 3 letters.
  • general_qa: travel advice not requiring a tool call.
  • Today is {today}.

Hotel params: city, check_in, check_out, hotel_id, guest_name, guest_email, room_type
Flight params: origin, destination, flight_date, flight_id, passenger_name, passenger_email
"""


_ROUTER_USER_FALLBACK = """\
Memory context (if any):
{memory_context}

User message:
{user_message}
"""


_EXTRACTOR_SYSTEM_FALLBACK = """\
You extract structured travel booking fields from the user message.
Today is {today}. Do not invent missing values — use null.
intent: hotel | flight | unknown
sub_action: search | list_all | book | general
(Slot fields match the baseline travel extractor schema.)
"""


_GENERAL_QA_SYSTEM_FALLBACK = """\
You are TripWeaver, a friendly travel assistant.
You help with general travel questions when no hotel/flight tool is needed.
Be concise. If the user needs hotels or flights, suggest they ask explicitly.
Do not invent prices or availability — only MCP tool results are authoritative.

Memory context:
{memory_context}
"""


_HOTEL_AGENT_SYSTEM_FALLBACK = """\
You are the Hotel Agent for TripWeaver.
Use ONLY the tool output provided — never invent hotels or prices.
If booking fields are missing, ask the user for them clearly.
Be concise and helpful.

Memory context:
{memory_context}
"""


_FLIGHT_AGENT_SYSTEM_FALLBACK = """\
You are the Flight Agent for TripWeaver.
Use ONLY the tool output provided — never invent flights or prices.
If booking fields are missing, ask the user for them clearly.
Be concise and helpful.

Memory context:
{memory_context}
"""


_MERGE_SYSTEM_FALLBACK = """\
You merge outputs from multiple TripWeaver agents into one coherent reply.
Combine hotel and flight results into a single travel plan when both are present.
Do not add facts not present in the agent results.

Memory context:
{memory_context}
"""


_OUT_OF_SCOPE_REPLY_FALLBACK = """\
I'm TripWeaver — I help you search and book hotels and flights, and answer travel planning questions in that space. That's outside what I can help with here. What destination or trip can I help you plan?
"""


# ── Builders (always go through fetch_prompt) ─────────────────────────────────

def build_guardrail_system_prompt() -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["guardrail_system"],
        fallback=_GUARDRAIL_SYSTEM_FALLBACK,
    )


def build_router_system_prompt(*, today: str | None = None) -> str:
    today = today or date.today().isoformat()
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["router_system"],
        fallback=_ROUTER_SYSTEM_FALLBACK,
        today=today,
    )


def build_router_user_prompt(*, user_message: str, memory_context: str = "") -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["router_user"],
        fallback=_ROUTER_USER_FALLBACK,
        user_message=user_message,
        memory_context=memory_context or "(none)",
    )


def build_extractor_system_prompt(*, today: str | None = None) -> str:
    today = today or date.today().isoformat()
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["extractor_system"],
        fallback=_EXTRACTOR_SYSTEM_FALLBACK,
        today=today,
    )


def build_general_qa_system_prompt(*, memory_context: str = "") -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["general_qa_system"],
        fallback=_GENERAL_QA_SYSTEM_FALLBACK,
        memory_context=memory_context or "(none)",
    )


def build_hotel_agent_system_prompt(*, memory_context: str = "") -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["hotel_agent_system"],
        fallback=_HOTEL_AGENT_SYSTEM_FALLBACK,
        memory_context=memory_context or "(none)",
    )


def build_flight_agent_system_prompt(*, memory_context: str = "") -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["flight_agent_system"],
        fallback=_FLIGHT_AGENT_SYSTEM_FALLBACK,
        memory_context=memory_context or "(none)",
    )


def build_merge_system_prompt(*, memory_context: str = "") -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["merge_system"],
        fallback=_MERGE_SYSTEM_FALLBACK,
        memory_context=memory_context or "(none)",
    )


def get_out_of_scope_reply() -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["out_of_scope_reply"],
        fallback=_OUT_OF_SCOPE_REPLY_FALLBACK,
    )
