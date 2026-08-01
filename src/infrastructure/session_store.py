"""
Per-session conversation memory — kills the global-history bug.

The baseline kept a single module-level ``conversation_history_messages = []``
shared across every caller: concurrent users clobbered each other's context.

``SessionStore`` replaces that with a thread-safe rolling window keyed by
``(user_id, session_id)``. The API creates one ``SessionStore`` at startup and
stores it on ``app.state``; each request reads/writes only its own thread.

This is deliberately in-memory (fine for a single-process deployment and the
assessment demo). Swapping in Redis later means implementing the same methods
with no call-site changes.
"""

from __future__ import annotations

import threading
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Tuple

from infrastructure.config import SESSION_HISTORY_WINDOW, SESSION_MAX_TURNS


@dataclass
class Turn:
    """A single conversation turn."""

    role: str  # "user" | "assistant"
    content: str


def _session_key(user_id: str, session_id: str) -> str:
    """Stable composite key; isolates threads per authenticated user."""
    return f"{user_id}:{session_id}"


class SessionStore:
    """Thread-safe, per-(user, session) rolling conversation history."""

    def __init__(self, max_turns: int = SESSION_MAX_TURNS) -> None:
        self._max_turns = max_turns
        self._lock = threading.Lock()
        self._sessions: Dict[str, Deque[Turn]] = defaultdict(
            lambda: deque(maxlen=self._max_turns)
        )
        self._flight_inventory: Dict[str, List[dict]] = defaultdict(list)
        self._hotel_inventory: Dict[str, List[dict]] = defaultdict(list)

    def add_turn(
        self, user_id: str, session_id: str, role: str, content: str
    ) -> None:
        """Append a turn to a session's history (bounded window)."""
        key = _session_key(user_id, session_id)
        with self._lock:
            self._sessions[key].append(Turn(role=role, content=content))

    def add_exchange(
        self, user_id: str, session_id: str, user_msg: str, assistant_msg: str
    ) -> None:
        """Append a (user, assistant) pair atomically."""
        key = _session_key(user_id, session_id)
        with self._lock:
            dq = self._sessions[key]
            dq.append(Turn(role="user", content=user_msg))
            dq.append(Turn(role="assistant", content=assistant_msg))

    def recent_pairs(
        self,
        user_id: str,
        session_id: str,
        k: int = SESSION_HISTORY_WINDOW,
    ) -> List[Tuple[str, str]]:
        """Return up to the last ``k`` (user, assistant) pairs for a thread."""
        key = _session_key(user_id, session_id)
        with self._lock:
            turns = list(self._sessions.get(key, ()))
        pairs: List[Tuple[str, str]] = []
        i = 0
        while i < len(turns) - 1:
            if turns[i].role == "user" and turns[i + 1].role == "assistant":
                pairs.append((turns[i].content, turns[i + 1].content))
                i += 2
            else:
                i += 1
        return pairs[-k:] if k else pairs

    def history_messages(
        self,
        user_id: str,
        session_id: str,
        k: int = SESSION_HISTORY_WINDOW,
    ) -> List[str]:
        """Flatten recent pairs into a ``[user, assistant, user, ...]`` list."""
        flat: List[str] = []
        for user_msg, assistant_msg in self.recent_pairs(user_id, session_id, k):
            flat.append(user_msg)
            flat.append(assistant_msg)
        return flat

    def merge_flight_inventory(
        self, user_id: str, session_id: str, flights: List[dict]
    ) -> None:
        """Merge flight search/list results by ``_id`` for follow-up booking."""
        if not flights:
            return
        key = _session_key(user_id, session_id)
        with self._lock:
            by_id = {
                f["_id"]: f
                for f in self._flight_inventory[key]
                if isinstance(f, dict) and f.get("_id")
            }
            for flight in flights:
                if isinstance(flight, dict) and flight.get("_id"):
                    by_id[flight["_id"]] = flight
            self._flight_inventory[key] = list(by_id.values())

    def get_flight_inventory(
        self, user_id: str, session_id: str
    ) -> List[dict]:
        key = _session_key(user_id, session_id)
        with self._lock:
            return list(self._flight_inventory.get(key, []))

    def format_flight_inventory_for_memory(
        self, user_id: str, session_id: str
    ) -> str:
        """Compact catalog for router/agents (includes Convex ``flight_id``)."""
        flights = self.get_flight_inventory(user_id, session_id)
        if not flights:
            return ""
        lines = ["Last flight search (use flight_id when booking):"]
        for f in flights[:12]:
            fid = f.get("_id", "")
            fn = f.get("flightNumber", "")
            airline = f.get("airline", "")
            origin = f.get("origin") or {}
            dest = f.get("destination") or {}
            o = origin.get("airport") or origin.get("city") or "?"
            d = dest.get("airport") or dest.get("city") or "?"
            date = f.get("flightDate", "")
            lines.append(
                f"- flight_id={fid} | {fn} | {airline} | {o}→{d} | {date}"
            )
        return "\n".join(lines)

    def reset(self, user_id: str, session_id: str) -> None:
        """Clear a single thread's history."""
        key = _session_key(user_id, session_id)
        with self._lock:
            self._sessions.pop(key, None)
            self._flight_inventory.pop(key, None)
            self._hotel_inventory.pop(key, None)

    def sessions(self) -> int:
        """Number of active threads (debug/health)."""
        with self._lock:
            return len(self._sessions)
