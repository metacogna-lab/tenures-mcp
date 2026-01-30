"""Tests for integration tools (Gmail, Google Drive, VaultRE, Ailo)."""

import pytest

from tenure_mcp.schemas.base import RequestContext
from tenure_mcp.schemas.integrations import (
    CheckDocumentExpiryInput,
    FetchPropertyEmailsInput,
    GetDocumentContentInput,
    GetPropertyContactsInput,
    GetTenantCommunicationHistoryInput,
    GetUpcomingOpenHomesInput,
    ListActivePropertiesInput,
    ListArrearsTenanciesInput,
    ListPropertyDocumentsInput,
    SearchCommunicationThreadsInput,
)
from tenure_mcp.tools.integration_tools import (
    check_document_expiry,
    fetch_property_emails,
    get_document_content,
    get_property_contacts,
    get_tenant_communication_history,
    get_upcoming_open_homes,
    list_active_properties,
    list_arrears_tenancies,
    list_property_documents,
    search_communication_threads,
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


# =============================================================================
# Gmail Integration Tools Tests
# =============================================================================


@pytest.mark.asyncio
async def test_fetch_property_emails(context):
    """Test fetch_property_emails tool returns emails for a property."""
    input_data = FetchPropertyEmailsInput(property_id="prop_001", days_back=30)
    output = await fetch_property_emails(input_data, context)

    assert output.property_id == "prop_001"
    assert isinstance(output.emails, list)
    assert output.total_count >= 0

    # If we got emails, verify structure
    if output.emails:
        email = output.emails[0]
        assert email.message_id
        assert email.thread_id
        assert email.subject
        assert email.sender
        assert email.recipient


@pytest.mark.asyncio
async def test_search_communication_threads(context):
    """Test search_communication_threads tool."""
    input_data = SearchCommunicationThreadsInput(
        query="property inspection",
        max_results=5,
    )
    output = await search_communication_threads(input_data, context)

    assert output.query == "property inspection"
    assert isinstance(output.threads, list)
    assert output.total_count >= 0


# =============================================================================
# Google Drive Integration Tools Tests
# =============================================================================


@pytest.mark.asyncio
async def test_list_property_documents(context):
    """Test list_property_documents tool returns documents for a property."""
    input_data = ListPropertyDocumentsInput(property_id="prop_001")
    output = await list_property_documents(input_data, context)

    assert output.property_id == "prop_001"
    assert isinstance(output.documents, list)
    assert output.total_count >= 0

    # If we got documents, verify structure
    if output.documents:
        doc = output.documents[0]
        assert doc.file_id
        assert doc.name
        assert doc.mime_type


@pytest.mark.asyncio
async def test_get_document_content(context):
    """Test get_document_content tool returns document details."""
    input_data = GetDocumentContentInput(file_id="file_001")
    output = await get_document_content(input_data, context)

    assert output.file_id == "file_001"
    assert output.name
    assert output.mime_type


@pytest.mark.asyncio
async def test_check_document_expiry(context):
    """Test check_document_expiry tool detects expiring documents."""
    input_data = CheckDocumentExpiryInput(property_id="prop_001", days_ahead=30)
    output = await check_document_expiry(input_data, context)

    assert output.property_id == "prop_001"
    assert isinstance(output.alerts, list)

    # Verify alert structure if any
    if output.alerts:
        alert = output.alerts[0]
        assert alert.file_id
        assert alert.document_name
        assert alert.expiry_date
        assert alert.alert_level in ["info", "warning", "critical"]


# =============================================================================
# VaultRE Integration Tools Tests
# =============================================================================


@pytest.mark.asyncio
async def test_list_active_properties(context):
    """Test list_active_properties tool returns property summaries."""
    input_data = ListActivePropertiesInput(limit=10)
    output = await list_active_properties(input_data, context)

    assert isinstance(output.properties, list)
    assert output.total_count >= 0

    # Verify property structure if any
    if output.properties:
        prop = output.properties[0]
        assert prop.property_id
        assert prop.address
        assert prop.property_class
        assert prop.status


@pytest.mark.asyncio
async def test_list_active_properties_with_status_filter(context):
    """Test list_active_properties with status filter."""
    input_data = ListActivePropertiesInput(status="listing", limit=10)
    output = await list_active_properties(input_data, context)

    assert isinstance(output.properties, list)
    # All returned properties should have listing status
    for prop in output.properties:
        assert prop.status.value == "listing"


@pytest.mark.asyncio
async def test_get_property_contacts(context):
    """Test get_property_contacts tool returns contacts grouped by type."""
    input_data = GetPropertyContactsInput(property_id="prop_001")
    output = await get_property_contacts(input_data, context)

    assert output.property_id == "prop_001"
    assert output.contacts is not None
    assert hasattr(output.contacts, "owners")
    assert hasattr(output.contacts, "tenants")
    assert hasattr(output.contacts, "landlords")
    assert hasattr(output.contacts, "purchasers")


@pytest.mark.asyncio
async def test_get_upcoming_open_homes(context):
    """Test get_upcoming_open_homes tool returns scheduled events."""
    input_data = GetUpcomingOpenHomesInput(days_ahead=7)
    output = await get_upcoming_open_homes(input_data, context)

    assert isinstance(output.open_homes, list)
    assert output.total_count >= 0

    # Verify open home structure if any
    if output.open_homes:
        oh = output.open_homes[0]
        assert oh.open_home_id
        assert oh.property_id
        assert oh.property_address
        assert oh.start_time
        assert oh.end_time


# =============================================================================
# Ailo Integration Tools Tests
# =============================================================================


@pytest.mark.asyncio
async def test_list_arrears_tenancies(context):
    """Test list_arrears_tenancies tool returns tenancies in arrears."""
    input_data = ListArrearsTenanciesInput(min_days=1, max_results=10)
    output = await list_arrears_tenancies(input_data, context)

    assert isinstance(output.arrears_reports, list)
    assert output.total_count >= 0

    # Verify arrears report structure if any
    if output.arrears_reports:
        report = output.arrears_reports[0]
        assert report.tenancy_id
        assert report.property_id
        assert report.tenant_name
        assert report.arrears_days >= 1
        assert report.arrears_status
        assert report.recommended_action


@pytest.mark.asyncio
async def test_get_tenant_communication_history(context):
    """Test get_tenant_communication_history tool returns communication records."""
    input_data = GetTenantCommunicationHistoryInput(
        tenancy_id="tenancy_001",
        limit=10,
    )
    output = await get_tenant_communication_history(input_data, context)

    assert output.history is not None
    assert output.history.tenancy_id == "tenancy_001"
    assert output.history.tenant_name
    assert isinstance(output.history.communications, list)


# =============================================================================
# Schema Validation Tests
# =============================================================================


def test_fetch_property_emails_input_validation():
    """Test FetchPropertyEmailsInput validates property_id format."""
    # Valid input
    valid_input = FetchPropertyEmailsInput(property_id="prop_001", days_back=30)
    assert valid_input.property_id == "prop_001"

    # Invalid property ID with special characters
    with pytest.raises(ValueError):
        FetchPropertyEmailsInput(property_id="prop@001", days_back=30)


def test_list_active_properties_input_limits():
    """Test ListActivePropertiesInput enforces limit bounds."""
    # Valid limit
    valid_input = ListActivePropertiesInput(limit=50)
    assert valid_input.limit == 50

    # Max limit is 100
    with pytest.raises(ValueError):
        ListActivePropertiesInput(limit=200)


def test_check_document_expiry_input_days_bounds():
    """Test CheckDocumentExpiryInput enforces days_ahead bounds."""
    # Valid days
    valid_input = CheckDocumentExpiryInput(property_id="prop_001", days_ahead=30)
    assert valid_input.days_ahead == 30

    # Days must be >= 1
    with pytest.raises(ValueError):
        CheckDocumentExpiryInput(property_id="prop_001", days_ahead=0)
