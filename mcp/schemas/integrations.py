"""Integration schemas for Gmail, Google Drive, VaultRE, and Ailo."""

import re
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from mcp.schemas.versioning import VersionedSchema


# =============================================================================
# Enums
# =============================================================================


class PropertyClass(str, Enum):
    """VaultRE property classification."""

    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    RURAL = "rural"
    LAND = "land"
    BUSINESS = "business"


class PropertyStatus(str, Enum):
    """VaultRE property status."""

    PROSPECT = "prospect"
    APPRAISAL = "appraisal"
    LISTING = "listing"
    UNDER_CONTRACT = "under_contract"
    SOLD = "sold"
    WITHDRAWN = "withdrawn"
    LEASED = "leased"
    AVAILABLE = "available"


class ContactType(str, Enum):
    """VaultRE contact type."""

    OWNER = "owner"
    TENANT = "tenant"
    PURCHASER = "purchaser"
    LANDLORD = "landlord"
    VENDOR = "vendor"
    BUYER = "buyer"


class RentFrequency(str, Enum):
    """Ailo rent frequency."""

    WEEKLY = "weekly"
    FORTNIGHTLY = "fortnightly"
    MONTHLY = "monthly"


class ArrearsStatus(str, Enum):
    """Ailo arrears status classification."""

    CURRENT = "current"
    MINOR = "minor"  # 1-7 days
    MODERATE = "moderate"  # 8-14 days
    SEVERE = "severe"  # 15-21 days
    CRITICAL = "critical"  # 21+ days


class GmailLabelType(str, Enum):
    """Gmail label types."""

    INBOX = "INBOX"
    SENT = "SENT"
    DRAFT = "DRAFT"
    SPAM = "SPAM"
    TRASH = "TRASH"
    STARRED = "STARRED"
    IMPORTANT = "IMPORTANT"
    UNREAD = "UNREAD"


class DriveMimeType(str, Enum):
    """Common Google Drive MIME types."""

    PDF = "application/pdf"
    DOC = "application/msword"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    SHEET = "application/vnd.google-apps.spreadsheet"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    FOLDER = "application/vnd.google-apps.folder"
    IMAGE_PNG = "image/png"
    IMAGE_JPEG = "image/jpeg"


# =============================================================================
# Gmail Schemas
# =============================================================================


class MessageHeader(BaseModel):
    """Gmail message header."""

    name: str = Field(..., description="Header name (e.g., From, To, Subject)")
    value: str = Field(..., description="Header value")


class MessageBody(BaseModel):
    """Gmail message body content."""

    size: int = Field(default=0, ge=0, description="Body size in bytes")
    data: Optional[str] = Field(None, description="Base64url encoded body data")


class MessagePart(BaseModel):
    """Gmail message part for multipart messages."""

    part_id: str = Field(..., description="Part identifier")
    mime_type: str = Field(..., description="MIME type of part")
    filename: Optional[str] = Field(None, description="Filename if attachment")
    headers: List[MessageHeader] = Field(default_factory=list)
    body: Optional[MessageBody] = None
    parts: Optional[List["MessagePart"]] = Field(
        None, description="Nested parts for multipart"
    )


class MessagePayload(BaseModel):
    """Gmail message payload structure."""

    mime_type: str = Field(..., description="MIME type of message")
    headers: List[MessageHeader] = Field(default_factory=list)
    body: Optional[MessageBody] = None
    parts: Optional[List[MessagePart]] = Field(
        None, description="Message parts for multipart messages"
    )


class GmailMessage(VersionedSchema):
    """Gmail message schema based on Gmail API v1."""

    id: str = Field(..., min_length=1, description="Immutable message ID")
    thread_id: str = Field(..., min_length=1, description="Thread ID")
    label_ids: List[str] = Field(default_factory=list, description="Applied label IDs")
    snippet: str = Field(default="", max_length=500, description="Message preview")
    internal_date: str = Field(..., description="Creation timestamp in epoch ms")
    payload: Optional[MessagePayload] = Field(None, description="Parsed message content")
    size_estimate: int = Field(default=0, ge=0, description="Estimated size in bytes")
    history_id: Optional[str] = Field(None, description="Last history record ID")

    @field_validator("id", "thread_id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Validate ID format."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("ID must contain only alphanumeric characters, hyphens, or underscores")
        return v


class GmailThread(VersionedSchema):
    """Gmail thread schema."""

    id: str = Field(..., min_length=1, description="Thread ID")
    snippet: str = Field(default="", max_length=500, description="Thread preview")
    history_id: Optional[str] = None
    messages: List[GmailMessage] = Field(default_factory=list, description="Thread messages")


class EmailSummary(BaseModel):
    """Simplified email summary for tool outputs."""

    message_id: str
    thread_id: str
    subject: str
    sender: str
    recipient: str
    snippet: str
    received_at: datetime
    labels: List[str] = Field(default_factory=list)
    has_attachments: bool = False


class ThreadSummary(BaseModel):
    """Simplified thread summary for tool outputs."""

    thread_id: str
    subject: str
    participants: List[str] = Field(default_factory=list)
    message_count: int
    last_message_at: datetime
    snippet: str


class SendEmailResult(BaseModel):
    """Result of sending an email."""

    message_id: str
    thread_id: str
    sent_at: datetime
    success: bool = True
    error_message: Optional[str] = None


# =============================================================================
# Google Drive Schemas
# =============================================================================


class DriveUser(BaseModel):
    """Google Drive user representation."""

    email: str = Field(..., description="User email address")
    display_name: Optional[str] = Field(None, description="Display name")
    photo_link: Optional[str] = Field(None, description="Profile photo URL")


class DrivePermission(BaseModel):
    """Google Drive file permission."""

    id: str = Field(..., description="Permission ID")
    type: str = Field(..., description="Permission type: user, group, domain, anyone")
    role: str = Field(..., description="Permission role: owner, writer, reader")
    email_address: Optional[str] = Field(None, description="Email if type is user/group")


class DriveFile(VersionedSchema):
    """Google Drive file schema based on Drive API v3."""

    id: str = Field(..., min_length=1, description="File ID")
    name: str = Field(..., min_length=1, description="File name")
    mime_type: str = Field(..., description="File MIME type")
    created_time: datetime = Field(..., description="Creation timestamp")
    modified_time: datetime = Field(..., description="Last modification timestamp")
    size: Optional[int] = Field(None, ge=0, description="File size in bytes")
    parents: List[str] = Field(default_factory=list, description="Parent folder IDs")
    web_view_link: Optional[str] = Field(None, description="Link to view in Drive")
    web_content_link: Optional[str] = Field(None, description="Direct download link")
    thumbnail_link: Optional[str] = Field(None, description="Thumbnail image link")
    owners: List[DriveUser] = Field(default_factory=list, description="File owners")
    shared: bool = Field(default=False, description="Whether file is shared")
    trashed: bool = Field(default=False, description="Whether file is in trash")
    description: Optional[str] = Field(None, max_length=1000, description="File description")
    md5_checksum: Optional[str] = Field(None, description="MD5 checksum for content")

    @field_validator("id")
    @classmethod
    def validate_file_id(cls, v: str) -> str:
        """Validate file ID format."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("File ID must contain only alphanumeric characters, hyphens, or underscores")
        return v


class DocumentInfo(BaseModel):
    """Simplified document info for tool outputs."""

    file_id: str
    name: str
    mime_type: str
    size_bytes: Optional[int] = None
    modified_at: datetime
    web_link: Optional[str] = None
    expiry_date: Optional[date] = Field(None, description="Document expiry for compliance")


class DocumentContent(BaseModel):
    """Document content wrapper."""

    file_id: str
    name: str
    mime_type: str
    content: bytes = Field(..., description="File content bytes")
    extracted_text: Optional[str] = Field(None, description="Extracted text if applicable")


class ExpiryAlert(BaseModel):
    """Document expiry alert."""

    file_id: str
    document_name: str
    document_type: str
    expiry_date: date
    days_until_expiry: int
    alert_level: str = Field(..., description="info, warning, or critical")
    property_id: Optional[str] = None


# =============================================================================
# VaultRE Schemas
# =============================================================================


class PropertyAddress(BaseModel):
    """VaultRE property address structure."""

    line1: str = Field(..., min_length=1, description="Street address")
    line2: Optional[str] = Field(None, description="Additional address line")
    suburb: str = Field(..., min_length=1, description="Suburb/city")
    state: str = Field(..., min_length=1, description="State/territory")
    postcode: str = Field(..., min_length=1, description="Postal code")
    country: str = Field(default="Australia", description="Country")

    @property
    def full_address(self) -> str:
        """Get formatted full address."""
        parts = [self.line1]
        if self.line2:
            parts.append(self.line2)
        parts.append(f"{self.suburb} {self.state} {self.postcode}")
        return ", ".join(parts)


class PriceInfo(BaseModel):
    """VaultRE price information."""

    display: str = Field(..., description="Display price (e.g., '$750,000')")
    value: Optional[float] = Field(None, ge=0, description="Numeric price value")
    price_from: Optional[float] = Field(None, ge=0, description="Price range from")
    price_to: Optional[float] = Field(None, ge=0, description="Price range to")
    hidden: bool = Field(default=False, description="Whether price is hidden")


class Agent(BaseModel):
    """VaultRE agent representation."""

    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent full name")
    email: Optional[str] = Field(None, description="Agent email")
    phone: Optional[str] = Field(None, description="Agent phone")
    photo_url: Optional[str] = Field(None, description="Agent photo URL")


class PropertyPhoto(BaseModel):
    """VaultRE property photo."""

    id: str = Field(..., description="Photo ID")
    url: str = Field(..., description="Photo URL")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    caption: Optional[str] = Field(None, description="Photo caption")
    order: int = Field(default=0, ge=0, description="Display order")


class VaultREProperty(VersionedSchema):
    """VaultRE property schema based on VaultRE API v1.3."""

    id: str = Field(..., min_length=1, description="Property ID")
    address: PropertyAddress = Field(..., description="Property address")
    property_class: PropertyClass = Field(..., description="Property classification")
    property_type: str = Field(..., description="Property type (e.g., House, Unit)")
    status: PropertyStatus = Field(..., description="Property status")
    bedrooms: Optional[int] = Field(None, ge=0, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(None, ge=0, description="Number of bathrooms")
    car_spaces: Optional[int] = Field(None, ge=0, description="Number of car spaces")
    land_area: Optional[float] = Field(None, ge=0, description="Land area in sqm")
    building_area: Optional[float] = Field(None, ge=0, description="Building area in sqm")
    price: Optional[PriceInfo] = Field(None, description="Price information")
    agents: List[Agent] = Field(default_factory=list, description="Listing agents")
    photos: List[PropertyPhoto] = Field(default_factory=list, description="Property photos")
    description: Optional[str] = Field(None, description="Property description")
    features: List[str] = Field(default_factory=list, description="Property features")
    created_at: Optional[datetime] = Field(None, description="Record creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")

    @field_validator("id")
    @classmethod
    def validate_property_id(cls, v: str) -> str:
        """Validate property ID format."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Property ID must contain only alphanumeric characters, hyphens, or underscores")
        return v


class VaultREContact(VersionedSchema):
    """VaultRE contact schema."""

    id: str = Field(..., min_length=1, description="Contact ID")
    first_name: str = Field(..., min_length=1, description="First name")
    last_name: str = Field(..., min_length=1, description="Last name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    mobile: Optional[str] = Field(None, description="Mobile number")
    contact_type: ContactType = Field(..., description="Contact type")
    company: Optional[str] = Field(None, description="Company name")
    notes: Optional[str] = Field(None, description="Contact notes")
    property_ids: List[str] = Field(default_factory=list, description="Related property IDs")
    created_at: Optional[datetime] = Field(None, description="Record creation time")

    @property
    def full_name(self) -> str:
        """Get full name."""
        return f"{self.first_name} {self.last_name}"


class PropertyFeedback(VersionedSchema):
    """VaultRE property feedback from inspections."""

    id: str = Field(..., description="Feedback ID")
    property_id: str = Field(..., description="Property ID")
    contact_id: Optional[str] = Field(None, description="Contact ID if linked")
    contact_name: Optional[str] = Field(None, description="Contact name")
    feedback_date: datetime = Field(..., description="Feedback date")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating 1-5")
    interest_level: Optional[str] = Field(None, description="Interest level")
    comments: str = Field(default="", description="Feedback comments")
    source: str = Field(default="open_home", description="Feedback source")


class OpenHome(BaseModel):
    """VaultRE open home event."""

    id: str = Field(..., description="Open home ID")
    property_id: str = Field(..., description="Property ID")
    start_time: datetime = Field(..., description="Start time")
    end_time: datetime = Field(..., description="End time")
    agent_id: Optional[str] = Field(None, description="Hosting agent ID")
    attendee_count: int = Field(default=0, ge=0, description="Number of attendees")
    notes: Optional[str] = Field(None, description="Open home notes")


class PropertySummary(BaseModel):
    """Simplified property summary for tool outputs."""

    property_id: str
    address: str
    property_class: PropertyClass
    status: PropertyStatus
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    price_display: Optional[str] = None
    primary_agent: Optional[str] = None


class PropertyContacts(BaseModel):
    """Property contacts grouped by type."""

    property_id: str
    owners: List[VaultREContact] = Field(default_factory=list)
    tenants: List[VaultREContact] = Field(default_factory=list)
    landlords: List[VaultREContact] = Field(default_factory=list)
    purchasers: List[VaultREContact] = Field(default_factory=list)


class OpenHomeSummary(BaseModel):
    """Simplified open home summary."""

    open_home_id: str
    property_id: str
    property_address: str
    start_time: datetime
    end_time: datetime
    agent_name: Optional[str] = None


# =============================================================================
# Ailo Schemas
# =============================================================================


class PaymentEntry(BaseModel):
    """Ailo payment history entry."""

    id: str = Field(..., description="Payment ID")
    ledger_id: str = Field(..., description="Ledger ID")
    amount: Decimal = Field(..., description="Payment amount")
    payment_date: date = Field(..., description="Payment date")
    payment_type: str = Field(default="rent", description="Payment type")
    reference: Optional[str] = Field(None, description="Payment reference")
    status: str = Field(default="completed", description="Payment status")


class AiloLedger(VersionedSchema):
    """Ailo ledger schema for tenancy financial tracking."""

    id: str = Field(..., min_length=1, description="Ledger ID")
    tenancy_id: str = Field(..., min_length=1, description="Tenancy ID")
    property_id: str = Field(..., min_length=1, description="Property ID")
    current_balance: Decimal = Field(default=Decimal("0.00"), description="Current balance (positive = owing)")
    rent_amount: Decimal = Field(..., gt=0, description="Rent amount per period")
    rent_frequency: RentFrequency = Field(..., description="Rent payment frequency")
    next_due_date: date = Field(..., description="Next rent due date")
    arrears_days: int = Field(default=0, ge=0, description="Days in arrears")
    arrears_status: ArrearsStatus = Field(default=ArrearsStatus.CURRENT, description="Arrears classification")
    payment_history: List[PaymentEntry] = Field(default_factory=list, description="Recent payments")
    last_payment_date: Optional[date] = Field(None, description="Date of last payment")
    last_payment_amount: Optional[Decimal] = Field(None, description="Amount of last payment")

    @field_validator("tenancy_id", "property_id")
    @classmethod
    def validate_ids(cls, v: str) -> str:
        """Validate ID formats."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("ID must contain only alphanumeric characters, hyphens, or underscores")
        return v


class AiloTenant(VersionedSchema):
    """Ailo tenant schema."""

    id: str = Field(..., min_length=1, description="Tenant ID")
    tenancy_id: str = Field(..., min_length=1, description="Tenancy ID")
    name: str = Field(..., min_length=1, description="Tenant full name")
    email: str = Field(..., description="Tenant email")
    phone: Optional[str] = Field(None, description="Tenant phone")
    lease_start: date = Field(..., description="Lease start date")
    lease_end: Optional[date] = Field(None, description="Lease end date")
    is_primary: bool = Field(default=True, description="Whether primary tenant")
    emergency_contact: Optional[str] = Field(None, description="Emergency contact details")


class LedgerSummary(BaseModel):
    """Simplified ledger summary for tool outputs."""

    ledger_id: str
    tenancy_id: str
    property_id: str
    current_balance: float
    rent_amount: float
    arrears_days: int
    arrears_status: ArrearsStatus
    next_due_date: date
    last_payment_date: Optional[date] = None


class ArrearsReport(BaseModel):
    """Arrears report for listing arrears tenancies."""

    tenancy_id: str
    property_id: str
    property_address: str
    tenant_name: str
    tenant_email: Optional[str] = None
    current_balance: float
    arrears_days: int
    arrears_status: ArrearsStatus
    rent_amount: float
    rent_frequency: RentFrequency
    last_payment_date: Optional[date] = None
    recommended_action: str


class CommunicationEntry(BaseModel):
    """Communication history entry."""

    id: str
    type: str = Field(..., description="email, sms, or note")
    direction: str = Field(..., description="inbound or outbound")
    subject: Optional[str] = None
    snippet: str
    timestamp: datetime
    contact_email: Optional[str] = None
    contact_name: Optional[str] = None


class CommunicationHistory(BaseModel):
    """Communication history for a tenancy."""

    tenancy_id: str
    property_id: str
    tenant_name: str
    communications: List[CommunicationEntry] = Field(default_factory=list)
    total_count: int = 0


# =============================================================================
# Unified Output Schemas
# =============================================================================


class ComplianceAlert(BaseModel):
    """Compliance alert for unified output."""

    alert_type: str = Field(..., description="document_expiry, arrears, inspection_due")
    severity: str = Field(..., description="info, warning, critical")
    message: str
    due_date: Optional[date] = None
    related_document_id: Optional[str] = None
    related_tenancy_id: Optional[str] = None


class GmailCollectionResult(BaseModel):
    """Result of Gmail data collection."""

    emails: List[EmailSummary] = Field(default_factory=list)
    threads: List[ThreadSummary] = Field(default_factory=list)
    total_count: int = 0
    collected_at: datetime = Field(default_factory=datetime.now)


class DriveCollectionResult(BaseModel):
    """Result of Drive data collection."""

    documents: List[DocumentInfo] = Field(default_factory=list)
    expiry_alerts: List[ExpiryAlert] = Field(default_factory=list)
    total_count: int = 0
    collected_at: datetime = Field(default_factory=datetime.now)


class VaultRECollectionResult(BaseModel):
    """Result of VaultRE data collection."""

    property: Optional[VaultREProperty] = None
    contacts: PropertyContacts = Field(default_factory=lambda: PropertyContacts(property_id=""))
    feedback: List[PropertyFeedback] = Field(default_factory=list)
    open_homes: List[OpenHome] = Field(default_factory=list)
    collected_at: datetime = Field(default_factory=datetime.now)


class AiloCollectionResult(BaseModel):
    """Result of Ailo data collection."""

    ledger: Optional[AiloLedger] = None
    tenant: Optional[AiloTenant] = None
    payment_history: List[PaymentEntry] = Field(default_factory=list)
    collected_at: datetime = Field(default_factory=datetime.now)


class UnifiedPropertyData(VersionedSchema):
    """Unified property data from all integrations."""

    property_id: str = Field(..., description="Central property identifier")
    property_details: Optional[VaultREProperty] = Field(None, description="Property details from VaultRE")
    owner_contacts: List[VaultREContact] = Field(default_factory=list, description="Owner contacts")
    tenant_info: Optional[AiloTenant] = Field(None, description="Current tenant info")
    financial_status: Optional[LedgerSummary] = Field(None, description="Financial/arrears status")
    recent_communications: List[CommunicationEntry] = Field(default_factory=list, description="Recent comms")
    documents: List[DocumentInfo] = Field(default_factory=list, description="Related documents")
    compliance_alerts: List[ComplianceAlert] = Field(default_factory=list, description="Active alerts")
    collected_at: datetime = Field(default_factory=datetime.now, description="Collection timestamp")


# =============================================================================
# Tool Input/Output Schemas
# =============================================================================


class FetchPropertyEmailsInput(VersionedSchema):
    """Input for fetch_property_emails tool."""

    property_id: str = Field(..., min_length=1, max_length=100, description="Property ID")
    days_back: int = Field(default=30, ge=1, le=365, description="Days to look back")

    @field_validator("property_id")
    @classmethod
    def validate_property_id(cls, v: str) -> str:
        """Validate property ID format."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Property ID must contain only alphanumeric characters, hyphens, or underscores")
        return v


class FetchPropertyEmailsOutput(VersionedSchema):
    """Output for fetch_property_emails tool."""

    property_id: str
    emails: List[EmailSummary] = Field(default_factory=list)
    total_count: int = 0


class SearchCommunicationThreadsInput(VersionedSchema):
    """Input for search_communication_threads tool."""

    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    contact_email: Optional[str] = Field(None, description="Filter by contact email")
    max_results: int = Field(default=10, ge=1, le=50, description="Maximum results")


class SearchCommunicationThreadsOutput(VersionedSchema):
    """Output for search_communication_threads tool."""

    query: str
    threads: List[ThreadSummary] = Field(default_factory=list)
    total_count: int = 0


class ListPropertyDocumentsInput(VersionedSchema):
    """Input for list_property_documents tool."""

    property_id: str = Field(..., min_length=1, max_length=100, description="Property ID")


class ListPropertyDocumentsOutput(VersionedSchema):
    """Output for list_property_documents tool."""

    property_id: str
    documents: List[DocumentInfo] = Field(default_factory=list)
    total_count: int = 0


class GetDocumentContentInput(VersionedSchema):
    """Input for get_document_content tool."""

    file_id: str = Field(..., min_length=1, max_length=100, description="File ID")


class GetDocumentContentOutput(VersionedSchema):
    """Output for get_document_content tool."""

    file_id: str
    name: str
    mime_type: str
    content_preview: str = Field(default="", max_length=5000, description="Content preview/extracted text")
    size_bytes: Optional[int] = None


class CheckDocumentExpiryInput(VersionedSchema):
    """Input for check_document_expiry tool."""

    property_id: str = Field(..., min_length=1, max_length=100, description="Property ID")
    days_ahead: int = Field(default=30, ge=1, le=365, description="Days to look ahead for expiries")


class CheckDocumentExpiryOutput(VersionedSchema):
    """Output for check_document_expiry tool."""

    property_id: str
    alerts: List[ExpiryAlert] = Field(default_factory=list)
    total_count: int = 0


class ListActivePropertiesInput(VersionedSchema):
    """Input for list_active_properties tool."""

    status: Optional[str] = Field(None, description="Filter by status")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum results")


class ListActivePropertiesOutput(VersionedSchema):
    """Output for list_active_properties tool."""

    properties: List[PropertySummary] = Field(default_factory=list)
    total_count: int = 0


class GetPropertyContactsInput(VersionedSchema):
    """Input for get_property_contacts tool."""

    property_id: str = Field(..., min_length=1, max_length=100, description="Property ID")


class GetPropertyContactsOutput(VersionedSchema):
    """Output for get_property_contacts tool."""

    property_id: str
    contacts: PropertyContacts


class GetUpcomingOpenHomesInput(VersionedSchema):
    """Input for get_upcoming_open_homes tool."""

    days_ahead: int = Field(default=7, ge=1, le=30, description="Days to look ahead")


class GetUpcomingOpenHomesOutput(VersionedSchema):
    """Output for get_upcoming_open_homes tool."""

    open_homes: List[OpenHomeSummary] = Field(default_factory=list)
    total_count: int = 0


class ListArrearsTenanciesInput(VersionedSchema):
    """Input for list_arrears_tenancies tool."""

    min_days: int = Field(default=1, ge=1, description="Minimum days in arrears")
    max_results: int = Field(default=20, ge=1, le=100, description="Maximum results")


class ListArrearsTenanciesOutput(VersionedSchema):
    """Output for list_arrears_tenancies tool."""

    arrears_reports: List[ArrearsReport] = Field(default_factory=list)
    total_count: int = 0


class GetTenantCommunicationHistoryInput(VersionedSchema):
    """Input for get_tenant_communication_history tool."""

    tenancy_id: str = Field(..., min_length=1, max_length=100, description="Tenancy ID")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum communications")


class GetTenantCommunicationHistoryOutput(VersionedSchema):
    """Output for get_tenant_communication_history tool."""

    history: CommunicationHistory


class UnifiedDataCollectionInput(VersionedSchema):
    """Input for unified_data_collection workflow."""

    property_id: str = Field(..., min_length=1, max_length=100, description="Property ID")
    collection_scope: List[str] = Field(
        default_factory=lambda: ["gmail", "drive", "vaultre", "ailo"],
        description="Which integrations to collect from",
    )

    @field_validator("collection_scope")
    @classmethod
    def validate_scope(cls, v: List[str]) -> List[str]:
        """Validate collection scope values."""
        valid_scopes = {"gmail", "drive", "vaultre", "ailo"}
        for scope in v:
            if scope not in valid_scopes:
                raise ValueError(f"Invalid scope '{scope}'. Must be one of: {valid_scopes}")
        return v


class UnifiedDataCollectionOutput(VersionedSchema):
    """Output for unified_data_collection workflow."""

    property_id: str
    data: UnifiedPropertyData
    collection_scope: List[str]
    errors: List[str] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
