"""Schemas for the query agent (variable input, LLM + tools)."""

from typing import List

from pydantic import BaseModel, Field


class AgentQueryInput(BaseModel):
    """Request body for POST /v1/agent/query."""

    query: str = Field(..., min_length=1, max_length=10000, description="Natural language query")
    max_steps: int = Field(default=5, ge=1, le=20, description="Max tool-calling steps")


class AgentQueryOutput(BaseModel):
    """Response from the query agent."""

    answer: str = Field(..., description="Final answer to the user")
    tool_calls_used: List[dict] = Field(default_factory=list, description="Tool invocations made")
    correlation_id: str = Field(..., description="Request correlation ID")
