"""Agent prompt templates (LangFuse + local fallbacks)."""

from agents.prompts.agent_prompts import (
    ALL_LANGFUSE_PROMPT_NAMES,
    LANGFUSE_PROMPT_NAMES,
    build_flight_agent_system_prompt,
    build_general_qa_system_prompt,
    build_guardrail_system_prompt,
    build_hotel_agent_system_prompt,
    build_merge_system_prompt,
    build_router_prompt,
    build_router_system_prompt,
    build_router_user_prompt,
    build_extractor_system_prompt,
    get_out_of_scope_reply,
)

__all__ = [
    "LANGFUSE_PROMPT_NAMES",
    "ALL_LANGFUSE_PROMPT_NAMES",
    "build_guardrail_system_prompt",
    "build_router_prompt",
    "build_router_system_prompt",
    "build_router_user_prompt",
    "build_extractor_system_prompt",
    "build_general_qa_system_prompt",
    "build_hotel_agent_system_prompt",
    "build_flight_agent_system_prompt",
    "build_merge_system_prompt",
    "get_out_of_scope_reply",
]
