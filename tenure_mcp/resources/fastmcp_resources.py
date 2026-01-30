"""FastMCP-compatible resource implementations.

This module provides FastMCP decorator-based resource registrations that wrap
our existing resource implementations. Resources are registered using FastMCP's
@mcp.resource() decorator pattern.
"""

from tenure_mcp.schemas.base import RequestContext
from tenure_mcp.resources.implementations import (
    get_ledger_summary_resource as _get_ledger_summary_resource,
    get_property_details_resource as _get_property_details_resource,
    get_property_documents_resource as _get_property_documents_resource,
    get_property_feedback_resource as _get_property_feedback_resource,
)

# Import FastMCP server instance
from tenure_mcp.server.fastmcp_server import create_fastmcp_server


def _get_default_context() -> RequestContext:
    """Create a default RequestContext for resource access.
    
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


@mcp.resource("vault://properties/{property_id}/details")
async def get_property_details(property_id: str) -> dict:
    """Get property details resource.
    
    URI: vault://properties/{id}/details
    Returns property listing summary with address, type, bedrooms, etc.
    """
    context = _get_default_context()
    return await _get_property_details_resource(property_id, context)


@mcp.resource("vault://properties/{property_id}/feedback")
async def get_property_feedback(property_id: str) -> dict:
    """Get property feedback resource.
    
    URI: vault://properties/{id}/feedback
    Returns open home feedback entries for the property.
    """
    context = _get_default_context()
    return await _get_property_feedback_resource(property_id, context)


@mcp.resource("ailo://ledgers/{tenancy_id}/summary")
async def get_ledger_summary(tenancy_id: str) -> dict:
    """Get ledger summary resource.
    
    URI: ailo://ledgers/{tenancy_id}/summary
    Returns ledger balance and arrears status for a tenancy.
    """
    context = _get_default_context()
    return await _get_ledger_summary_resource(tenancy_id, context)


@mcp.resource("vault://properties/{property_id}/documents")
async def get_property_documents(property_id: str) -> dict:
    """Get property documents resource.
    
    URI: vault://properties/{id}/documents
    Returns document URLs (contracts, certificates) for the property.
    """
    context = _get_default_context()
    return await _get_property_documents_resource(property_id, context)
