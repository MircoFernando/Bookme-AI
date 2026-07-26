"""
Hotel MCP server — exposes HotelTool over the Model Context Protocol.

Thin transport layer only: all business logic stays in ``agents.tools.hotel_tool``.

Transport: stdio (JSON-RPC on stdout — never print() to stdout in this process).

Run standalone:
    cd src && python -m mcp_servers.hotel_server

Inspect:
    make inspect-hotel
"""

from __future__ import annotations

import os
import sys
from typing import Optional

# Ensure ``src/`` is importable when launched as ``python -m mcp_servers.hotel_server``
_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(_SRC), ".env"))

from loguru import logger
from mcp.server.fastmcp import FastMCP

from agents.tools.hotel_tool import HotelTool

mcp = FastMCP("bookme-ai-hotels")

_hotel: HotelTool | None = None


def _get_hotel() -> HotelTool:
    global _hotel
    if _hotel is None:
        logger.info("Initialising HotelTool inside MCP server...")
        _hotel = HotelTool()
    return _hotel


@mcp.tool()
def list_hotels() -> str:
    """List all available hotels from the travel service."""
    return _get_hotel().dispatch("list_hotels", {})


@mcp.tool()
def search_hotels(
    city: str,
    check_in: Optional[str] = None,
    check_out: Optional[str] = None,
) -> str:
    """
    Search hotels by city and optional check-in/check-out dates (YYYY-MM-DD).

    Args:
        city: City name, e.g. Colombo, Bangkok, Mumbai.
        check_in: Optional check-in date (YYYY-MM-DD).
        check_out: Optional check-out date (YYYY-MM-DD).
    """
    params = {"city": city}
    if check_in:
        params["checkIn"] = check_in
    if check_out:
        params["checkOut"] = check_out
    return _get_hotel().dispatch("search_hotels", params)


@mcp.tool()
def book_hotel(
    hotel_id: str,
    guest_name: str,
    guest_email: str,
    check_in_date: str,
    check_out_date: str,
    room_type: str,
) -> str:
    """
    Book a hotel room.

    Args:
        hotel_id: Hotel identifier from search/list results.
        guest_name: Guest full name.
        guest_email: Guest email.
        check_in_date: Check-in (YYYY-MM-DD).
        check_out_date: Check-out (YYYY-MM-DD).
        room_type: e.g. single, double, suite.
    """
    return _get_hotel().dispatch(
        "book_hotel",
        {
            "hotel_id": hotel_id,
            "guest_name": guest_name,
            "guest_email": guest_email,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "room_type": room_type,
        },
    )


if __name__ == "__main__":
    logger.info("Starting bookme-ai-hotels MCP server on stdio...")
    mcp.run()
