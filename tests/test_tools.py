"""Tests for tool implementations."""

import pytest

from mcp.schemas.base import RequestContext
from mcp.schemas.tools import (
    AnalyzeFeedbackInput,
    CalculateBreachInput,
    ExtractExpiryInput,
    OCRDocumentInput,
)
from mcp.tools.implementations import (
    analyze_open_home_feedback,
    calculate_breach_status,
    extract_expiry_date,
    ocr_document,
)


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
async def test_analyze_open_home_feedback(context):
    """Test analyze_open_home_feedback tool."""
    input_data = AnalyzeFeedbackInput(property_id="prop_001")
    output = await analyze_open_home_feedback(input_data, context)

    assert output.property_id == "prop_001"
    assert output.total_feedback_count > 0
    assert len(output.sentiment_categories) > 0


@pytest.mark.asyncio
async def test_calculate_breach_status(context):
    """Test calculate_breach_status tool."""
    input_data = CalculateBreachInput(tenancy_id="tenancy_001")
    output = await calculate_breach_status(input_data, context)

    assert output.tenancy_id == "tenancy_001"
    assert output.breach_risk.level in ["low", "medium", "high", "critical"]
    assert output.breach_risk.breach_legal_status in ["compliant", "at_risk", "breached"]


@pytest.mark.asyncio
async def test_ocr_document(context):
    """Test ocr_document tool."""
    input_data = OCRDocumentInput(document_url="https://example.com/doc.pdf")
    output = await ocr_document(input_data, context)

    assert output.document_url == "https://example.com/doc.pdf"
    assert len(output.extracted_text) > 0
    assert output.confidence_score is not None


@pytest.mark.asyncio
async def test_extract_expiry_date(context):
    """Test extract_expiry_date tool."""
    text = "This agreement expires on 15/01/2026. Valid until 31/12/2025."
    input_data = ExtractExpiryInput(text=text)
    output = await extract_expiry_date(input_data, context)

    assert len(output.extracted_dates) > 0
    for date in output.extracted_dates:
        assert date.field_name in ["expiry_date", "valid_until", "end_date"]
        assert date.confidence >= 0.0
        assert date.confidence <= 1.0
