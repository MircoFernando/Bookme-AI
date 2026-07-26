"""
Flight MCP server — exposes FlightTool over the Model Context Protocol.

Run standalone:
    cd src && python -m mcp_servers.flight_server

Inspect:
    make inspect-flight
"""

from __future__ import annotations

import os
import sys
from typing import Optional

_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(_SRC), ".env"))

from loguru import logger
from mcp.server.fastmcp import FastMCP

from agents.tools.flight_tool import FlightTool

mcp = FastMCP("tripweaver-flights")

_flight: FlightTool | None = None


def _get_flight() -> FlightTool:
    global _flight
    if _flight is None:
        logger.info("Initialising FlightTool inside MCP server...")
        _flight = FlightTool()
    return _flight


@mcp.tool()
def list_flights() -> str:
    """List all available flights from the travel service."""
    return _get_flight().dispatch("list_flights", {})


@mcp.tool()
def search_flights(
    origin: str,
    destination: str,
    date: Optional[str] = None,
) -> str:
    """
    Search flights by origin, destination, and optional date (YYYY-MM-DD).

    Args:
        origin: Origin city or 3-letter airport code (e.g. CMB).
        destination: Destination city or airport code (e.g. BKK).
        date: Optional departure date (YYYY-MM-DD).
    """
    params = {"origin": origin, "destination": destination}
    if date:
        params["date"] = date
    return _get_flight().dispatch("search_flights", params)


@mcp.tool()
def book_flight(
    flight_id: str,
    passenger_name: str,
    passenger_email: str,
) -> str:
    """
    Book a flight.

    Args:
        flight_id: Flight identifier from search/list results.
        passenger_name: Passenger full name.
        passenger_email: Passenger email.
    """
    return _get_flight().dispatch(
        "book_flight",
        {
            "flight_id": flight_id,
            "passenger_name": passenger_name,
            "passenger_email": passenger_email,
        },
    )


if __name__ == "__main__":
    logger.info("Starting tripweaver-flights MCP server on stdio...")
    mcp.run()
