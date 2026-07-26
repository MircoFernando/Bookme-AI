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
            }
            for src, dst in aliases.items():
                if src in p and dst not in p:
                    p[dst] = p.pop(src)
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

    def book_flight(
        self,
        flight_id: Optional[str] = None,
        passenger_name: Optional[str] = None,
        passenger_email: Optional[str] = None,
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

        payload = {
            "flightId": flight_id,
            "passengerName": passenger_name,
            "passengerEmail": passenger_email,
        }
        envelope = post_json(f"{FLIGHTS_BASE_URL}/book", payload)
        if not envelope.get("ok"):
            return _dumps(envelope)
        return _dumps({"ok": True, "booking": envelope.get("data")})
