"""
MCP servers — the standardised bridge between agents and external travel
services. Each server wraps a business tool and exposes it over the Model
Context Protocol so agents consume it through the MCP layer, never directly.

Populated on Day 2:
    hotel_server.py    — list_hotels / search_hotels / book_hotel
    flight_server.py   — list_flights / search_flights / book_flight
    mcp_config.py      — subprocess launch config for MultiServerMCPClient
"""
