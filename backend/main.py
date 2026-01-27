"""Main entrypoint for MCP Server."""

import uvicorn

from mcp.config import settings
from mcp.server import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.mcp_server_host,
        port=settings.mcp_server_port,
        reload=True,
    )
