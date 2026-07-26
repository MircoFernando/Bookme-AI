"""
Per-session conversation memory — kills the global-history bug.

The baseline kept a single module-level ``conversation_history_messages = []``
shared across every caller: concurrent users clobbered each other's context.

``SessionStore`` replaces that with a thread-safe, per-``session_id`` rolling
window of turns. The API creates one ``SessionStore`` at startup and stores it
on ``app.state``; each request reads/writes only its own session's history.

This is deliberately in-memory (fine for a single-process deployment and the
assessment demo). Swapping in Redis later means implementing the same three
methods — ``add_turn`` / ``recent_pairs`` / ``reset`` — with no call-site
changes, mirroring the Week 13 decoupling philosophy.
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
    role: str        # "user" | "assistant"
    content: str


class SessionStore:
    """Thread-safe, per-session rolling conversation history."""

    def __init__(self, max_turns: int = SESSION_MAX_TURNS) -> None:
        self._max_turns = max_turns
        self._lock = threading.Lock()
        self._sessions: Dict[str, Deque[Turn]] = defaultdict(
            lambda: deque(maxlen=self._max_turns)
        )

    def add_turn(self, session_id: str, role: str, content: str) -> None:
        """Append a turn to a session's history (bounded window)."""
        with self._lock:
            self._sessions[session_id].append(Turn(role=role, content=content))

    def add_exchange(self, session_id: str, user_msg: str, assistant_msg: str) -> None:
        """Append a (user, assistant) pair atomically."""
        with self._lock:
            dq = self._sessions[session_id]
            dq.append(Turn(role="user", content=user_msg))
            dq.append(Turn(role="assistant", content=assistant_msg))

    def recent_pairs(self, session_id: str, k: int = SESSION_HISTORY_WINDOW) -> List[Tuple[str, str]]:
        """Return up to the last ``k`` (user, assistant) pairs for a session."""
        with self._lock:
            turns = list(self._sessions.get(session_id, ()))
        pairs: List[Tuple[str, str]] = []
        i = 0
        while i < len(turns) - 1:
            if turns[i].role == "user" and turns[i + 1].role == "assistant":
                pairs.append((turns[i].content, turns[i + 1].content))
                i += 2
            else:
                i += 1
        return pairs[-k:] if k else pairs

    def history_messages(self, session_id: str, k: int = SESSION_HISTORY_WINDOW) -> List[str]:
        """Flatten recent pairs into a ``[user, assistant, user, ...]`` list."""
        flat: List[str] = []
        for user_msg, assistant_msg in self.recent_pairs(session_id, k):
            flat.append(user_msg)
            flat.append(assistant_msg)
        return flat

    def reset(self, session_id: str) -> None:
        """Clear a single session's history."""
        with self._lock:
            self._sessions.pop(session_id, None)

    def sessions(self) -> int:
        """Number of active sessions (debug/health)."""
        with self._lock:
            return len(self._sessions)
