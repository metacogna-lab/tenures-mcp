"""FastMCP-compatible tool implementations.

This module provides FastMCP decorator-based tool registrations that wrap
our existing tool implementations. Tools are registered using FastMCP's
@mcp.tool() decorator pattern.
"""

from typing import Optional

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
from tenure_mcp.schemas.integrations import (
    CheckDocumentExpiryInput,
    CheckDocumentExpiryOutput,
    FetchPropertyEmailsInput,
    FetchPropertyEmailsOutput,
    GetDocumentContentInput,
    GetDocumentContentOutput,
    GetPropertyContactsInput,
    GetPropertyContactsOutput,
    GetTenantCommunicationHistoryInput,
    GetTenantCommunicationHistoryOutput,
    GetUpcomingOpenHomesInput,
    GetUpcomingOpenHomesOutput,
    ListActivePropertiesInput,
    ListActivePropertiesOutput,
    ListArrearsTenanciesInput,
    ListArrearsTenanciesOutput,
    ListPropertyDocumentsInput,
    ListPropertyDocumentsOutput,
    SearchCommunicationThreadsInput,
    SearchCommunicationThreadsOutput,
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
from tenure_mcp.tools.integration_tools import (
    check_document_expiry as _check_document_expiry,
    fetch_property_emails as _fetch_property_emails,
    get_document_content as _get_document_content,
    get_property_contacts as _get_property_contacts,
    get_tenant_communication_history as _get_tenant_communication_history,
    get_upcoming_open_homes as _get_upcoming_open_homes,
    list_active_properties as _list_active_properties,
    list_arrears_tenancies as _list_arrears_tenancies,
    list_property_documents as _list_property_documents,
    search_communication_threads as _search_communication_threads,
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


# =============================================================================
# Integration Tools (Gmail, Google Drive, VaultRE, Ailo)
# =============================================================================


@mcp.tool()
async def fetch_property_emails(property_id: str, days_back: int = 30) -> FetchPropertyEmailsOutput:
    """Fetch emails related to a specific property.
    
    Retrieves email communications linked to a property within the specified
    time window. Useful for vendor reports and communication history.
    """
    input_data = FetchPropertyEmailsInput(property_id=property_id, days_back=days_back)
    context = _get_default_context()
    return await _fetch_property_emails(input_data, context)


@mcp.tool()
async def search_communication_threads(
    query: str, max_results: int = 10, contact_email: Optional[str] = None
) -> SearchCommunicationThreadsOutput:
    """Search email threads by query and optional contact filter.
    
    Searches through email communications to find relevant threads.
    Useful for finding specific conversations or contact history.
    """
    input_data = SearchCommunicationThreadsInput(
        query=query, max_results=max_results, contact_email=contact_email
    )
    context = _get_default_context()
    return await _search_communication_threads(input_data, context)


@mcp.tool()
async def list_property_documents(property_id: str) -> ListPropertyDocumentsOutput:
    """List all documents associated with a property.
    
    Retrieves document metadata for files linked to a property in Google Drive.
    Includes contracts, inspection reports, certificates, etc.
    """
    input_data = ListPropertyDocumentsInput(property_id=property_id)
    context = _get_default_context()
    return await _list_property_documents(input_data, context)


@mcp.tool()
async def get_document_content(document_id: str) -> GetDocumentContentOutput:
    """Get document metadata and content preview.
    
    Retrieves a document's details and a preview/extract of its content.
    Useful for compliance checks and document review.
    """
    input_data = GetDocumentContentInput(document_id=document_id)
    context = _get_default_context()
    return await _get_document_content(input_data, context)


@mcp.tool()
async def check_document_expiry(property_id: str) -> CheckDocumentExpiryOutput:
    """Check expiry dates for all documents associated with a property.
    
    Scans property documents and identifies any that are expired or expiring soon.
    Useful for compliance monitoring and renewal reminders.
    """
    input_data = CheckDocumentExpiryInput(property_id=property_id)
    context = _get_default_context()
    return await _check_document_expiry(input_data, context)


@mcp.tool()
async def list_active_properties(
    status: Optional[str] = None, property_class: Optional[str] = None
) -> ListActivePropertiesOutput:
    """List active properties from VaultRE.
    
    Retrieves properties matching optional status and class filters.
    Useful for property management and reporting.
    """
    input_data = ListActivePropertiesInput(status=status, property_class=property_class)
    context = _get_default_context()
    return await _list_active_properties(input_data, context)


@mcp.tool()
async def get_property_contacts(property_id: str) -> GetPropertyContactsOutput:
    """Get all contacts associated with a property.
    
    Retrieves contact information for owners, tenants, vendors, etc.
    linked to a specific property in VaultRE.
    """
    input_data = GetPropertyContactsInput(property_id=property_id)
    context = _get_default_context()
    return await _get_property_contacts(input_data, context)


@mcp.tool()
async def get_upcoming_open_homes(
    property_id: Optional[str] = None, days_ahead: int = 30
) -> GetUpcomingOpenHomesOutput:
    """Get upcoming open home appointments.
    
    Retrieves scheduled open home events, optionally filtered by property.
    Useful for scheduling and vendor reports.
    """
    input_data = GetUpcomingOpenHomesInput(property_id=property_id, days_ahead=days_ahead)
    context = _get_default_context()
    return await _get_upcoming_open_homes(input_data, context)


@mcp.tool()
async def list_arrears_tenancies(
    min_days_overdue: int = 0, status: Optional[str] = None
) -> ListArrearsTenanciesOutput:
    """List tenancies with rent arrears from Ailo.
    
    Retrieves tenancies with overdue rent payments, optionally filtered
    by minimum days overdue and status. Useful for arrears management.
    """
    input_data = ListArrearsTenanciesInput(min_days_overdue=min_days_overdue, status=status)
    context = _get_default_context()
    return await _list_arrears_tenancies(input_data, context)


@mcp.tool()
async def get_tenant_communication_history(
    tenancy_id: str, days_back: int = 90
) -> GetTenantCommunicationHistoryOutput:
    """Get communication history for a tenancy.
    
    Retrieves all communications (emails, calls, notes) related to a tenancy.
    Useful for arrears management and tenant relations.
    """
    input_data = GetTenantCommunicationHistoryInput(tenancy_id=tenancy_id, days_back=days_back)
    context = _get_default_context()
    return await _get_tenant_communication_history(input_data, context)
