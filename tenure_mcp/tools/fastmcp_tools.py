"""FastMCP-compatible tool implementations.

This module provides FastMCP decorator-based tool registrations that wrap
our existing tool implementations. Tools are registered using FastMCP's
@mcp.tool() decorator pattern.
"""

from tenure_mcp.schemas.base import RequestContext
from tenure_mcp.schemas.tools import (
    AnalyzeFeedbackInput,
    AnalyzeFeedbackOutput,
    CalculateBreachInput,
    CalculateBreachOutput,
    ExtractExpiryInput,
    ExtractExpiryOutput,
    GenerateVendorReportInput,
    GenerateVendorReportOutput,
    OCRDocumentInput,
    OCRDocumentOutput,
    PrepareBreachNoticeInput,
    PrepareBreachNoticeOutput,
    WebSearchInput,
    WebSearchOutput,
)
from tenure_mcp.tools.implementations import (
    analyze_open_home_feedback as _analyze_open_home_feedback,
    calculate_breach_status as _calculate_breach_status,
    extract_expiry_date as _extract_expiry_date,
    generate_vendor_report as _generate_vendor_report,
    ocr_document as _ocr_document,
    prepare_breach_notice as _prepare_breach_notice,
    web_search as _web_search,
)

# Import FastMCP server instance
from tenure_mcp.server.fastmcp_server import create_fastmcp_server


def _get_default_context() -> RequestContext:
    """Create a default RequestContext for tool execution.
    
    TODO: Extract from FastMCP request context or FastAPI request when integrated.
    For now, returns a default context for MVP.
    """
    return RequestContext(
        user_id="default_user",
        tenant_id="default_tenant",
        auth_context="default_auth",
        role="agent",
    )


# Get FastMCP server instance (create if not exists)
mcp = create_fastmcp_server()


@mcp.tool()
async def analyze_open_home_feedback(property_id: str) -> AnalyzeFeedbackOutput:
    """Analyze open home feedback for a property.
    
    Returns sentiment categories and comment breakdown.
    """
    input_data = AnalyzeFeedbackInput(property_id=property_id)
    context = _get_default_context()
    return await _analyze_open_home_feedback(input_data, context)


@mcp.tool()
async def calculate_breach_status(tenancy_id: str) -> CalculateBreachOutput:
    """Calculate breach status for a tenancy.
    
    Returns legality and breach risk based on rent status and lease terms.
    """
    input_data = CalculateBreachInput(tenancy_id=tenancy_id)
    context = _get_default_context()
    return await _calculate_breach_status(input_data, context)


@mcp.tool()
async def ocr_document(document_url: str) -> OCRDocumentOutput:
    """Extract text from a document using OCR.
    
    Supports PDF, image, and other document formats.
    """
    input_data = OCRDocumentInput(document_url=document_url)
    context = _get_default_context()
    return await _ocr_document(input_data, context)


@mcp.tool()
async def extract_expiry_date(text: str) -> ExtractExpiryOutput:
    """Extract expiry dates from text content.
    
    Parses common date formats and returns structured expiry information.
    """
    input_data = ExtractExpiryInput(text=text)
    context = _get_default_context()
    return await _extract_expiry_date(input_data, context)


@mcp.tool()
async def generate_vendor_report(property_id: str) -> GenerateVendorReportOutput:
    """Generate a comprehensive vendor report for a property.
    
    Combines property details, feedback analysis, and market trends.
    """
    input_data = GenerateVendorReportInput(property_id=property_id)
    context = _get_default_context()
    return await _generate_vendor_report(input_data, context)


@mcp.tool()
async def prepare_breach_notice(tenancy_id: str) -> PrepareBreachNoticeOutput:
    """Prepare a breach notice document for a tenancy.
    
    Requires HITL (Human-in-the-Loop) approval before execution.
    """
    input_data = PrepareBreachNoticeInput(tenancy_id=tenancy_id)
    context = _get_default_context()
    return await _prepare_breach_notice(input_data, context)


@mcp.tool()
async def web_search(query: str, max_results: int = 5) -> WebSearchOutput:
    """Search the web for current information.
    
    Use when query needs current/external information not in local data.
    """
    input_data = WebSearchInput(query=query, max_results=max_results)
    context = _get_default_context()
    return await _web_search(input_data, context)
