"""
HTTP client for external travel APIs (Convex hotel/flight services).

"""

from __future__ import annotations

from typing import Any, Optional

import httpx
from loguru import logger
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from infrastructure.config import (
    HTTP_BACKOFF_SECONDS,
    HTTP_MAX_RETRIES,
    HTTP_TIMEOUT,
)


class RetryableHTTPError(Exception):
    """Raised internally to trigger tenacity retry on server/gateway errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


def _attempts() -> int:
    # tenacity counts the initial try + retries; cap at least 1 attempt.
    return max(1, HTTP_MAX_RETRIES)


def _fail(error: str, code: str, *, status_code: Optional[int] = None) -> dict[str, Any]:
    out: dict[str, Any] = {"ok": False, "error": error, "code": code}
    if status_code is not None:
        out["status_code"] = status_code
    return out


def _ok(data: Any) -> dict[str, Any]:
    return {"ok": True, "data": data}


@retry(
    reraise=True,
    stop=stop_after_attempt(_attempts()),
    wait=wait_exponential(multiplier=HTTP_BACKOFF_SECONDS, min=HTTP_BACKOFF_SECONDS, max=8),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError, RetryableHTTPError)),
)
def _request(method: str, url: str, *, params: Optional[dict] = None, json_body: Optional[dict] = None) -> dict[str, Any]:
    """Single HTTP round-trip; may raise for retryable errors."""
    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        response = client.request(method, url, params=params, json=json_body)

    if response.status_code in (502, 503, 504):
        raise RetryableHTTPError(
            f"Upstream unavailable (HTTP {response.status_code})",
            status_code=response.status_code,
        )

    if response.status_code >= 400:
        return _fail(
            f"HTTP {response.status_code}: {response.text[:200]}",
            "HTTP",
            status_code=response.status_code,
        )

    try:
        body = response.json()
    except Exception as exc:
        return _fail(f"Invalid JSON response: {exc}", "PARSE")

    return _ok(body)


def get_json(url: str, params: Optional[dict] = None) -> dict[str, Any]:
    """GET and parse JSON with retries. Never raises — returns envelope."""
    try:
        return _request("GET", url, params=params)
    except httpx.TimeoutException:
        logger.warning("GET timeout: {}", url)
        return _fail("Travel service timed out. Please try again.", "TIMEOUT")
    except httpx.ConnectError as exc:
        logger.warning("GET connection error {}: {}", url, exc)
        return _fail("Could not reach the travel service.", "NETWORK")
    except RetryableHTTPError as exc:
        logger.warning("GET failed after retries {}: {}", url, exc)
        return _fail(str(exc), "UPSTREAM", status_code=exc.status_code)
    except Exception as exc:
        logger.exception("GET unexpected error {}", url)
        return _fail(f"Unexpected error: {exc}", "UNKNOWN")


def post_json(url: str, payload: dict) -> dict[str, Any]:
    """POST JSON with retries. Never raises — returns envelope."""
    try:
        return _request("POST", url, json_body=payload)
    except httpx.TimeoutException:
        logger.warning("POST timeout: {}", url)
        return _fail("Booking service timed out. Please try again.", "TIMEOUT")
    except httpx.ConnectError as exc:
        logger.warning("POST connection error {}: {}", url, exc)
        return _fail("Could not reach the booking service.", "NETWORK")
    except RetryableHTTPError as exc:
        logger.warning("POST failed after retries {}: {}", url, exc)
        return _fail(str(exc), "UPSTREAM", status_code=exc.status_code)
    except Exception as exc:
        logger.exception("POST unexpected error {}", url)
        return _fail(f"Unexpected error: {exc}", "UNKNOWN")
