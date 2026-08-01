"""
Flight tool — Convex flight API (list / search / book).

Same contract as ``HotelTool``: ``dispatch(action, params) -> JSON str``.
"""

from __future__ import annotations

import json
from typing import Any, Optional

from loguru import logger

from infrastructure.config import FLIGHTS_BASE_URL
from infrastructure.http_client import get_json, post_json
from infrastructure.observability import observe, update_current_observation


def _dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _extract_flights(data: Any) -> list:
    if isinstance(data, dict):
        raw = data.get("flights", [])
        return raw if isinstance(raw, list) else []
    if isinstance(data, list):
        return data
    return []


def _normalize_airport(value: str) -> str:
    v = (value or "").strip()
    if len(v) == 3 and v.isalpha():
        return v.upper()
    return v


def _normalize_flight_number(value: str) -> str:
    return (value or "").strip().upper().replace(" ", "")


def _looks_like_convex_id(value: str) -> bool:
    """True for Convex document ids (not display flight numbers like CA2194)."""
    v = (value or "").strip()
    return (
        len(v) >= 16
        and v.isalnum()
        and v[0].isalpha()
        and v.islower()
    )


def _flights_matching_number(flights: list, flight_number: str) -> list:
    needle = _normalize_flight_number(flight_number)
    if not needle:
        return []
    return [
        f
        for f in flights
        if isinstance(f, dict)
        and _normalize_flight_number(str(f.get("flightNumber", ""))) == needle
    ]


def _flights_matching_label(flights: list, label: str) -> list:
    """Match flight number or airline name substring (session inventory only)."""
    needle = (label or "").strip().lower()
    if not needle:
        return []
    matches: list = []
    for f in flights:
        if not isinstance(f, dict):
            continue
        fn = _normalize_flight_number(str(f.get("flightNumber", ""))).lower()
        airline = str(f.get("airline", "")).lower()
        if needle == fn or (len(needle) >= 4 and needle in airline):
            matches.append(f)
    return matches


def _dedupe_flights(flights: list) -> list:
    seen: set[str] = set()
    out: list = []
    for f in flights:
        if not isinstance(f, dict):
            continue
        fid = f.get("_id")
        if fid and fid not in seen:
            seen.add(fid)
            out.append(f)
    return out


def resolve_flight_id(
    flight_id: str,
    *,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    date: Optional[str] = None,
    candidate_flights: Optional[list] = None,
) -> tuple[Optional[str], Optional[str]]:
    """Resolve a Convex ``flight_id`` or display flight number / airline label."""
    return FlightTool()._resolve_flight_id(
        flight_id,
        origin=origin,
        destination=destination,
        date=date,
        candidate_flights=candidate_flights,
    )


class FlightTool:
    """Flight service actions routed by ``dispatch``."""

    VALID_ACTIONS = ("list_flights", "search_flights", "book_flight")

    @observe(name="flight_tool")
    def dispatch(self, action: str, params: Optional[dict] = None) -> str:
        params = params or {}
        update_current_observation(input=f"action={action} params={params}")

        handlers = {
            "list_flights": self.list_flights,
            "search_flights": self.search_flights,
            "book_flight": self.book_flight,
        }
        handler = handlers.get(action)
        if handler is None:
            return _dumps({
                "ok": False,
                "error": f"Unknown flight action: {action}",
                "code": "UNKNOWN_ACTION",
                "available": list(handlers.keys()),
            })

        try:
            result = handler(**self._clean_params(action, params))
            update_current_observation(output=result[:500] if len(result) > 500 else result)
            return result
        except TypeError as exc:
            logger.warning("FlightTool dispatch TypeError: {}", exc)
            return _dumps({
                "ok": False,
                "error": f"Invalid parameters for {action}: {exc}",
                "code": "VALIDATION",
            })
        except Exception as exc:
            logger.exception("FlightTool dispatch failed")
            return _dumps({
                "ok": False,
                "error": f"Flight service error: {exc}",
                "code": "INTERNAL",
            })

    @staticmethod
    def _clean_params(action: str, params: dict) -> dict:
        p = {k: v for k, v in params.items() if v is not None}
        if action == "book_flight":
            aliases = {
                "flightId": "flight_id",
                "passengerName": "passenger_name",
                "passengerEmail": "passenger_email",
                "flightNumber": "flight_id",
                "flight_number": "flight_id",
            }
            for src, dst in aliases.items():
                if src in p and dst not in p:
                    p[dst] = p.pop(src)
            if "flight_date" in p and "date" not in p:
                p["date"] = p.pop("flight_date")
        if action == "search_flights":
            if "flight_date" in p and "date" not in p:
                p["date"] = p.pop("flight_date")
        return p

    def list_flights(self) -> str:
        envelope = get_json(FLIGHTS_BASE_URL)
        if not envelope.get("ok"):
            return _dumps(envelope)
        flights = _extract_flights(envelope.get("data"))
        return _dumps({"ok": True, "flights": flights, "count": len(flights)})

    def search_flights(
        self,
        origin: str,
        destination: str,
        date: Optional[str] = None,
    ) -> str:
        if not origin or not destination:
            return _dumps({
                "ok": False,
                "error": "origin and destination are required to search flights",
                "code": "VALIDATION",
            })
        query: dict[str, str] = {
            "origin": _normalize_airport(str(origin)),
            "destination": _normalize_airport(str(destination)),
        }
        if date:
            query["date"] = date

        envelope = get_json(f"{FLIGHTS_BASE_URL}/search", params=query)
        if not envelope.get("ok"):
            return _dumps(envelope)
        flights = _extract_flights(envelope.get("data"))
        return _dumps({
            "ok": True,
            "flights": flights,
            "count": len(flights),
            "origin": query["origin"],
            "destination": query["destination"],
        })

    def _collect_flights_for_resolve(
        self,
        *,
        origin: Optional[str],
        destination: Optional[str],
        date: Optional[str],
        candidate_flights: Optional[list],
    ) -> list:
        pools: list = []
        if candidate_flights:
            pools.extend(candidate_flights)
        if origin and destination:
            raw = self.search_flights(origin, destination, date)
            try:
                payload = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                payload = {}
            if payload.get("ok"):
                pools.extend(payload.get("flights") or [])
        if not pools:
            raw = self.list_flights()
            try:
                payload = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                payload = {}
            if payload.get("ok"):
                pools.extend(payload.get("flights") or [])
        return _dedupe_flights(pools)

    def _resolve_flight_id(
        self,
        flight_id: str,
        *,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        date: Optional[str] = None,
        candidate_flights: Optional[list] = None,
    ) -> tuple[Optional[str], Optional[str]]:
        token = (flight_id or "").strip()
        if not token:
            return None, "flight_id is required"
        if _looks_like_convex_id(token):
            return token, None

        pools = self._collect_flights_for_resolve(
            origin=origin,
            destination=destination,
            date=date,
            candidate_flights=candidate_flights,
        )

        matches = _flights_matching_number(pools, token)
        if not matches and candidate_flights:
            matches = _flights_matching_label(candidate_flights, token)

        if len(matches) == 1:
            return str(matches[0]["_id"]), None
        if len(matches) > 1:
            opts = ", ".join(
                f"{m.get('flightNumber')} (flight_id={m.get('_id')})"
                for m in matches[:5]
            )
            return None, (
                f"Multiple flights match '{token}': {opts}. "
                "Specify flight_id from the search results."
            )
        return None, (
            f"No flight found matching '{token}'. "
            "Search again or pass the Convex flight_id from results."
        )

    def book_flight(
        self,
        flight_id: Optional[str] = None,
        passenger_name: Optional[str] = None,
        passenger_email: Optional[str] = None,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        date: Optional[str] = None,
        candidate_flights: Optional[list] = None,
    ) -> str:
        missing = [
            name
            for name, val in [
                ("flight_id", flight_id),
                ("passenger_name", passenger_name),
                ("passenger_email", passenger_email),
            ]
            if not val
        ]
        if missing:
            return _dumps({
                "ok": False,
                "error": f"Missing required booking fields: {', '.join(missing)}",
                "code": "VALIDATION",
            })

        resolved_id, resolve_err = self._resolve_flight_id(
            str(flight_id),
            origin=origin,
            destination=destination,
            date=date,
            candidate_flights=candidate_flights,
        )
        if resolve_err or not resolved_id:
            return _dumps({
                "ok": False,
                "error": resolve_err or "Could not resolve flight_id",
                "code": "VALIDATION",
            })

        payload = {
            "flightId": resolved_id,
            "passengerName": passenger_name,
            "passengerEmail": passenger_email,
        }
        envelope = post_json(f"{FLIGHTS_BASE_URL}/book", payload)
        if not envelope.get("ok"):
            return _dumps(envelope)
        data = envelope.get("data")
        if isinstance(data, dict):
            data = {**data, "resolved_flight_id": resolved_id}
        return _dumps({"ok": True, "booking": data})
