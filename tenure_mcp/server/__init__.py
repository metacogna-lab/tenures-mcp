"""FastAPI server for MCP Server."""

from tenure_mcp.server.app import create_app
from tenure_mcp.server.sse import sse_app

__all__ = ["create_app", "sse_app"]
