"""Tests for LangGraph workflows."""

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
async def test_weekly_vendor_report_workflow(context):
    """Test WeeklyVendorReportFlow."""
    executor = get_workflow_executor()
    result = await executor.execute_weekly_vendor_report("prop_001", context)

    assert result["success"] is True
    assert result["workflow_name"] == "weekly_vendor_report"
    assert "output" in result
    assert result["output"] is not None


@pytest.mark.asyncio
async def test_arrears_detection_workflow(context):
    """Test ArrearsDetectionFlow."""
    executor = get_workflow_executor()
    result = await executor.execute_arrears_detection("tenancy_001", context)

    assert result["success"] is True
    assert result["workflow_name"] == "arrears_detection"
    assert "output" in result
    assert "classification" in result["output"]


@pytest.mark.asyncio
async def test_compliance_audit_workflow(context):
    """Test ComplianceAuditFlow."""
    executor = get_workflow_executor()
    result = await executor.execute_compliance_audit("prop_001", context)

    assert result["success"] is True
    assert result["workflow_name"] == "compliance_audit"
    assert "output" in result
    assert "compliance_status" in result["output"]
