"""
Centralised logging — powered by **loguru**.

Usage (any module)::

    from loguru import logger
    logger.info("Hello")

Usage (entry-points — API, scripts, MCP servers)::

    from infrastructure.log import setup_logging
    setup_logging()            # defaults: INFO, stderr

IMPORTANT — stdio-safe by design:
    Logs are written to **stderr**, never stdout. MCP servers communicate
    over stdout using JSON-RPC; any stray stdout write corrupts the protocol.
    Keeping loguru on stderr means the same logging setup is safe inside an
    MCP server subprocess.
"""

from __future__ import annotations

import logging
import sys
from typing import Optional

from loguru import logger

_FMT = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
    "<level>{message}</level>"
)

_CONFIGURED = False


class _InterceptHandler(logging.Handler):
    """Route stdlib ``logging`` records into loguru so third-party libs
    (uvicorn, httpx, langchain, mcp) emit through the same sinks."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(
    level: Optional[str] = None,
    *,
    intercept_stdlib: bool = True,
    log_file: Optional[str] = None,
) -> None:
    """Configure loguru for the current process. Call once at each entry-point.

    Args:
        level: Minimum level. Defaults to ``config.LOG_LEVEL`` (INFO).
        intercept_stdlib: Route stdlib logging through loguru.
        log_file: Optional rotating file sink.
    """
    global _CONFIGURED

    if level is None:
        try:
            from infrastructure.config import LOG_LEVEL
            level = LOG_LEVEL
        except Exception:
            level = "INFO"

    logger.remove()
    logger.add(
        sys.stderr,                 # stderr — stdio-safe for MCP servers
        format=_FMT,
        level=level.upper(),
        colorize=True,
        backtrace=True,
        diagnose=False,             # concise tracebacks in production
    )

    if log_file:
        logger.add(
            log_file,
            format=_FMT,
            level=level.upper(),
            rotation="10 MB",
            retention="7 days",
            compression="gz",
        )

    if intercept_stdlib:
        logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)

    _CONFIGURED = True
    logger.debug("Loguru configured — level={}", level)
