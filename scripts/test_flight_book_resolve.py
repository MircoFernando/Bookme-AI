#!/usr/bin/env python3
"""Tests for flight_id resolution (flight number → Convex id)."""

from __future__ import annotations

import sys

sys.path.insert(0, "src")

from agents.tools.flight_tool import (  # noqa: E402
    FlightTool,
    _looks_like_convex_id,
    resolve_flight_id,
)
from infrastructure.session_store import SessionStore  # noqa: E402


SAMPLE = [
    {
        "_id": "k97bz5s0c4see2f7mc5e9t3r397rda66",
        "flightNumber": "CA2194",
        "airline": "Cathay Pacific",
        "origin": {"airport": "CGK", "city": "Jakarta"},
        "destination": {"airport": "DPS", "city": "Bali"},
        "flightDate": "2026-02-18",
    },
    {
        "_id": "k97other00000000000000000000000001",
        "flightNumber": "JA4179",
        "airline": "Japan Airlines",
        "origin": {"airport": "CGK", "city": "Jakarta"},
        "destination": {"airport": "DPS", "city": "Bali"},
        "flightDate": "2026-02-18",
    },
]


def test_convex_id_detection() -> None:
    assert _looks_like_convex_id("k97bz5s0c4see2f7mc5e9t3r397rda66")
    assert not _looks_like_convex_id("CA2194")


def test_resolve_from_candidate_flight_number() -> None:
    resolved, err = resolve_flight_id("CA2194", candidate_flights=SAMPLE)
    assert err is None
    assert resolved == "k97bz5s0c4see2f7mc5e9t3r397rda66"


def test_resolve_from_candidate_airline_label() -> None:
    resolved, err = resolve_flight_id("Cathay Pacific", candidate_flights=SAMPLE)
    assert err is None
    assert resolved == "k97bz5s0c4see2f7mc5e9t3r397rda66"


def test_session_inventory_memory_format() -> None:
    store = SessionStore()
    store.merge_flight_inventory("u1", "s1", SAMPLE)
    text = store.format_flight_inventory_for_memory("u1", "s1")
    assert "flight_id=k97bz5s0c4see2f7mc5e9t3r397rda66" in text
    assert "CA2194" in text
    store.reset("u1", "s1")
    assert store.format_flight_inventory_for_memory("u1", "s1") == ""


def test_book_with_flight_number_mock_candidates() -> None:
    """Integration: book by flight number when candidates supplied."""
    tool = FlightTool()
    result = tool.book_flight(
        flight_id="CA2194",
        passenger_name="Test User",
        passenger_email="test@example.com",
        candidate_flights=SAMPLE,
    )
    import json

    payload = json.loads(result)
    assert payload.get("ok") is True, payload
    booking = payload.get("booking") or {}
    inner = booking.get("booking") if isinstance(booking.get("booking"), dict) else booking
    assert inner.get("status") == "confirmed" or booking.get("success")


def main() -> int:
    test_convex_id_detection()
    test_resolve_from_candidate_flight_number()
    test_resolve_from_candidate_airline_label()
    test_session_inventory_memory_format()
    test_book_with_flight_number_mock_candidates()
    print("OK test_flight_book_resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
