#!/usr/bin/env python3
"""Unit tests for Gemini/OpenAI content normalization in the orchestrator."""

from __future__ import annotations

import sys

sys.path.insert(0, "src")

from agents.orchestrator import _llm_content_to_str


def test_plain_string() -> None:
    assert _llm_content_to_str("hello") == "hello"


def test_gemini_signature_only_block() -> None:
    gemini_tail = [
        {
            "type": "text",
            "text": "",
            "extras": {"signature": "EjQKMgERTTIPwd2Y/23++bbO0Emkju7ZpESK5OJeZwRlw03RL5lUQ68bfKlsxiGKNebe24qn"},
            "index": 0,
        }
    ]
    assert _llm_content_to_str(gemini_tail) == ""


def test_mixed_text_and_signature_blocks() -> None:
    blocks = [
        {"type": "text", "text": "Safe travels!"},
        {
            "type": "text",
            "text": "",
            "extras": {"signature": "EjQK..."},
        },
    ]
    assert _llm_content_to_str(blocks) == "Safe travels!"


def test_openai_style_text_blocks() -> None:
    blocks = [{"type": "text", "text": "Line one"}, {"type": "text", "text": "Line two"}]
    assert _llm_content_to_str(blocks) == "Line one\nLine two"


def main() -> int:
    test_plain_string()
    test_gemini_signature_only_block()
    test_mixed_text_and_signature_blocks()
    test_openai_style_text_blocks()
    print("OK test_llm_content_to_str")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
