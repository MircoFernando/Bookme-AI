"""
HTTP middleware — request id, latency header, JSON 500 handler.
"""

from __future__ import annotations

import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:16]
        request.state.request_id = req_id

        start = time.perf_counter()
        response = await call_next(request)
        latency_ms = int((time.perf_counter() - start) * 1000)

        response.headers["x-request-id"] = req_id
        response.headers["x-latency-ms"] = str(latency_ms)
        return response


def install_middleware(app: FastAPI) -> None:
    app.add_middleware(RequestContextMiddleware)

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):
        req_id = getattr(request.state, "request_id", None)
        logger.exception(
            "Unhandled error on {} {} [req_id={}]",
            request.method,
            request.url.path,
            req_id,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "request_id": req_id},
            headers={"x-request-id": req_id or ""},
        )
