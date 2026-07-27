#!/usr/bin/env python3
"""Acceptance checks for SessionStore composite (user_id, session_id) keys."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(ROOT))

from infrastructure.session_store import SessionStore  # noqa: E402


def main() -> int:
    store = SessionStore()
    shared_session = "thread-abc"

    store.add_exchange("user-a", shared_session, "book hotel", "Sure, which city?")
    store.add_exchange("user-b", shared_session, "book flight", "Where to?")

    pairs_a = store.recent_pairs("user-a", shared_session)
    pairs_b = store.recent_pairs("user-b", shared_session)

    assert pairs_a == [("book hotel", "Sure, which city?")], pairs_a
    assert pairs_b == [("book flight", "Where to?")], pairs_b

    store.add_exchange("user-a", shared_session, "Colombo", "Searching Colombo hotels…")
    assert len(store.recent_pairs("user-a", shared_session)) == 2
    assert len(store.recent_pairs("user-b", shared_session)) == 1

    flat = store.history_messages("user-a", shared_session, k=1)
    assert flat == ["Colombo", "Searching Colombo hotels…"], flat

    store.reset("user-a", shared_session)
    assert store.recent_pairs("user-a", shared_session) == []
    assert store.recent_pairs("user-b", shared_session) == pairs_b

    print("SessionStore composite-key checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
