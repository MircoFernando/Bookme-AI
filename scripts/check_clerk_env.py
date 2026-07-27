#!/usr/bin/env python3
"""Validate Clerk + CORS env when AUTH_DISABLED=0."""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"), override=False)


def main() -> int:
    auth_disabled = os.getenv("AUTH_DISABLED", "1").lower() in ("1", "true", "yes")
    if auth_disabled:
        print("OK — AUTH_DISABLED=1 (Clerk not required on API)")
        return 0

    secret = (os.getenv("CLERK_SECRET_KEY") or "").strip()
    parties = (os.getenv("CLERK_AUTHORIZED_PARTIES") or "").strip()
    cors = (os.getenv("CORS_ORIGINS") or "").strip()

    errors: list[str] = []
    if not secret:
        errors.append("CLERK_SECRET_KEY is empty (Dashboard → API keys → Secret key)")
    if not parties:
        errors.append(
            "CLERK_AUTHORIZED_PARTIES is empty (e.g. http://localhost:5173,http://127.0.0.1:5173)"
        )
    if not cors:
        errors.append("CORS_ORIGINS is empty (same origins as authorized parties)")

    try:
        import clerk_backend_api  # noqa: F401
    except ImportError:
        errors.append("pip install clerk-backend-api (see requirements.txt)")

    if errors:
        print("Clerk production auth is enabled but configuration is incomplete:\n")
        for e in errors:
            print(f"  • {e}")
        print("\nSee docs/CLERK_SETUP.md")
        return 1

    print("OK — Clerk production env present (AUTH_DISABLED=0)")
    print(f"     authorized_parties: {parties}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
