"""Tests for tool implementations."""

import pytest

from mcp.schemas.base import RequestContext
from mcp.schemas.tools import (
    AnalyzeFeedbackInput,
    CalculateBreachInput,
    ExtractExpiryInput,
    OCRDocumentInput,
    WebSearchInput,
)
from mcp.tools.implementations import (
    analyze_open_home_feedback,
    calculate_breach_status,
    extract_expiry_date,
    ocr_document,
    web_search,
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


@pytest.mark.asyncio
async def test_web_search_no_api_key(context):
    """Test web_search when TAVILY_API_KEY is not set returns empty results."""
    input_data = WebSearchInput(query="test query", max_results=3)
    output = await web_search(input_data, context)
    assert output.query == "test query"
    assert output.results == []


@pytest.mark.asyncio
async def test_web_search_mocked_httpx(context, monkeypatch):
    """Test web_search with mocked Tavily API response."""
    from unittest.mock import MagicMock

    async def mock_post(*args, **kwargs):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = lambda: None
        mock_resp.json.return_value = {
            "results": [
                {"title": "Example", "url": "https://example.com", "content": "Snippet text"},
            ],
        }
        return mock_resp

    import mcp.config
    monkeypatch.setattr(mcp.config.settings, "tavily_api_key", "fake-key")
    monkeypatch.setattr(mcp.config.settings, "web_search_max_results", 5)
    import httpx
    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    input_data = WebSearchInput(query="test", max_results=2)
    output = await web_search(input_data, context)
    assert output.query == "test"
    assert len(output.results) == 1
    assert output.results[0].title == "Example"
    assert output.results[0].url == "https://example.com"
    assert output.results[0].snippet == "Snippet text"
