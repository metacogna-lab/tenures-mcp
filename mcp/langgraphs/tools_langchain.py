"""Convert MCP tool registry to LangChain tools for the query agent."""

from typing import Any, List, Type

from langchain_core.tools import StructuredTool
from pydantic import BaseModel

from mcp.schemas.base import RequestContext
from mcp.tools import get_tool_registry


def _get_input_schemas() -> dict[str, tuple[Type[BaseModel], str]]:
    """Tool name -> (input schema class, description)."""
    from mcp.schemas.tools import (
        AnalyzeFeedbackInput,
        CalculateBreachInput,
        ExtractExpiryInput,
        GenerateVendorReportInput,
        OCRDocumentInput,
        PrepareBreachNoticeInput,
        WebSearchInput,
    )

    return {
        "analyze_open_home_feedback": (AnalyzeFeedbackInput, "Analyze open home feedback for a property. Input: property_id."),
        "calculate_breach_status": (CalculateBreachInput, "Get breach risk and arrears status for a tenancy. Input: tenancy_id."),
        "generate_vendor_report": (GenerateVendorReportInput, "Generate weekly vendor report for a property. Input: property_id."),
        "ocr_document": (OCRDocumentInput, "Extract text from a document URL. Input: document_url."),
        "extract_expiry_date": (ExtractExpiryInput, "Extract expiry/compliance dates from text. Input: text (10-10000 chars)."),
        "prepare_breach_notice": (PrepareBreachNoticeInput, "Draft a breach notice. Input: tenancy_id, breach_type (rent_arrears, lease_violation, property_damage)."),
        "web_search": (WebSearchInput, "Search the web. Use when the question needs current or external information. Input: query, optional max_results."),
    }


async def _invoke_tool(
    schema_class: Type[BaseModel],
    tool_func: Any,
    context: RequestContext,
    **kwargs: Any,
) -> str:
    """Run one MCP tool and return result as string."""
    try:
        input_data = schema_class(**kwargs)
        output = await tool_func(input_data, context)
        if hasattr(output, "model_dump"):
            return str(output.model_dump())
        return str(output)
    except Exception as e:
        return f"Error: {e!s}"


def get_langchain_tools(context: RequestContext) -> List[StructuredTool]:
    """Build LangChain tools from MCP tool registry for the given request context."""
    registry = get_tool_registry()
    schemas = _get_input_schemas()
    tools = []

    for name, (schema_class, description) in schemas.items():
        tool_func = registry.get(name)
        if not tool_func:
            continue

        def _make_coro(
            sc: Type[BaseModel],
            tf: Any,
            ctx: RequestContext,
        ):
            async def _coro(**kwargs: Any) -> str:
                return await _invoke_tool(sc, tf, ctx, **kwargs)

            return _coro

        tools.append(
            StructuredTool.from_function(
                coroutine=_make_coro(schema_class, tool_func, context),
                name=name,
                description=description,
                args_schema=schema_class,
            )
        )

    return tools
