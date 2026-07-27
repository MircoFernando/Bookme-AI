"""
Hotel tool — Convex hotel API (list / search / book).

Business logic lives here; MCP servers only call
``HotelTool.dispatch(action, params)``. Returns a **JSON string** so MCP
and adapters share one contract.
"""

from __future__ import annotations

import json
from typing import Any, Optional

from loguru import logger

from infrastructure.config import HOTELS_BASE_URL
from infrastructure.http_client import get_json, post_json
from infrastructure.observability import observe, update_current_observation


def _dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _extract_hotels(data: Any) -> list:
    if isinstance(data, dict):
        raw = data.get("hotels", [])
        return raw if isinstance(raw, list) else []
    if isinstance(data, list):
        return data
    return []


class HotelTool:
    """Hotel service actions routed by ``dispatch``."""

    VALID_ACTIONS = ("list_hotels", "search_hotels", "book_hotel")

    @observe(name="hotel_tool")
    def dispatch(self, action: str, params: Optional[dict] = None) -> str:
        params = params or {}
        update_current_observation(input=f"action={action} params={params}")

        handlers = {
            "list_hotels": self.list_hotels,
            "search_hotels": self.search_hotels,
            "book_hotel": self.book_hotel,
        }
        handler = handlers.get(action)
        if handler is None:
            return _dumps({
                "ok": False,
                "error": f"Unknown hotel action: {action}",
                "code": "UNKNOWN_ACTION",
                "available": list(handlers.keys()),
            })

        try:
            result = handler(**self._clean_params(action, params))
            update_current_observation(output=result[:500] if len(result) > 500 else result)
            return result
        except TypeError as exc:
            logger.warning("HotelTool dispatch TypeError: {}", exc)
            return _dumps({
                "ok": False,
                "error": f"Invalid parameters for {action}: {exc}",
                "code": "VALIDATION",
            })
        except Exception as exc:
            logger.exception("HotelTool dispatch failed")
            return _dumps({
                "ok": False,
                "error": f"Hotel service error: {exc}",
                "code": "INTERNAL",
            })

    @staticmethod
    def _clean_params(action: str, params: dict) -> dict:
        """Map router aliases and drop Nones."""
        p = {k: v for k, v in params.items() if v is not None}
        if action == "search_hotels":
            if "check_in" in p and "checkIn" not in p:
                p["checkIn"] = p.pop("check_in")
            if "check_out" in p and "checkOut" not in p:
                p["checkOut"] = p.pop("check_out")
        if action == "book_hotel":
            aliases = {
                "hotelId": "hotel_id",
                "guestName": "guest_name",
                "guestEmail": "guest_email",
                "checkInDate": "check_in_date",
                "checkOutDate": "check_out_date",
                "roomType": "room_type",
            }
            for src, dst in aliases.items():
                if src in p and dst not in p:
                    p[dst] = p.pop(src)
        return p

    def list_hotels(self) -> str:
        envelope = get_json(HOTELS_BASE_URL)
        if not envelope.get("ok"):
            return _dumps(envelope)
        hotels = _extract_hotels(envelope.get("data"))
        return _dumps({"ok": True, "hotels": hotels, "count": len(hotels)})

    def search_hotels(
        self,
        city: str,
        checkIn: Optional[str] = None,
        checkOut: Optional[str] = None,
    ) -> str:
        if not city or not str(city).strip():
            return _dumps({
                "ok": False,
                "error": "city is required to search hotels",
                "code": "VALIDATION",
            })
        query: dict[str, str] = {"city": str(city).strip()}
        if checkIn:
            query["checkIn"] = checkIn
        if checkOut:
            query["checkOut"] = checkOut

        envelope = get_json(f"{HOTELS_BASE_URL}/search", params=query)
        if not envelope.get("ok"):
            return _dumps(envelope)
        hotels = _extract_hotels(envelope.get("data"))
        return _dumps({"ok": True, "hotels": hotels, "count": len(hotels), "city": query["city"]})

    def book_hotel(
        self,
        hotel_id: Optional[str] = None,
        guest_name: Optional[str] = None,
        guest_email: Optional[str] = None,
        check_in_date: Optional[str] = None,
        check_out_date: Optional[str] = None,
        room_type: Optional[str] = None,
    ) -> str:
        missing = [
            name
            for name, val in [
                ("hotel_id", hotel_id),
                ("guest_name", guest_name),
                ("guest_email", guest_email),
                ("check_in_date", check_in_date),
                ("check_out_date", check_out_date),
                ("room_type", room_type),
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
            "hotelId": hotel_id,
            "guestName": guest_name,
            "guestEmail": guest_email,
            "checkInDate": check_in_date,
            "checkOutDate": check_out_date,
            "roomType": room_type,
        }
        envelope = post_json(f"{HOTELS_BASE_URL}/book", payload)
        if not envelope.get("ok"):
            return _dumps(envelope)
        return _dumps({"ok": True, "booking": envelope.get("data")})
