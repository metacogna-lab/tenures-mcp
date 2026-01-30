"""Mock clients for Gmail, Google Drive, VaultRE, and Ailo integrations."""

import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from tenure_mcp.config import settings
from tenure_mcp.schemas.integrations import (
    Agent,
    AiloLedger,
    AiloTenant,
    ArrearsStatus,
    ContactType,
    DocumentInfo,
    DriveFile,
    DriveUser,
    EmailSummary,
    ExpiryAlert,
    GmailMessage,
    GmailThread,
    LedgerSummary,
    MessageHeader,
    MessagePayload,
    OpenHome,
    PaymentEntry,
    PriceInfo,
    PropertyAddress,
    PropertyClass,
    PropertyContacts,
    PropertyFeedback,
    PropertyPhoto,
    PropertyStatus,
    PropertySummary,
    RentFrequency,
    SendEmailResult,
    ThreadSummary,
    VaultREContact,
    VaultREProperty,
)


class BaseIntegrationClient(ABC):
    """Base class for integration clients."""

    def __init__(self, mock_enabled: bool = True):
        """Initialize client."""
        self.mock_enabled = mock_enabled

    async def _simulate_latency(self) -> None:
        """Simulate network latency."""
        if self.mock_enabled:
            latency_ms = settings.mock_latency_ms
            await asyncio.sleep(latency_ms / 1000.0)

    @abstractmethod
    async def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """Get property details."""
        pass


# =============================================================================
# Gmail Client
# =============================================================================


class GmailClient(BaseIntegrationClient):
    """Mock Gmail client for email integration."""

    def __init__(self, mock_enabled: bool = True):
        """Initialize Gmail client."""
        super().__init__(mock_enabled)
        if not mock_enabled and not settings.production_integrations_enabled:
            raise NotImplementedError("Production Gmail integration not enabled in MVP")

    async def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """Not applicable for Gmail - returns empty dict."""
        return {}

    async def list_messages(
        self,
        query: Optional[str] = None,
        max_results: int = 20,
        property_id: Optional[str] = None,
    ) -> List[GmailMessage]:
        """List email messages with optional filtering."""
        await self._simulate_latency()

        # Mock messages related to property
        messages = [
            GmailMessage(
                id=f"msg_{uuid.uuid4().hex[:12]}",
                thread_id=f"thread_{uuid.uuid4().hex[:8]}",
                label_ids=["INBOX", "IMPORTANT"],
                snippet="Thank you for the property inspection. The property at 123 Main St looks great...",
                internal_date=str(int((datetime.now() - timedelta(days=1)).timestamp() * 1000)),
                payload=MessagePayload(
                    mime_type="text/plain",
                    headers=[
                        MessageHeader(name="From", value="vendor@example.com"),
                        MessageHeader(name="To", value="agent@raywhite.com"),
                        MessageHeader(name="Subject", value="Re: Property Inspection - 123 Main St"),
                    ],
                ),
                size_estimate=2048,
            ),
            GmailMessage(
                id=f"msg_{uuid.uuid4().hex[:12]}",
                thread_id=f"thread_{uuid.uuid4().hex[:8]}",
                label_ids=["INBOX"],
                snippet="I would like to schedule a viewing for the property listed at...",
                internal_date=str(int((datetime.now() - timedelta(days=2)).timestamp() * 1000)),
                payload=MessagePayload(
                    mime_type="text/plain",
                    headers=[
                        MessageHeader(name="From", value="buyer@example.com"),
                        MessageHeader(name="To", value="agent@raywhite.com"),
                        MessageHeader(name="Subject", value="Property Viewing Request"),
                    ],
                ),
                size_estimate=1024,
            ),
            GmailMessage(
                id=f"msg_{uuid.uuid4().hex[:12]}",
                thread_id=f"thread_{uuid.uuid4().hex[:8]}",
                label_ids=["SENT"],
                snippet="Following up on the open home last weekend. We had 15 groups through...",
                internal_date=str(int((datetime.now() - timedelta(days=3)).timestamp() * 1000)),
                payload=MessagePayload(
                    mime_type="text/plain",
                    headers=[
                        MessageHeader(name="From", value="agent@raywhite.com"),
                        MessageHeader(name="To", value="vendor@example.com"),
                        MessageHeader(name="Subject", value="Weekly Vendor Update"),
                    ],
                ),
                size_estimate=3072,
            ),
        ]

        # Filter by query if provided
        if query:
            query_lower = query.lower()
            messages = [m for m in messages if query_lower in m.snippet.lower()]

        return messages[:max_results]

    async def get_message(self, message_id: str) -> Optional[GmailMessage]:
        """Get a single email message by ID."""
        await self._simulate_latency()

        return GmailMessage(
            id=message_id,
            thread_id=f"thread_{uuid.uuid4().hex[:8]}",
            label_ids=["INBOX"],
            snippet="This is the full message content preview...",
            internal_date=str(int(datetime.now().timestamp() * 1000)),
            payload=MessagePayload(
                mime_type="text/plain",
                headers=[
                    MessageHeader(name="From", value="sender@example.com"),
                    MessageHeader(name="To", value="agent@raywhite.com"),
                    MessageHeader(name="Subject", value="Property Inquiry"),
                ],
            ),
            size_estimate=1500,
        )

    async def search_threads(
        self, query: str, max_results: int = 10
    ) -> List[GmailThread]:
        """Search email threads."""
        await self._simulate_latency()

        threads = [
            GmailThread(
                id=f"thread_{uuid.uuid4().hex[:8]}",
                snippet="Discussion about property valuation and market trends...",
                messages=[],
            ),
            GmailThread(
                id=f"thread_{uuid.uuid4().hex[:8]}",
                snippet="Open home scheduling and feedback collection...",
                messages=[],
            ),
        ]

        return threads[:max_results]

    async def get_property_emails(
        self, property_id: str, days_back: int = 30
    ) -> List[EmailSummary]:
        """Get emails related to a specific property."""
        await self._simulate_latency()

        cutoff = datetime.now() - timedelta(days=days_back)

        return [
            EmailSummary(
                message_id=f"msg_{uuid.uuid4().hex[:12]}",
                thread_id=f"thread_{uuid.uuid4().hex[:8]}",
                subject=f"Property Update - {property_id}",
                sender="vendor@example.com",
                recipient="agent@raywhite.com",
                snippet="Thank you for the weekly update on our property...",
                received_at=datetime.now() - timedelta(days=1),
                labels=["INBOX", "IMPORTANT"],
                has_attachments=False,
            ),
            EmailSummary(
                message_id=f"msg_{uuid.uuid4().hex[:12]}",
                thread_id=f"thread_{uuid.uuid4().hex[:8]}",
                subject=f"Open Home Report - {property_id}",
                sender="agent@raywhite.com",
                recipient="vendor@example.com",
                snippet="Attached is the open home report from this weekend...",
                received_at=datetime.now() - timedelta(days=3),
                labels=["SENT"],
                has_attachments=True,
            ),
            EmailSummary(
                message_id=f"msg_{uuid.uuid4().hex[:12]}",
                thread_id=f"thread_{uuid.uuid4().hex[:8]}",
                subject="Buyer Inquiry",
                sender="buyer@example.com",
                recipient="agent@raywhite.com",
                snippet="I'm interested in the property and would like to arrange a private inspection...",
                received_at=datetime.now() - timedelta(days=5),
                labels=["INBOX"],
                has_attachments=False,
            ),
        ]

    async def send_notification(
        self, to: str, subject: str, body: str
    ) -> SendEmailResult:
        """Send an email notification (mock - does not actually send)."""
        await self._simulate_latency()

        return SendEmailResult(
            message_id=f"msg_{uuid.uuid4().hex[:12]}",
            thread_id=f"thread_{uuid.uuid4().hex[:8]}",
            sent_at=datetime.now(),
            success=True,
        )


# =============================================================================
# Google Drive Client
# =============================================================================


class GoogleDriveClient(BaseIntegrationClient):
    """Mock Google Drive client for document storage integration."""

    def __init__(self, mock_enabled: bool = True):
        """Initialize Google Drive client."""
        super().__init__(mock_enabled)
        if not mock_enabled and not settings.production_integrations_enabled:
            raise NotImplementedError("Production Google Drive integration not enabled in MVP")

    async def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """Not applicable for Google Drive - returns empty dict."""
        return {}

    async def list_files(
        self,
        folder_id: Optional[str] = None,
        mime_type: Optional[str] = None,
        property_id: Optional[str] = None,
        max_results: int = 50,
    ) -> List[DriveFile]:
        """List files in Drive with optional filtering."""
        await self._simulate_latency()

        files = [
            DriveFile(
                id=f"file_{uuid.uuid4().hex[:12]}",
                name="Contract_of_Sale.pdf",
                mime_type="application/pdf",
                created_time=datetime.now() - timedelta(days=30),
                modified_time=datetime.now() - timedelta(days=5),
                size=256000,
                parents=[folder_id or "root"],
                web_view_link="https://drive.google.com/file/d/example1/view",
                owners=[DriveUser(email="agent@raywhite.com", display_name="Ray White Agent")],
                shared=True,
            ),
            DriveFile(
                id=f"file_{uuid.uuid4().hex[:12]}",
                name="Building_Inspection_Report.pdf",
                mime_type="application/pdf",
                created_time=datetime.now() - timedelta(days=60),
                modified_time=datetime.now() - timedelta(days=60),
                size=512000,
                parents=[folder_id or "root"],
                web_view_link="https://drive.google.com/file/d/example2/view",
                owners=[DriveUser(email="inspector@example.com", display_name="Building Inspector")],
                shared=True,
            ),
            DriveFile(
                id=f"file_{uuid.uuid4().hex[:12]}",
                name="Strata_Report.pdf",
                mime_type="application/pdf",
                created_time=datetime.now() - timedelta(days=45),
                modified_time=datetime.now() - timedelta(days=45),
                size=384000,
                parents=[folder_id or "root"],
                web_view_link="https://drive.google.com/file/d/example3/view",
                owners=[DriveUser(email="strata@example.com", display_name="Strata Manager")],
                shared=True,
            ),
            DriveFile(
                id=f"file_{uuid.uuid4().hex[:12]}",
                name="Smoke_Alarm_Certificate.pdf",
                mime_type="application/pdf",
                created_time=datetime.now() - timedelta(days=350),
                modified_time=datetime.now() - timedelta(days=350),
                size=128000,
                parents=[folder_id or "root"],
                web_view_link="https://drive.google.com/file/d/example4/view",
                owners=[DriveUser(email="agent@raywhite.com", display_name="Ray White Agent")],
                shared=False,
                description="Expires in 15 days",
            ),
        ]

        # Filter by MIME type if specified
        if mime_type:
            files = [f for f in files if f.mime_type == mime_type]

        return files[:max_results]

    async def get_file(self, file_id: str) -> Optional[DriveFile]:
        """Get file metadata by ID."""
        await self._simulate_latency()

        return DriveFile(
            id=file_id,
            name="Document.pdf",
            mime_type="application/pdf",
            created_time=datetime.now() - timedelta(days=30),
            modified_time=datetime.now() - timedelta(days=1),
            size=256000,
            parents=["root"],
            web_view_link=f"https://drive.google.com/file/d/{file_id}/view",
            owners=[DriveUser(email="agent@raywhite.com", display_name="Ray White Agent")],
            shared=True,
        )

    async def get_file_content(self, file_id: str) -> bytes:
        """Get file content (mock returns placeholder bytes)."""
        await self._simulate_latency()

        # Mock content - in production would return actual file bytes
        return b"Mock file content for " + file_id.encode()

    async def upload_file(
        self,
        name: str,
        content: bytes,
        mime_type: str,
        folder_id: Optional[str] = None,
    ) -> DriveFile:
        """Upload a file to Drive (mock - does not actually upload)."""
        await self._simulate_latency()

        return DriveFile(
            id=f"file_{uuid.uuid4().hex[:12]}",
            name=name,
            mime_type=mime_type,
            created_time=datetime.now(),
            modified_time=datetime.now(),
            size=len(content),
            parents=[folder_id or "root"],
            web_view_link="https://drive.google.com/file/d/new/view",
            owners=[DriveUser(email="agent@raywhite.com", display_name="Ray White Agent")],
            shared=False,
        )

    async def get_property_documents(
        self, property_id: str
    ) -> List[DocumentInfo]:
        """Get documents associated with a property."""
        await self._simulate_latency()

        return [
            DocumentInfo(
                file_id=f"file_{uuid.uuid4().hex[:12]}",
                name="Contract_of_Sale.pdf",
                mime_type="application/pdf",
                size_bytes=256000,
                modified_at=datetime.now() - timedelta(days=5),
                web_link="https://drive.google.com/file/d/example1/view",
                expiry_date=None,
            ),
            DocumentInfo(
                file_id=f"file_{uuid.uuid4().hex[:12]}",
                name="Building_Inspection_Report.pdf",
                mime_type="application/pdf",
                size_bytes=512000,
                modified_at=datetime.now() - timedelta(days=60),
                web_link="https://drive.google.com/file/d/example2/view",
                expiry_date=None,
            ),
            DocumentInfo(
                file_id=f"file_{uuid.uuid4().hex[:12]}",
                name="Smoke_Alarm_Certificate.pdf",
                mime_type="application/pdf",
                size_bytes=128000,
                modified_at=datetime.now() - timedelta(days=350),
                web_link="https://drive.google.com/file/d/example4/view",
                expiry_date=date.today() + timedelta(days=15),
            ),
            DocumentInfo(
                file_id=f"file_{uuid.uuid4().hex[:12]}",
                name="Pool_Safety_Certificate.pdf",
                mime_type="application/pdf",
                size_bytes=96000,
                modified_at=datetime.now() - timedelta(days=700),
                web_link="https://drive.google.com/file/d/example5/view",
                expiry_date=date.today() - timedelta(days=5),  # Expired
            ),
        ]

    async def check_document_expiry(
        self, property_id: str, days_ahead: int = 30
    ) -> List[ExpiryAlert]:
        """Check for documents nearing expiry."""
        await self._simulate_latency()

        alerts = []
        docs = await self.get_property_documents(property_id)

        for doc in docs:
            if doc.expiry_date:
                days_until = (doc.expiry_date - date.today()).days

                if days_until < 0:
                    alert_level = "critical"
                elif days_until <= 7:
                    alert_level = "critical"
                elif days_until <= days_ahead:
                    alert_level = "warning"
                else:
                    continue

                alerts.append(
                    ExpiryAlert(
                        file_id=doc.file_id,
                        document_name=doc.name,
                        document_type=doc.mime_type,
                        expiry_date=doc.expiry_date,
                        days_until_expiry=days_until,
                        alert_level=alert_level,
                        property_id=property_id,
                    )
                )

        return sorted(alerts, key=lambda x: x.days_until_expiry)


# =============================================================================
# VaultRE Client (Extended)
# =============================================================================


class VaultREClient(BaseIntegrationClient):
    """Mock VaultRE client for real estate CRM integration."""

    def __init__(self, mock_enabled: bool = True):
        """Initialize VaultRE client."""
        super().__init__(mock_enabled)
        if not mock_enabled and not settings.production_integrations_enabled:
            raise NotImplementedError("Production VaultRE integration not enabled in MVP")

    async def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """Get property details from VaultRE (legacy dict return)."""
        await self._simulate_latency()
        return {
            "property_id": property_id,
            "address": "123 Main Street, Brisbane QLD 4000",
            "status": "For Sale",
        }

    async def get_property(self, property_id: str) -> VaultREProperty:
        """Get full property details as typed schema."""
        await self._simulate_latency()

        return VaultREProperty(
            id=property_id,
            address=PropertyAddress(
                line1="123 Main Street",
                suburb="Brisbane",
                state="QLD",
                postcode="4000",
            ),
            property_class=PropertyClass.RESIDENTIAL,
            property_type="House",
            status=PropertyStatus.LISTING,
            bedrooms=4,
            bathrooms=2,
            car_spaces=2,
            land_area=650.0,
            building_area=280.0,
            price=PriceInfo(
                display="$1,250,000 - $1,350,000",
                price_from=1250000.0,
                price_to=1350000.0,
            ),
            agents=[
                Agent(
                    id="agent_001",
                    name="John Smith",
                    email="john.smith@raywhite.com",
                    phone="0412 345 678",
                )
            ],
            photos=[
                PropertyPhoto(
                    id="photo_001",
                    url="https://example.com/photos/main.jpg",
                    thumbnail_url="https://example.com/photos/main_thumb.jpg",
                    caption="Front view",
                    order=0,
                )
            ],
            description="Beautiful family home in prime location...",
            features=["Air Conditioning", "Swimming Pool", "Built-in Robes"],
            created_at=datetime.now() - timedelta(days=30),
            updated_at=datetime.now() - timedelta(days=1),
        )

    async def list_properties(
        self,
        status: Optional[str] = None,
        limit: int = 20,
    ) -> List[VaultREProperty]:
        """List properties with optional status filter."""
        await self._simulate_latency()

        properties = [
            VaultREProperty(
                id="prop_001",
                address=PropertyAddress(
                    line1="123 Main Street",
                    suburb="Brisbane",
                    state="QLD",
                    postcode="4000",
                ),
                property_class=PropertyClass.RESIDENTIAL,
                property_type="House",
                status=PropertyStatus.LISTING,
                bedrooms=4,
                bathrooms=2,
                price=PriceInfo(display="$1,250,000"),
                agents=[Agent(id="agent_001", name="John Smith")],
            ),
            VaultREProperty(
                id="prop_002",
                address=PropertyAddress(
                    line1="45 Oak Avenue",
                    suburb="Paddington",
                    state="QLD",
                    postcode="4064",
                ),
                property_class=PropertyClass.RESIDENTIAL,
                property_type="Unit",
                status=PropertyStatus.LISTING,
                bedrooms=2,
                bathrooms=1,
                price=PriceInfo(display="$650,000"),
                agents=[Agent(id="agent_002", name="Jane Doe")],
            ),
            VaultREProperty(
                id="prop_003",
                address=PropertyAddress(
                    line1="78 River Road",
                    suburb="New Farm",
                    state="QLD",
                    postcode="4005",
                ),
                property_class=PropertyClass.RESIDENTIAL,
                property_type="Townhouse",
                status=PropertyStatus.UNDER_CONTRACT,
                bedrooms=3,
                bathrooms=2,
                price=PriceInfo(display="$980,000"),
                agents=[Agent(id="agent_001", name="John Smith")],
            ),
        ]

        # Filter by status if provided
        if status:
            try:
                status_enum = PropertyStatus(status.lower())
                properties = [p for p in properties if p.status == status_enum]
            except ValueError:
                pass

        return properties[:limit]

    async def get_property_feedback(
        self, property_id: str
    ) -> List[PropertyFeedback]:
        """Get property feedback from VaultRE (legacy)."""
        await self._simulate_latency()
        return await self.list_property_feedback(property_id)

    async def list_property_feedback(
        self, property_id: str, limit: int = 20
    ) -> List[PropertyFeedback]:
        """List feedback for a property."""
        await self._simulate_latency()

        return [
            PropertyFeedback(
                id="feedback_001",
                property_id=property_id,
                contact_id="contact_001",
                contact_name="Michael Brown",
                feedback_date=datetime.now() - timedelta(days=3),
                rating=4,
                interest_level="High",
                comments="Love the layout and location. Need to discuss price.",
                source="open_home",
            ),
            PropertyFeedback(
                id="feedback_002",
                property_id=property_id,
                contact_id="contact_002",
                contact_name="Sarah Wilson",
                feedback_date=datetime.now() - timedelta(days=3),
                rating=5,
                interest_level="Very High",
                comments="Perfect for our family. Will be making an offer.",
                source="open_home",
            ),
            PropertyFeedback(
                id="feedback_003",
                property_id=property_id,
                contact_id="contact_003",
                contact_name="David Lee",
                feedback_date=datetime.now() - timedelta(days=3),
                rating=3,
                interest_level="Medium",
                comments="Nice property but slightly above our budget.",
                source="private_inspection",
            ),
        ][:limit]

    async def get_contacts_by_property(
        self, property_id: str
    ) -> List[VaultREContact]:
        """Get all contacts associated with a property."""
        await self._simulate_latency()

        return [
            VaultREContact(
                id="contact_owner_001",
                first_name="Robert",
                last_name="Johnson",
                email="robert.johnson@email.com",
                phone="0412 111 222",
                contact_type=ContactType.OWNER,
                property_ids=[property_id],
            ),
            VaultREContact(
                id="contact_owner_002",
                first_name="Mary",
                last_name="Johnson",
                email="mary.johnson@email.com",
                phone="0412 111 223",
                contact_type=ContactType.OWNER,
                property_ids=[property_id],
            ),
            VaultREContact(
                id="contact_buyer_001",
                first_name="Michael",
                last_name="Brown",
                email="michael.brown@email.com",
                phone="0412 333 444",
                contact_type=ContactType.BUYER,
                property_ids=[property_id],
            ),
        ]

    async def get_property_contacts(
        self, property_id: str
    ) -> PropertyContacts:
        """Get contacts grouped by type for a property."""
        await self._simulate_latency()

        contacts = await self.get_contacts_by_property(property_id)

        return PropertyContacts(
            property_id=property_id,
            owners=[c for c in contacts if c.contact_type == ContactType.OWNER],
            tenants=[c for c in contacts if c.contact_type == ContactType.TENANT],
            landlords=[c for c in contacts if c.contact_type == ContactType.LANDLORD],
            purchasers=[c for c in contacts if c.contact_type in (ContactType.PURCHASER, ContactType.BUYER)],
        )

    async def get_open_homes(
        self, property_id: str, include_past: bool = False
    ) -> List[OpenHome]:
        """Get open homes for a property."""
        await self._simulate_latency()

        now = datetime.now()
        open_homes = [
            OpenHome(
                id="oh_001",
                property_id=property_id,
                start_time=now + timedelta(days=2, hours=10),
                end_time=now + timedelta(days=2, hours=10, minutes=30),
                agent_id="agent_001",
                attendee_count=0,
            ),
            OpenHome(
                id="oh_002",
                property_id=property_id,
                start_time=now + timedelta(days=9, hours=11),
                end_time=now + timedelta(days=9, hours=11, minutes=30),
                agent_id="agent_001",
                attendee_count=0,
            ),
            OpenHome(
                id="oh_past_001",
                property_id=property_id,
                start_time=now - timedelta(days=5, hours=10),
                end_time=now - timedelta(days=5, hours=9, minutes=30),
                agent_id="agent_001",
                attendee_count=15,
                notes="Great turnout, multiple interested parties",
            ),
        ]

        if not include_past:
            open_homes = [oh for oh in open_homes if oh.start_time > now]

        return open_homes

    async def list_upcoming_open_homes(
        self, days_ahead: int = 7
    ) -> List[OpenHome]:
        """List all upcoming open homes within specified days."""
        await self._simulate_latency()

        now = datetime.now()
        cutoff = now + timedelta(days=days_ahead)

        # Mock open homes across multiple properties
        return [
            OpenHome(
                id="oh_001",
                property_id="prop_001",
                start_time=now + timedelta(days=2, hours=10),
                end_time=now + timedelta(days=2, hours=10, minutes=30),
                agent_id="agent_001",
            ),
            OpenHome(
                id="oh_002",
                property_id="prop_002",
                start_time=now + timedelta(days=2, hours=11),
                end_time=now + timedelta(days=2, hours=11, minutes=30),
                agent_id="agent_002",
            ),
            OpenHome(
                id="oh_003",
                property_id="prop_001",
                start_time=now + timedelta(days=5, hours=10),
                end_time=now + timedelta(days=5, hours=10, minutes=30),
                agent_id="agent_001",
            ),
        ]

    async def get_property_summaries(
        self, status: Optional[str] = None, limit: int = 20
    ) -> List[PropertySummary]:
        """Get simplified property summaries."""
        await self._simulate_latency()

        properties = await self.list_properties(status=status, limit=limit)

        return [
            PropertySummary(
                property_id=p.id,
                address=p.address.full_address,
                property_class=p.property_class,
                status=p.status,
                bedrooms=p.bedrooms,
                bathrooms=p.bathrooms,
                price_display=p.price.display if p.price else None,
                primary_agent=p.agents[0].name if p.agents else None,
            )
            for p in properties
        ]


# =============================================================================
# Ailo Client (Extended)
# =============================================================================


class AiloClient(BaseIntegrationClient):
    """Mock Ailo client for property management integration."""

    def __init__(self, mock_enabled: bool = True):
        """Initialize Ailo client."""
        super().__init__(mock_enabled)
        if not mock_enabled and not settings.production_integrations_enabled:
            raise NotImplementedError("Production Ailo integration not enabled in MVP")

    async def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """Get property details (not typically used for Ailo)."""
        await self._simulate_latency()
        return {}

    async def get_ledger_summary(self, tenancy_id: str) -> Dict[str, Any]:
        """Get ledger summary from Ailo (legacy dict return)."""
        await self._simulate_latency()
        ledger = await self.get_ledger(tenancy_id)
        return {
            "tenancy_id": ledger.tenancy_id,
            "current_balance": float(ledger.current_balance),
            "status": ledger.arrears_status.value,
        }

    async def get_ledger(self, tenancy_id: str) -> AiloLedger:
        """Get full ledger details as typed schema."""
        await self._simulate_latency()

        # Generate mock ledger based on tenancy_id
        if "arrears" in tenancy_id.lower():
            # Simulate arrears scenario
            return AiloLedger(
                id=f"ledger_{tenancy_id}",
                tenancy_id=tenancy_id,
                property_id="prop_lease_001",
                current_balance=Decimal("1250.00"),
                rent_amount=Decimal("500.00"),
                rent_frequency=RentFrequency.WEEKLY,
                next_due_date=date.today() - timedelta(days=10),
                arrears_days=17,
                arrears_status=ArrearsStatus.SEVERE,
                last_payment_date=date.today() - timedelta(days=24),
                last_payment_amount=Decimal("500.00"),
            )
        else:
            # Normal tenant
            return AiloLedger(
                id=f"ledger_{tenancy_id}",
                tenancy_id=tenancy_id,
                property_id="prop_lease_001",
                current_balance=Decimal("0.00"),
                rent_amount=Decimal("550.00"),
                rent_frequency=RentFrequency.WEEKLY,
                next_due_date=date.today() + timedelta(days=3),
                arrears_days=0,
                arrears_status=ArrearsStatus.CURRENT,
                last_payment_date=date.today() - timedelta(days=4),
                last_payment_amount=Decimal("550.00"),
            )

    async def get_tenant_details(self, tenancy_id: str) -> AiloTenant:
        """Get tenant details for a tenancy."""
        await self._simulate_latency()

        return AiloTenant(
            id=f"tenant_{tenancy_id}",
            tenancy_id=tenancy_id,
            name="James Wilson",
            email="james.wilson@email.com",
            phone="0412 555 666",
            lease_start=date.today() - timedelta(days=180),
            lease_end=date.today() + timedelta(days=185),
            is_primary=True,
        )

    async def list_arrears(
        self, min_days: int = 1, max_results: int = 20
    ) -> List[AiloLedger]:
        """List tenancies in arrears."""
        await self._simulate_latency()

        # Mock arrears ledgers
        arrears_ledgers = [
            AiloLedger(
                id="ledger_arr_001",
                tenancy_id="tenancy_001",
                property_id="prop_lease_001",
                current_balance=Decimal("1750.00"),
                rent_amount=Decimal("500.00"),
                rent_frequency=RentFrequency.WEEKLY,
                next_due_date=date.today() - timedelta(days=21),
                arrears_days=28,
                arrears_status=ArrearsStatus.CRITICAL,
                last_payment_date=date.today() - timedelta(days=35),
            ),
            AiloLedger(
                id="ledger_arr_002",
                tenancy_id="tenancy_002",
                property_id="prop_lease_002",
                current_balance=Decimal("650.00"),
                rent_amount=Decimal("650.00"),
                rent_frequency=RentFrequency.FORTNIGHTLY,
                next_due_date=date.today() - timedelta(days=10),
                arrears_days=17,
                arrears_status=ArrearsStatus.SEVERE,
                last_payment_date=date.today() - timedelta(days=24),
            ),
            AiloLedger(
                id="ledger_arr_003",
                tenancy_id="tenancy_003",
                property_id="prop_lease_003",
                current_balance=Decimal("450.00"),
                rent_amount=Decimal("450.00"),
                rent_frequency=RentFrequency.WEEKLY,
                next_due_date=date.today() - timedelta(days=3),
                arrears_days=10,
                arrears_status=ArrearsStatus.MODERATE,
                last_payment_date=date.today() - timedelta(days=10),
            ),
            AiloLedger(
                id="ledger_arr_004",
                tenancy_id="tenancy_004",
                property_id="prop_lease_004",
                current_balance=Decimal("200.00"),
                rent_amount=Decimal("400.00"),
                rent_frequency=RentFrequency.WEEKLY,
                next_due_date=date.today() - timedelta(days=1),
                arrears_days=5,
                arrears_status=ArrearsStatus.MINOR,
                last_payment_date=date.today() - timedelta(days=6),
            ),
        ]

        # Filter by minimum days
        filtered = [l for l in arrears_ledgers if l.arrears_days >= min_days]

        # Sort by arrears days descending (worst first)
        filtered.sort(key=lambda x: x.arrears_days, reverse=True)

        return filtered[:max_results]

    async def get_payment_history(
        self, tenancy_id: str, limit: int = 10
    ) -> List[PaymentEntry]:
        """Get payment history for a tenancy."""
        await self._simulate_latency()

        ledger = await self.get_ledger(tenancy_id)

        # Generate mock payment history
        payments = []
        base_date = date.today()

        for i in range(limit):
            payment_date = base_date - timedelta(days=7 * (i + 1))
            payments.append(
                PaymentEntry(
                    id=f"payment_{tenancy_id}_{i}",
                    ledger_id=ledger.id,
                    amount=ledger.rent_amount,
                    payment_date=payment_date,
                    payment_type="rent",
                    reference=f"RENT-{payment_date.strftime('%Y%m%d')}",
                    status="completed",
                )
            )

        return payments

    async def get_ledger_summary(self, tenancy_id: str) -> LedgerSummary:
        """Get simplified ledger summary."""
        await self._simulate_latency()

        ledger = await self.get_ledger(tenancy_id)

        return LedgerSummary(
            ledger_id=ledger.id,
            tenancy_id=ledger.tenancy_id,
            property_id=ledger.property_id,
            current_balance=float(ledger.current_balance),
            rent_amount=float(ledger.rent_amount),
            arrears_days=ledger.arrears_days,
            arrears_status=ledger.arrears_status,
            next_due_date=ledger.next_due_date,
            last_payment_date=ledger.last_payment_date,
        )


# =============================================================================
# Global Client Instances
# =============================================================================


_vaultre_client: Optional[VaultREClient] = None
_ailo_client: Optional[AiloClient] = None
_gmail_client: Optional[GmailClient] = None
_google_drive_client: Optional[GoogleDriveClient] = None


def get_vaultre_client() -> VaultREClient:
    """Get global VaultRE client."""
    global _vaultre_client
    if _vaultre_client is None:
        _vaultre_client = VaultREClient(mock_enabled=settings.vaultre_mock_enabled)
    return _vaultre_client


def get_ailo_client() -> AiloClient:
    """Get global Ailo client."""
    global _ailo_client
    if _ailo_client is None:
        _ailo_client = AiloClient(mock_enabled=settings.ailo_mock_enabled)
    return _ailo_client


def get_gmail_client() -> GmailClient:
    """Get global Gmail client."""
    global _gmail_client
    if _gmail_client is None:
        _gmail_client = GmailClient(mock_enabled=settings.gmail_mock_enabled)
    return _gmail_client


def get_google_drive_client() -> GoogleDriveClient:
    """Get global Google Drive client."""
    global _google_drive_client
    if _google_drive_client is None:
        _google_drive_client = GoogleDriveClient(mock_enabled=settings.google_drive_mock_enabled)
    return _google_drive_client
