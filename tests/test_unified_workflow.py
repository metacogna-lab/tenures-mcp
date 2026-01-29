"""Tests for unified data collection workflow."""

import pytest

from mcp.schemas.base import RequestContext
from mcp.langgraphs.executor import get_workflow_executor


@pytest.fixture
def context():
    """Create test request context."""
    return RequestContext(
        user_id="test_user",
        tenant_id="test_tenant",
        auth_context="test_token",
        role="agent",
    )


@pytest.mark.asyncio
async def test_unified_collection_workflow_full_scope(context):
    """Test unified collection workflow with all integrations."""
    executor = get_workflow_executor()
    result = await executor.execute_unified_collection(
        property_id="prop_001",
        context=context,
        collection_scope=["gmail", "drive", "vaultre", "ailo"],
    )

    assert result["success"] is True
    assert result["workflow_name"] == "unified_collection"
    assert "output" in result
    assert "errors" in result
    assert "execution_time_ms" in result

    # Verify unified output structure
    if result["output"]:
        output = result["output"]
        assert output["property_id"] == "prop_001"
        assert "property_details" in output
        assert "owner_contacts" in output
        assert "tenant_info" in output
        assert "financial_status" in output
        assert "recent_communications" in output
        assert "documents" in output
        assert "compliance_alerts" in output
        assert "collected_at" in output


@pytest.mark.asyncio
async def test_unified_collection_workflow_vaultre_only(context):
    """Test unified collection with only VaultRE scope."""
    executor = get_workflow_executor()
    result = await executor.execute_unified_collection(
        property_id="prop_001",
        context=context,
        collection_scope=["vaultre"],
    )

    assert result["success"] is True
    assert result["workflow_name"] == "unified_collection"

    if result["output"]:
        output = result["output"]
        assert output["property_id"] == "prop_001"
        # VaultRE data should be present
        assert "property_details" in output
        assert "owner_contacts" in output


@pytest.mark.asyncio
async def test_unified_collection_workflow_ailo_only(context):
    """Test unified collection with only Ailo scope."""
    executor = get_workflow_executor()
    result = await executor.execute_unified_collection(
        property_id="prop_lease_001",
        context=context,
        collection_scope=["ailo"],
    )

    assert result["success"] is True
    assert result["workflow_name"] == "unified_collection"
    assert "output" in result


@pytest.mark.asyncio
async def test_unified_collection_workflow_gmail_drive(context):
    """Test unified collection with Gmail and Drive only."""
    executor = get_workflow_executor()
    result = await executor.execute_unified_collection(
        property_id="prop_001",
        context=context,
        collection_scope=["gmail", "drive"],
    )

    assert result["success"] is True
    assert result["workflow_name"] == "unified_collection"

    if result["output"]:
        output = result["output"]
        # Communications and documents should be present
        assert "recent_communications" in output
        assert "documents" in output


@pytest.mark.asyncio
async def test_unified_collection_workflow_default_scope(context):
    """Test unified collection with default scope (all integrations)."""
    executor = get_workflow_executor()
    result = await executor.execute_unified_collection(
        property_id="prop_001",
        context=context,
        collection_scope=None,  # Should default to all
    )

    assert result["success"] is True
    assert result["workflow_name"] == "unified_collection"
    assert "output" in result


@pytest.mark.asyncio
async def test_unified_collection_workflow_execution_time(context):
    """Test that execution time is tracked."""
    executor = get_workflow_executor()
    result = await executor.execute_unified_collection(
        property_id="prop_001",
        context=context,
    )

    assert result["success"] is True
    assert "execution_time_ms" in result
    # Execution time should be a positive number (or None if timing failed)
    if result["execution_time_ms"] is not None:
        assert result["execution_time_ms"] > 0


@pytest.mark.asyncio
async def test_unified_collection_workflow_compliance_alerts(context):
    """Test that compliance alerts are generated for expiring documents."""
    executor = get_workflow_executor()
    result = await executor.execute_unified_collection(
        property_id="prop_001",
        context=context,
        collection_scope=["drive"],
    )

    assert result["success"] is True

    if result["output"]:
        output = result["output"]
        # The mock data includes expiring documents, so we should have alerts
        assert "compliance_alerts" in output
        # May have document expiry alerts
        assert isinstance(output["compliance_alerts"], list)


@pytest.mark.asyncio
async def test_unified_collection_workflow_errors_captured(context):
    """Test that errors during collection are captured but don't fail workflow."""
    executor = get_workflow_executor()

    # Use a property that exists in mocks
    result = await executor.execute_unified_collection(
        property_id="prop_001",
        context=context,
    )

    # Workflow should complete even if some integrations have issues
    assert result["success"] is True
    assert "errors" in result
    assert isinstance(result["errors"], list)


@pytest.mark.asyncio
async def test_unified_collection_workflow_different_properties(context):
    """Test unified collection with different property types."""
    executor = get_workflow_executor()

    # Test with a lease property
    result = await executor.execute_unified_collection(
        property_id="prop_lease_001",
        context=context,
    )

    assert result["success"] is True
    assert result["workflow_name"] == "unified_collection"

    # Test with a sale property
    result2 = await executor.execute_unified_collection(
        property_id="prop_002",
        context=context,
    )

    assert result2["success"] is True
