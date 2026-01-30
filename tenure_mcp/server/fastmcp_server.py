"""FastMCP server integration for Tenure MCP Server.

This module creates a FastMCP server instance and provides integration
with the existing FastAPI application.
"""

from typing import Optional

from fastmcp import FastMCP

from tenure_mcp.config import settings


# Global FastMCP server instance
_fastmcp_server: Optional[FastMCP] = None


def create_fastmcp_server() -> FastMCP:
    """Create and configure FastMCP server instance.
    
    Returns:
        FastMCP: Configured FastMCP server instance
    """
    global _fastmcp_server
    
    if _fastmcp_server is None:
        _fastmcp_server = FastMCP(
            name="Tenure MCP Server",
        )
    
    return _fastmcp_server


def get_fastmcp_server() -> FastMCP:
    """Get the global FastMCP server instance.
    
    Returns:
        FastMCP: The FastMCP server instance
        
    Raises:
        RuntimeError: If server has not been created yet
    """
    if _fastmcp_server is None:
        raise RuntimeError("FastMCP server has not been created. Call create_fastmcp_server() first.")
    return _fastmcp_server
