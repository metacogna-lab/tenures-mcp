"""Langfuse-wrapped OpenAI client for traced LLM calls."""

import os
from typing import Any

from mcp.config import settings

# Configure Langfuse environment before importing the wrapped client.
# Langfuse reads these env vars on import.
if settings.langfuse_secret_key and settings.langfuse_public_key:
    os.environ.setdefault("LANGFUSE_SECRET_KEY", settings.langfuse_secret_key)
    os.environ.setdefault("LANGFUSE_PUBLIC_KEY", settings.langfuse_public_key)
    os.environ.setdefault("LANGFUSE_HOST", settings.langfuse_host)
else:
    # Disable Langfuse tracing when credentials are not set
    os.environ.setdefault("LANGFUSE_TRACING_ENABLED", "false")

# Use Langfuse's drop-in replacement for OpenAI
from langfuse.openai import AsyncOpenAI

# Module-level client instance (lazy initialized)
_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    """Get or create the Langfuse-wrapped async OpenAI client."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def create_chat_completion(
    name: str,
    model: str,
    messages: list[dict[str, str]],
    metadata: dict[str, Any] | None = None,
    **kwargs: Any,
) -> Any:
    """Create a chat completion with Langfuse tracing.

    Args:
        name: Identifier for this generation in Langfuse (e.g. "query_agent").
        model: OpenAI model name (e.g. "gpt-4o-mini").
        messages: List of message dicts with "role" and "content" keys.
        metadata: Optional metadata dict passed to Langfuse for filtering/grouping.
        **kwargs: Additional arguments passed to OpenAI's create method.

    Returns:
        The OpenAI ChatCompletion response object.
    """
    client = get_openai_client()
    return await client.chat.completions.create(
        model=model,
        messages=messages,
        name=name,
        metadata=metadata or {},
        **kwargs,
    )
