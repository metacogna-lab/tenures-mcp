"""Tests for query agent (LangGraph ReAct agent with MCP tools)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from mcp.schemas.base import RequestContext
from mcp.schemas.agent import AgentQueryInput, AgentQueryOutput


@pytest.fixture
def context():
    """Create test request context."""
    return RequestContext(
        user_id="test_user",
        tenant_id="test_tenant",
        auth_context="test_token",
        role="agent",
    )


@pytest.mark.asyncio
async def test_execute_query_agent_no_openai_key(context, monkeypatch):
    """Test execute_query_agent returns disabled message when OPENAI_API_KEY is not set."""
    import mcp.config
    monkeypatch.setattr(mcp.config.settings, "openai_api_key", "")

    from mcp.langgraphs.agent import execute_query_agent

    result = await execute_query_agent("What is the breach status?", context)
    assert isinstance(result, AgentQueryOutput)
    assert "disabled" in result.answer.lower() or "OPENAI_API_KEY" in result.answer
    assert result.tool_calls_used == []


@pytest.mark.asyncio
async def test_execute_query_agent_mocked_graph(context, monkeypatch):
    """Test execute_query_agent with mocked LangGraph agent."""
    import mcp.config
    monkeypatch.setattr(mcp.config.settings, "openai_api_key", "sk-fake")
    monkeypatch.setattr(mcp.config.settings, "query_agent_model", "gpt-4o-mini")
    monkeypatch.setattr(mcp.config.settings, "query_agent_max_steps", 5)

    from langchain_core.messages import AIMessage, HumanMessage

    mock_agent = MagicMock()
    mock_agent.ainvoke = AsyncMock(return_value={
        "messages": [
            HumanMessage(content="Test query"),
            AIMessage(content="", tool_calls=[{"id": "call_1", "name": "web_search", "args": {"query": "test"}}]),
            AIMessage(content="Here is your answer based on the search results."),
        ]
    })

    with patch("mcp.langgraphs.agent.create_react_agent", return_value=mock_agent):
        from mcp.langgraphs.agent import execute_query_agent

        result = await execute_query_agent("Test query", context)

    assert isinstance(result, AgentQueryOutput)
    assert "answer" in result.answer.lower() or len(result.answer) > 0
    assert len(result.tool_calls_used) == 1
    assert result.tool_calls_used[0]["name"] == "web_search"


@pytest.mark.asyncio
async def test_agent_query_input_validation():
    """Test AgentQueryInput validation."""
    # Valid input
    valid = AgentQueryInput(query="What is the breach status for tenancy_001?")
    assert valid.query == "What is the breach status for tenancy_001?"
    assert valid.max_steps == 5  # default

    # With custom max_steps
    custom = AgentQueryInput(query="Test", max_steps=10)
    assert custom.max_steps == 10

    # Empty query should fail
    with pytest.raises(Exception):
        AgentQueryInput(query="")

    # max_steps out of range
    with pytest.raises(Exception):
        AgentQueryInput(query="Test", max_steps=25)


@pytest.mark.asyncio
async def test_agent_query_output_structure():
    """Test AgentQueryOutput structure."""
    output = AgentQueryOutput(
        answer="The breach status is high risk.",
        tool_calls_used=[{"name": "calculate_breach_status", "args": {"tenancy_id": "tenancy_001"}}],
        correlation_id="test-123",
    )
    assert output.answer == "The breach status is high risk."
    assert len(output.tool_calls_used) == 1
    assert output.correlation_id == "test-123"
