"""FastMCP-compatible resource implementations.

This module provides FastMCP decorator-based resource registrations that wrap
our existing resource implementations. Resources are registered using FastMCP's
@mcp.resource() decorator pattern.
"""

from opentelemetry import trace

from tenure_mcp.observability import get_tracer
from tenure_mcp.schemas.base import RequestContext

# Get tracer for this module
tracer = get_tracer(__name__)
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
    with tracer.start_as_current_span("resource.get_property_details") as span:
        span.set_attribute("resource.name", "get_property_details")
        span.set_attribute("resource.uri_pattern", "vault://properties/{property_id}/details")
        span.set_attribute("resource.input.property_id", property_id)
        
        try:
            context = _get_default_context()
            result = await _get_property_details_resource(property_id, context)
            span.set_status(trace.Status(trace.StatusCode.OK))
            return result
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


@mcp.resource("vault://properties/{property_id}/feedback")
async def get_property_feedback(property_id: str) -> dict:
    """Get property feedback resource.
    
    URI: vault://properties/{id}/feedback
    Returns open home feedback entries for the property.
    """
    with tracer.start_as_current_span("resource.get_property_feedback") as span:
        span.set_attribute("resource.name", "get_property_feedback")
        span.set_attribute("resource.uri_pattern", "vault://properties/{property_id}/feedback")
        span.set_attribute("resource.input.property_id", property_id)
        
        try:
            context = _get_default_context()
            result = await _get_property_feedback_resource(property_id, context)
            span.set_status(trace.Status(trace.StatusCode.OK))
            return result
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


@mcp.resource("ailo://ledgers/{tenancy_id}/summary")
async def get_ledger_summary(tenancy_id: str) -> dict:
    """Get ledger summary resource.
    
    URI: ailo://ledgers/{tenancy_id}/summary
    Returns ledger balance and arrears status for a tenancy.
    """
    with tracer.start_as_current_span("resource.get_ledger_summary") as span:
        span.set_attribute("resource.name", "get_ledger_summary")
        span.set_attribute("resource.uri_pattern", "ailo://ledgers/{tenancy_id}/summary")
        span.set_attribute("resource.input.tenancy_id", tenancy_id)
        
        try:
            context = _get_default_context()
            result = await _get_ledger_summary_resource(tenancy_id, context)
            span.set_status(trace.Status(trace.StatusCode.OK))
            return result
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


@mcp.resource("vault://properties/{property_id}/documents")
async def get_property_documents(property_id: str) -> dict:
    """Get property documents resource.
    
    URI: vault://properties/{id}/documents
    Returns document URLs (contracts, certificates) for the property.
    """
    with tracer.start_as_current_span("resource.get_property_documents") as span:
        span.set_attribute("resource.name", "get_property_documents")
        span.set_attribute("resource.uri_pattern", "vault://properties/{property_id}/documents")
        span.set_attribute("resource.input.property_id", property_id)
        
        try:
            context = _get_default_context()
            result = await _get_property_documents_resource(property_id, context)
            span.set_status(trace.Status(trace.StatusCode.OK))
            return result
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise
