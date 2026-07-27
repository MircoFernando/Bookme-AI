"""
Web search MCP server — exposes WebSearchTool over the Model Context Protocol.

Thin transport layer only: all business logic stays in ``agents.tools.web_search_tool``.

Transport: stdio (JSON-RPC on stdout — never print() to stdout in this process).

Run standalone:
    cd src && python -m mcp_servers.web_search_server

Inspect:
    make inspect-web-search
"""

from __future__ import annotations

import os
import sys

# Ensure ``src/`` is importable when launched as ``python -m mcp_servers.web_search_server``
_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(_SRC), ".env"))

from loguru import logger
from mcp.server.fastmcp import FastMCP

from agents.tools.web_search_tool import WebSearchTool

mcp = FastMCP("bookme-ai-web-search")

_web_search: WebSearchTool | None = None


def _get_web_search() -> WebSearchTool:
    global _web_search
    if _web_search is None:
        logger.info("Initialising WebSearchTool inside MCP server...")
        _web_search = WebSearchTool()
    return _web_search


@mcp.tool()
async def search_web(query: str) -> str:
    """Search the web for travel destinations, attractions, and trip advice."""
    return await _get_web_search().asearch(query)


if __name__ == "__main__":
    logger.info("Starting bookme-ai-web-search MCP server on stdio...")
    mcp.run()
