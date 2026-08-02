"""
Web search tool — Tavily Search API (travel / tourism Q&A).

Business logic lives here; the MCP server calls ``WebSearchTool.asearch``.
Returns a **JSON string** (same contract as ``HotelTool`` / ``FlightTool``).
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
from loguru import logger

from infrastructure.config import (
    HTTP_TIMEOUT,
    TAVILY_INCLUDE_ANSWER,
    TAVILY_MAX_RESULTS,
    TAVILY_SEARCH_DEPTH,
    TAVILY_SEARCH_URL,
    get_tavily_api_key,
)
from infrastructure.observability import observe, update_current_observation


def _dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _compact_results(raw: Any) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if not isinstance(raw, list):
        return out
    for item in raw[:TAVILY_MAX_RESULTS]:
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "title": str(item.get("title") or ""),
                "url": str(item.get("url") or ""),
                "content": str(item.get("content") or "")[:1200],
            }
        )
    return out


class WebSearchTool:
    """Tavily-backed web search for destination and tourism questions."""

    @observe(name="web_search_tool")
    async def asearch(self, query: str) -> str:
        q = (query or "").strip()
        update_current_observation(input=q[:300])

        if not q:
            return _dumps(
                {"ok": False, "error": "Empty search query.", "code": "VALIDATION"}
            )

        api_key = get_tavily_api_key()
        if not api_key:
            logger.warning(
                "TAVILY_API_KEY is not set in this process — "
                "MCP stdio children need env forwarded via mcp_config.mcp_subprocess_env()"
            )
            return _dumps(
                {
                    "ok": False,
                    "error": "TAVILY_API_KEY is not set.",
                    "code": "UNAVAILABLE",
                }
            )

        payload = {
            "api_key": api_key,
            "query": q,
            "search_depth": TAVILY_SEARCH_DEPTH,
            "max_results": TAVILY_MAX_RESULTS,
            "include_answer": TAVILY_INCLUDE_ANSWER,
        }

        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                response = await client.post(TAVILY_SEARCH_URL, json=payload)
        except httpx.TimeoutException:
            logger.warning("Tavily search timed out")
            return _dumps(
                {"ok": False, "error": "Web search timed out.", "code": "TIMEOUT"}
            )
        except httpx.ConnectError as exc:
            logger.warning("Tavily connection error: {}", exc)
            return _dumps(
                {"ok": False, "error": "Could not reach Tavily.", "code": "NETWORK"}
            )
        except Exception as exc:
            logger.exception("Tavily search failed")
            return _dumps({"ok": False, "error": str(exc), "code": "INTERNAL"})

        if response.status_code >= 400:
            logger.warning(
                "Tavily HTTP {}: {}",
                response.status_code,
                response.text[:200],
            )
            return _dumps(
                {
                    "ok": False,
                    "error": f"Tavily HTTP {response.status_code}: {response.text[:200]}",
                    "code": "HTTP",
                    "status_code": response.status_code,
                }
            )

        try:
            body = response.json()
        except Exception as exc:
            return _dumps(
                {"ok": False, "error": f"Invalid JSON: {exc}", "code": "PARSE"}
            )

        compact = {
            "ok": True,
            "query": q,
            "answer": body.get("answer") if TAVILY_INCLUDE_ANSWER else None,
            "results": _compact_results(body.get("results")),
        }
        result = _dumps(compact)
        update_current_observation(
            output=result[:500] if len(result) > 500 else result
        )
        return result

    def search(self, query: str) -> str:
        """Sync entry for scripts/tests."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.asearch(query))
        return loop.run_until_complete(self.asearch(query))
