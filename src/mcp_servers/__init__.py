"""
MCP servers — standardised bridge between agents and Convex travel APIs.

  hotel_server.py   → HotelTool   (3 tools)
  flight_server.py  → FlightTool  (3 tools)
  mcp_config.py     → subprocess launch config for MultiServerMCPClient

Run:
    cd src && python -m mcp_servers.hotel_server
    cd src && python -m mcp_servers.flight_server

Smoke test (loads all tools via MCP client):
    PYTHONPATH=src python scripts/test_mcp_client.py
"""

from mcp_servers.mcp_config import build_mcp_server_config

__all__ = ["build_mcp_server_config"]
