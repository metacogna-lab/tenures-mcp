"""Integration tools for Gmail, Google Drive, VaultRE, and Ailo."""

from datetime import date, datetime, timedelta
from typing import Optional

from tenure_mcp.middleware.clients import (
    get_ailo_client,
    get_gmail_client,
    get_google_drive_client,
    get_vaultre_client,
)
from tenure_mcp.schemas.base import RequestContext
from tenure_mcp.schemas.integrations import (
    ArrearsReport,
    ArrearsStatus,
    CheckDocumentExpiryInput,
    CheckDocumentExpiryOutput,
    CommunicationEntry,
    CommunicationHistory,
    FetchPropertyEmailsInput,
    FetchPropertyEmailsOutput,
    GetDocumentContentInput,
    GetDocumentContentOutput,
    GetPropertyContactsInput,
    GetPropertyContactsOutput,
    GetTenantCommunicationHistoryInput,
    GetTenantCommunicationHistoryOutput,
    GetUpcomingOpenHomesInput,
    GetUpcomingOpenHomesOutput,
    ListActivePropertiesInput,
    ListActivePropertiesOutput,
    ListArrearsTenanciesInput,
    ListArrearsTenanciesOutput,
    ListPropertyDocumentsInput,
    ListPropertyDocumentsOutput,
    OpenHomeSummary,
    SearchCommunicationThreadsInput,
    SearchCommunicationThreadsOutput,
    ThreadSummary,
)


# =============================================================================
# Gmail Tools
# =============================================================================


async def fetch_property_emails(
    input_data: FetchPropertyEmailsInput, context: RequestContext
) -> FetchPropertyEmailsOutput:
    """Fetch emails related to a specific property.
    
    Retrieves email communications linked to a property within the specified
    time window. Useful for vendor reports and communication history.
    """
    client = get_gmail_client()

    # Get emails for the property
    emails = await client.get_property_emails(
        property_id=input_data.property_id,
        days_back=input_data.days_back,
    )

    return FetchPropertyEmailsOutput(
        property_id=input_data.property_id,
        emails=emails,
        total_count=len(emails),
    )


async def search_communication_threads(
    input_data: SearchCommunicationThreadsInput, context: RequestContext
) -> SearchCommunicationThreadsOutput:
    """Search email threads by query and optional contact filter.
    
    Searches through email communications to find relevant threads.
    Useful for finding specific conversations or contact history.
    """
    client = get_gmail_client()

    # Search threads
    threads = await client.search_threads(
        query=input_data.query,
        max_results=input_data.max_results,
    )

    # Convert to ThreadSummary
    thread_summaries = [
        ThreadSummary(
            thread_id=t.id,
            subject=t.snippet[:100] if t.snippet else "No subject",
            participants=[],  # Would be populated from thread messages
            message_count=len(t.messages),
            last_message_at=datetime.now(),  # Would be from latest message
            snippet=t.snippet,
        )
        for t in threads
    ]

    # Filter by contact email if provided
    if input_data.contact_email:
        # In a real implementation, we'd filter by participant email
        pass

    return SearchCommunicationThreadsOutput(
        query=input_data.query,
        threads=thread_summaries,
        total_count=len(thread_summaries),
    )


# =============================================================================
# Google Drive Tools
# =============================================================================


async def list_property_documents(
    input_data: ListPropertyDocumentsInput, context: RequestContext
) -> ListPropertyDocumentsOutput:
    """List all documents associated with a property.
    
    Retrieves document metadata for files linked to a property in Google Drive.
    Includes contracts, inspection reports, certificates, etc.
    """
    client = get_google_drive_client()

    # Get documents for the property
    documents = await client.get_property_documents(
        property_id=input_data.property_id,
    )

    return ListPropertyDocumentsOutput(
        property_id=input_data.property_id,
        documents=documents,
        total_count=len(documents),
    )


async def get_document_content(
    input_data: GetDocumentContentInput, context: RequestContext
) -> GetDocumentContentOutput:
    """Get document metadata and content preview.
    
    Retrieves a document's details and a preview/extract of its content.
    Useful for compliance checks and document review.
    """
    client = get_google_drive_client()

    # Get file metadata
    file = await client.get_file(input_data.file_id)

    if not file:
        return GetDocumentContentOutput(
            file_id=input_data.file_id,
            name="Not Found",
            mime_type="unknown",
            content_preview="Document not found",
        )

    # Get content (mock returns placeholder)
    content = await client.get_file_content(input_data.file_id)

    return GetDocumentContentOutput(
        file_id=input_data.file_id,
        name=file.name,
        mime_type=file.mime_type,
        content_preview=content.decode("utf-8", errors="ignore")[:5000],
        size_bytes=file.size,
    )


async def check_document_expiry(
    input_data: CheckDocumentExpiryInput, context: RequestContext
) -> CheckDocumentExpiryOutput:
    """Check for documents nearing or past expiry for compliance.
    
    Scans documents associated with a property for expiry dates and
    generates alerts for items requiring attention. Critical for
    compliance management (smoke alarms, pool safety, etc.).
    """
    client = get_google_drive_client()

    # Get expiry alerts
    alerts = await client.check_document_expiry(
        property_id=input_data.property_id,
        days_ahead=input_data.days_ahead,
    )

    return CheckDocumentExpiryOutput(
        property_id=input_data.property_id,
        alerts=alerts,
        total_count=len(alerts),
    )


# =============================================================================
# VaultRE Tools
# =============================================================================


async def list_active_properties(
    input_data: ListActivePropertiesInput, context: RequestContext
) -> ListActivePropertiesOutput:
    """List active properties with optional status filter.
    
    Retrieves a summary list of properties from VaultRE CRM.
    Useful for portfolio overview and status tracking.
    """
    client = get_vaultre_client()

    # Get property summaries
    summaries = await client.get_property_summaries(
        status=input_data.status,
        limit=input_data.limit,
    )

    return ListActivePropertiesOutput(
        properties=summaries,
        total_count=len(summaries),
    )


async def get_property_contacts(
    input_data: GetPropertyContactsInput, context: RequestContext
) -> GetPropertyContactsOutput:
    """Get all contacts associated with a property grouped by type.
    
    Retrieves contacts (owners, tenants, landlords, purchasers) linked
    to a property. Useful for communication and stakeholder management.
    """
    client = get_vaultre_client()

    # Get contacts grouped by type
    contacts = await client.get_property_contacts(
        property_id=input_data.property_id,
    )

    return GetPropertyContactsOutput(
        property_id=input_data.property_id,
        contacts=contacts,
    )


async def get_upcoming_open_homes(
    input_data: GetUpcomingOpenHomesInput, context: RequestContext
) -> GetUpcomingOpenHomesOutput:
    """Get upcoming open home events within specified days.
    
    Retrieves scheduled open homes for all properties.
    Useful for agent scheduling and vendor updates.
    """
    client = get_vaultre_client()

    # Get upcoming open homes
    open_homes = await client.list_upcoming_open_homes(
        days_ahead=input_data.days_ahead,
    )

    # Get property details for addresses
    summaries = []
    for oh in open_homes:
        # In a real implementation, we'd batch fetch property details
        prop = await client.get_property(oh.property_id)
        summaries.append(
            OpenHomeSummary(
                open_home_id=oh.id,
                property_id=oh.property_id,
                property_address=prop.address.full_address if prop else "Unknown",
                start_time=oh.start_time,
                end_time=oh.end_time,
                agent_name=None,  # Would fetch from agent registry
            )
        )

    return GetUpcomingOpenHomesOutput(
        open_homes=summaries,
        total_count=len(summaries),
    )


# =============================================================================
# Ailo Tools
# =============================================================================


async def list_arrears_tenancies(
    input_data: ListArrearsTenanciesInput, context: RequestContext
) -> ListArrearsTenanciesOutput:
    """List tenancies currently in arrears.
    
    Retrieves tenancies with rent arrears above the specified threshold.
    Essential for property management and breach detection workflows.
    """
    client = get_ailo_client()
    vaultre_client = get_vaultre_client()

    # Get arrears ledgers
    ledgers = await client.list_arrears(
        min_days=input_data.min_days,
        max_results=input_data.max_results,
    )

    # Build arrears reports
    reports = []
    for ledger in ledgers:
        # Get tenant details
        tenant = await client.get_tenant_details(ledger.tenancy_id)

        # Get property address (would typically come from a property lookup)
        property_address = f"Property {ledger.property_id}"

        # Determine recommended action based on arrears status
        if ledger.arrears_status == ArrearsStatus.CRITICAL:
            action = "Initiate breach notice and legal review"
        elif ledger.arrears_status == ArrearsStatus.SEVERE:
            action = "Issue breach notice immediately"
        elif ledger.arrears_status == ArrearsStatus.MODERATE:
            action = "Send formal reminder and schedule call"
        else:
            action = "Send friendly payment reminder"

        reports.append(
            ArrearsReport(
                tenancy_id=ledger.tenancy_id,
                property_id=ledger.property_id,
                property_address=property_address,
                tenant_name=tenant.name if tenant else "Unknown",
                tenant_email=tenant.email if tenant else None,
                current_balance=float(ledger.current_balance),
                arrears_days=ledger.arrears_days,
                arrears_status=ledger.arrears_status,
                rent_amount=float(ledger.rent_amount),
                rent_frequency=ledger.rent_frequency,
                last_payment_date=ledger.last_payment_date,
                recommended_action=action,
            )
        )

    return ListArrearsTenanciesOutput(
        arrears_reports=reports,
        total_count=len(reports),
    )


async def get_tenant_communication_history(
    input_data: GetTenantCommunicationHistoryInput, context: RequestContext
) -> GetTenantCommunicationHistoryOutput:
    """Get communication history for a tenancy.
    
    Retrieves email and other communications related to a tenant/tenancy.
    Combines data from Gmail and internal notes for a complete picture.
    """
    ailo_client = get_ailo_client()
    gmail_client = get_gmail_client()

    # Get tenant details
    tenant = await ailo_client.get_tenant_details(input_data.tenancy_id)
    ledger = await ailo_client.get_ledger(input_data.tenancy_id)

    if not tenant:
        return GetTenantCommunicationHistoryOutput(
            history=CommunicationHistory(
                tenancy_id=input_data.tenancy_id,
                property_id="unknown",
                tenant_name="Unknown",
                communications=[],
                total_count=0,
            )
        )

    # Get emails related to tenant
    emails = await gmail_client.get_property_emails(
        property_id=ledger.property_id if ledger else "unknown",
        days_back=90,  # Last 3 months
    )

    # Filter emails to/from tenant and convert to CommunicationEntry
    communications = []
    for email in emails:
        if tenant.email and (
            tenant.email.lower() in email.sender.lower()
            or tenant.email.lower() in email.recipient.lower()
        ):
            communications.append(
                CommunicationEntry(
                    id=email.message_id,
                    type="email",
                    direction="inbound" if tenant.email.lower() in email.sender.lower() else "outbound",
                    subject=email.subject,
                    snippet=email.snippet,
                    timestamp=email.received_at,
                    contact_email=tenant.email,
                    contact_name=tenant.name,
                )
            )

    # Sort by timestamp descending
    communications.sort(key=lambda x: x.timestamp, reverse=True)
    communications = communications[: input_data.limit]

    return GetTenantCommunicationHistoryOutput(
        history=CommunicationHistory(
            tenancy_id=input_data.tenancy_id,
            property_id=ledger.property_id if ledger else "unknown",
            tenant_name=tenant.name,
            communications=communications,
            total_count=len(communications),
        )
    )
