"""
Friendly labels for streaming chain-of-thought events.

Maps internal stage / tool identifiers to user-facing copy (Week 13 pattern).
"""

from __future__ import annotations

from typing import Optional, Tuple


STAGE_LABELS: dict[str, str] = {
    "decision": "Classifying your request…",
    "guardrail": "Checking this is travel-related…",
    "route": "Choosing hotel, flight, or search…",
    "orchestrator": "Running travel agents…",
    "save": "Saving the conversation…",
}

_TOOL_LABELS: dict[Tuple[str, Optional[str]], str] = {
    ("hotel", "search"): "Searching hotels…",
    ("hotel", "list"): "Listing hotels…",
    ("hotel", "book"): "Booking a hotel…",
    ("flight", "search"): "Searching flights…",
    ("flight", "list"): "Listing flights…",
    ("flight", "book"): "Booking a flight…",
    ("web_search", "search"): "Searching live web (Tavily)…",
    ("general_qa", None): "Answering your question…",
    ("out_of_scope", None): "Outside travel planning scope",
    ("multi", None): "Running multiple travel agents…",
}


def stage_label(stage: str) -> str:
    return STAGE_LABELS.get(stage, stage.replace("_", " ").capitalize())


def tool_label(route: str, action: Optional[str] = None) -> str:
    return (
        _TOOL_LABELS.get((route, action))
        or _TOOL_LABELS.get((route, None))
        or f"Running {route}{' / ' + action if action else ''}"
    )
