"""FastAPI server for MCP Server."""

from mcp.server.app import create_app
from mcp.server.sse import sse_app

__all__ = ["create_app", "sse_app"]
