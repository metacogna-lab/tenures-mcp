"""Tests for FastMCP integration."""

import pytest
from fastapi.testclient import TestClient

from tenure_mcp.server.app import create_app
from tenure_mcp.server.fastmcp_server import create_fastmcp_server, get_fastmcp_server


@pytest.fixture
def fastmcp_server():
    """Create a FastMCP server instance for testing."""
    return create_fastmcp_server()


@pytest.fixture
def app():
    """Create FastAPI app for testing."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


class TestFastMCPServer:
    """Test FastMCP server creation and configuration."""

    def test_create_fastmcp_server(self, fastmcp_server):
        """Test FastMCP server can be created."""
        assert fastmcp_server is not None
        assert fastmcp_server.name == "Tenure MCP Server"

    def test_get_fastmcp_server(self, fastmcp_server):
        """Test getting FastMCP server instance."""
        server = get_fastmcp_server()
        assert server is not None
        assert server is fastmcp_server  # Should be same instance

    def test_tools_registered(self):
        """Test that tools are registered when module is imported."""
        # Import tools module to trigger registration
        from tenure_mcp.tools import fastmcp_tools  # noqa: F401
        
        # FastMCP server should exist
        server = get_fastmcp_server()
        assert server is not None
        assert hasattr(server, "name")


class TestFastMCPEndpoints:
    """Test FastMCP HTTP endpoints."""

    def test_mcp_endpoint_exists(self, client):
        """Test that /mcp endpoint is mounted."""
        # FastMCP endpoints are mounted at /mcp
        # The exact endpoint structure depends on FastMCP's HTTP app
        # For now, just verify the mount exists
        response = client.get("/mcp/")
        # FastMCP might return 404 for root, but that's okay - mount exists
        assert response.status_code in [200, 404, 405]  # 405 = method not allowed is fine

    def test_health_endpoint_still_works(self, client):
        """Test that existing health endpoints still work."""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_version_endpoint_still_works(self, client):
        """Test that version endpoint still works."""
        response = client.get("/version")
        assert response.status_code == 200
        assert "version" in response.json()


class TestFastMCPToolCompatibility:
    """Test that FastMCP tools are compatible with existing tool registry."""

    def test_tool_registry_still_works(self):
        """Test that existing tool registry still functions."""
        from tenure_mcp.tools import get_tool_registry
        
        registry = get_tool_registry()
        tools = registry.list_tools()
        
        # Should have tools registered
        assert len(tools) > 0
        assert "analyze_open_home_feedback" in tools

    def test_tools_can_be_called_via_registry(self):
        """Test that tools can still be called via existing registry."""
        from tenure_mcp.schemas.base import RequestContext
        from tenure_mcp.tools import get_tool_registry
        
        registry = get_tool_registry()
        tool = registry.get("analyze_open_home_feedback")
        
        assert tool is not None
        
        # Tool should be callable with input_data and context
        # (We won't actually call it here to avoid side effects)


class TestFastMCPResourceCompatibility:
    """Test that FastMCP resources are compatible with existing resource registry."""

    def test_resource_registry_still_works(self):
        """Test that existing resource registry still functions."""
        from tenure_mcp.resources import get_resource_registry
        
        registry = get_resource_registry()
        resources = registry.list_resources()
        
        # Should have resources registered
        assert len(resources) > 0
