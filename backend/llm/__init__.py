"""LLM module with Langfuse-traced OpenAI client.

This module provides a thin wrapper around the OpenAI API that automatically
logs all LLM calls to Langfuse for observability. When Langfuse credentials
are not configured, tracing is disabled but the client still works.
"""

from backend.llm.client import create_chat_completion, get_openai_client

__all__ = ["create_chat_completion", "get_openai_client"]
