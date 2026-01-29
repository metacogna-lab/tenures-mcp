"""MCP SSE Transport for Tenure MCP Server.

Exposes the MCP Server tools via Server-Sent Events (SSE) transport
for LLM agent integration (Claude MCP client, LangChain).

Note: Currently uses stub implementations due to naming conflict between
the local 'mcp' package and the external MCP SDK. Full SSE support requires
either renaming the local package or using alternative import strategies.

TODO: Resolve namespace conflict to enable full MCP SDK integration.
"""

import json
import logging
from typing import Any, Callable

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

logger = logging.getLogger(__name__)


def _get_default_context():
    """Create default request context for SSE connections."""
    # Import here to avoid circular import
    from mcp.config import settings
    from mcp.schemas.base import RequestContext
    
    return RequestContext(
        user_id="sse_client",
        tenant_id="default",
        auth_context="sse",
        role=settings.role,
    )


# Tool definitions for MCP protocol
TOOL_DEFINITIONS = [
    {
        "name": "analyze_open_home_feedback",
        "description": "Analyze open home feedback for a property. Returns sentiment categories and comment breakdown.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "property_id": {
                    "type": "string",
                    "description": "Property identifier (e.g., prop_001)",
                }
            },
            "required": ["property_id"],
        },
    },
    {
        "name": "calculate_breach_status",
        "description": "Calculate breach status for a tenancy. Returns legality and breach risk based on rent status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tenancy_id": {
                    "type": "string",
                    "description": "Tenancy identifier (e.g., tenancy_001)",
                }
            },
            "required": ["tenancy_id"],
        },
    },
    {
        "name": "ocr_document",
        "description": "Extract text from uploaded documents using OCR.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_url": {
                    "type": "string",
                    "description": "URL or URI of the document to process",
                }
            },
            "required": ["document_url"],
        },
    },
    {
        "name": "extract_expiry_date",
        "description": "Extract expiry dates from text using regex patterns.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to extract dates from",
                }
            },
            "required": ["text"],
        },
    },
    {
        "name": "generate_vendor_report",
        "description": "Generate weekly vendor report combining feedback, stats, and trends.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "property_id": {
                    "type": "string",
                    "description": "Property identifier",
                }
            },
            "required": ["property_id"],
        },
    },
    {
        "name": "web_search",
        "description": "Search the web for current information using Tavily API.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 5)",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
]


async def execute_tool(name: str, arguments: dict[str, Any]) -> dict:
    """Execute an MCP tool and return results."""
    context = _get_default_context()

    # Import tool implementations
    from mcp.tools.implementations import (
        analyze_open_home_feedback,
        calculate_breach_status,
        extract_expiry_date,
        generate_vendor_report,
        ocr_document,
        web_search,
    )
    from mcp.schemas.tools import (
        AnalyzeFeedbackInput,
        CalculateBreachInput,
        ExtractExpiryInput,
        GenerateVendorReportInput,
        OCRDocumentInput,
        WebSearchInput,
    )

    try:
        if name == "analyze_open_home_feedback":
            input_data = AnalyzeFeedbackInput(**arguments)
            result = await analyze_open_home_feedback(input_data, context)
        elif name == "calculate_breach_status":
            input_data = CalculateBreachInput(**arguments)
            result = await calculate_breach_status(input_data, context)
        elif name == "ocr_document":
            input_data = OCRDocumentInput(**arguments)
            result = await ocr_document(input_data, context)
        elif name == "extract_expiry_date":
            input_data = ExtractExpiryInput(**arguments)
            result = await extract_expiry_date(input_data, context)
        elif name == "generate_vendor_report":
            input_data = GenerateVendorReportInput(**arguments)
            result = await generate_vendor_report(input_data, context)
        elif name == "web_search":
            input_data = WebSearchInput(**arguments)
            result = await web_search(input_data, context)
        else:
            return {"error": f"Unknown tool: {name}"}

        # Convert Pydantic model to dict
        if hasattr(result, "model_dump"):
            return result.model_dump(mode="json")
        return result

    except Exception as e:
        logger.exception(f"Tool execution failed: {name}")
        return {"error": f"Tool execution failed: {str(e)}"}


# Simple SSE endpoint handlers (JSON-RPC style)
async def handle_sse(request: Request):
    """Handle SSE connection - returns server info and available tools."""
    async def event_stream():
        # Send server info
        yield f"data: {json.dumps({'type': 'server_info', 'name': 'tenure-mcp-server', 'version': '0.1.0'})}\n\n"
        # Send available tools
        yield f"data: {json.dumps({'type': 'tools', 'tools': TOOL_DEFINITIONS})}\n\n"
        # Keep connection alive
        import asyncio
        while True:
            await asyncio.sleep(30)
            yield f"data: {json.dumps({'type': 'ping'})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def handle_list_tools(request: Request):
    """List available tools (JSON-RPC compatible)."""
    return JSONResponse({
        "jsonrpc": "2.0",
        "result": {"tools": TOOL_DEFINITIONS},
        "id": request.query_params.get("id", "1"),
    })


async def handle_call_tool(request: Request):
    """Execute a tool (JSON-RPC compatible)."""
    try:
        body = await request.json()
        
        # Support both direct and JSON-RPC style requests
        if "method" in body:
            # JSON-RPC style
            params = body.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            request_id = body.get("id", "1")
        else:
            # Direct style
            tool_name = body.get("name")
            arguments = body.get("arguments", {})
            request_id = body.get("id", "1")
        
        if not tool_name:
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "Missing tool name"},
                "id": request_id,
            }, status_code=400)
        
        result = await execute_tool(tool_name, arguments)
        
        if "error" in result:
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": result["error"]},
                "id": request_id,
            }, status_code=500)
        
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": {"content": [{"type": "text", "text": json.dumps(result, default=str)}]},
            "id": request_id,
        })
        
    except json.JSONDecodeError:
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"},
            "id": None,
        }, status_code=400)
    except Exception as e:
        logger.exception("Tool call failed")
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": None,
        }, status_code=500)


def create_sse_app() -> Starlette:
    """Create Starlette app for SSE transport."""
    return Starlette(
        debug=False,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/tools", endpoint=handle_list_tools, methods=["GET"]),
            Route("/tools/call", endpoint=handle_call_tool, methods=["POST"]),
            Route("/messages/", endpoint=handle_call_tool, methods=["POST"]),
        ],
    )


# Export for mounting in FastAPI
sse_app = create_sse_app()
