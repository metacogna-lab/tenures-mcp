"""Query agent: LangGraph ReAct agent with variable input and MCP tools (including web search)."""

from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from tenure_mcp.config import settings
from tenure_mcp.langgraphs.tools_langchain import get_langchain_tools
from tenure_mcp.prompts.query_agent_v1 import QUERY_AGENT_SYSTEM_PROMPT_V1
from tenure_mcp.schemas.agent import AgentQueryOutput
from tenure_mcp.schemas.base import RequestContext


def _get_langfuse_handler():
    """Get Langfuse callback handler for LangChain tracing. Returns None if disabled."""
    if not settings.langfuse_secret_key or not settings.langfuse_public_key:
        return None
    try:
        # Initialize the Langfuse client singleton with credentials
        from langfuse import Langfuse
        from langfuse.langchain import CallbackHandler

        Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
        return CallbackHandler()
    except Exception:
        return None


def _build_model() -> ChatOpenAI:
    """Build ChatOpenAI model from settings (no tools bound; graph provides tools)."""
    return ChatOpenAI(
        model=settings.query_agent_model,
        api_key=settings.openai_api_key or "not-set",
        temperature=0,
    )


def _extract_answer_and_tool_calls(messages: list[BaseMessage]) -> tuple[str, list[dict]]:
    """Extract final answer text and list of tool invocations from agent messages."""
    tool_calls_used: list[dict] = []
    last_content: str = ""

    for msg in messages:
        if isinstance(msg, AIMessage):
            if getattr(msg, "tool_calls", None):
                for tc in msg.tool_calls:
                    tool_calls_used.append({
                        "name": tc.get("name", ""),
                        "args": tc.get("args", {}),
                    })
            if msg.content and isinstance(msg.content, str):
                last_content = msg.content

    return last_content or "No answer generated.", tool_calls_used


async def execute_query_agent(
    query: str,
    context: RequestContext,
    max_steps: int = 5,
    correlation_id: str | None = None,
) -> AgentQueryOutput:
    """
    Run the query agent: build ReAct graph with context-scoped tools, invoke with query, return answer and tool calls.

    LLM calls are traced via Langfuse when credentials are configured.
    """
    import uuid

    cid = correlation_id or str(uuid.uuid4())
    model = _build_model()
    tools = get_langchain_tools(context)
    if not settings.openai_api_key:
        return AgentQueryOutput(
            answer="Query agent is disabled: OPENAI_API_KEY is not set.",
            tool_calls_used=[],
            correlation_id=cid,
        )

    agent = create_react_agent(
        model,
        tools=tools,
        prompt=QUERY_AGENT_SYSTEM_PROMPT_V1,
    )
    steps = min(max_steps, settings.query_agent_max_steps)
    config: dict[str, Any] = {"recursion_limit": steps}

    # Add Langfuse callback for LLM tracing if configured
    langfuse_handler = _get_langfuse_handler()
    if langfuse_handler:
        config["callbacks"] = [langfuse_handler]
        # Set trace attributes via metadata (Langfuse v3 pattern)
        config["metadata"] = {
            "langfuse_user_id": context.user_id,
            "langfuse_session_id": context.tenant_id,  # Use tenant_id as session
            "langfuse_tags": ["query_agent"],
        }

    initial = {"messages": [HumanMessage(content=query)]}
    result = await agent.ainvoke(initial, config=config)
    messages = result.get("messages", [])
    answer, tool_calls_used = _extract_answer_and_tool_calls(messages)

    # Flush Langfuse to ensure traces are sent
    if langfuse_handler:
        try:
            from langfuse import get_client

            get_client().flush()
        except Exception:
            pass  # Don't fail the request if flush fails

    return AgentQueryOutput(
        answer=answer,
        tool_calls_used=tool_calls_used,
        correlation_id=cid,
    )
