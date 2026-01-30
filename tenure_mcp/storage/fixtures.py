"""Mock data fixtures for integration testing and development."""

import uuid
from datetime import date, datetime, timedelta
from typing import Any, Dict, List

from tenure_mcp.storage.database import get_db


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    return f"{prefix}{uuid.uuid4().hex[:12]}"


# =============================================================================
# Property IDs (shared across integrations)
# =============================================================================

PROPERTY_IDS = [
    "prop_001",
    "prop_002",
    "prop_003",
    "prop_lease_001",
    "prop_lease_002",
]

TENANCY_IDS = [
    "tenancy_001",
    "tenancy_002",
    "tenancy_003",
    "tenancy_004",
]


# =============================================================================
# VaultRE Mock Properties
# =============================================================================

MOCK_PROPERTIES: List[Dict[str, Any]] = [
    {
        "id": "prop_001",
        "address_line1": "123 Main Street",
        "address_suburb": "Brisbane",
        "address_state": "QLD",
        "address_postcode": "4000",
        "property_class": "residential",
        "property_type": "House",
        "status": "listing",
        "bedrooms": 4,
        "bathrooms": 2,
        "car_spaces": 2,
        "land_area": 650.0,
        "building_area": 280.0,
        "price_display": "$1,250,000 - $1,350,000",
        "price_value": 1300000.0,
        "description": "Stunning family home in prime Brisbane CBD location. Features modern kitchen, open plan living, and resort-style pool.",
        "features": ["Air Conditioning", "Swimming Pool", "Built-in Robes", "Dishwasher", "Security System"],
        "agent_ids": ["agent_001"],
    },
    {
        "id": "prop_002",
        "address_line1": "45 Oak Avenue",
        "address_suburb": "Paddington",
        "address_state": "QLD",
        "address_postcode": "4064",
        "property_class": "residential",
        "property_type": "Unit",
        "status": "listing",
        "bedrooms": 2,
        "bathrooms": 1,
        "car_spaces": 1,
        "land_area": None,
        "building_area": 85.0,
        "price_display": "$650,000",
        "price_value": 650000.0,
        "description": "Charming character unit in sought-after Paddington. Walking distance to cafes and boutiques.",
        "features": ["Air Conditioning", "Balcony", "Intercom"],
        "agent_ids": ["agent_002"],
    },
    {
        "id": "prop_003",
        "address_line1": "78 River Road",
        "address_suburb": "New Farm",
        "address_state": "QLD",
        "address_postcode": "4005",
        "property_class": "residential",
        "property_type": "Townhouse",
        "status": "under_contract",
        "bedrooms": 3,
        "bathrooms": 2,
        "car_spaces": 2,
        "land_area": 180.0,
        "building_area": 150.0,
        "price_display": "$980,000",
        "price_value": 980000.0,
        "description": "Modern townhouse with river glimpses. Low body corporate, pet friendly.",
        "features": ["Air Conditioning", "Courtyard", "Built-in Robes"],
        "agent_ids": ["agent_001"],
    },
    {
        "id": "prop_lease_001",
        "address_line1": "15 Park Lane",
        "address_suburb": "Woolloongabba",
        "address_state": "QLD",
        "address_postcode": "4102",
        "property_class": "residential",
        "property_type": "Apartment",
        "status": "leased",
        "bedrooms": 2,
        "bathrooms": 1,
        "car_spaces": 1,
        "land_area": None,
        "building_area": 72.0,
        "price_display": "$550/week",
        "price_value": 550.0,
        "description": "Modern apartment close to Gabba stadium and transport.",
        "features": ["Air Conditioning", "Balcony", "Secure Parking"],
        "agent_ids": ["agent_003"],
    },
    {
        "id": "prop_lease_002",
        "address_line1": "22 Valley View Drive",
        "address_suburb": "Greenslopes",
        "address_state": "QLD",
        "address_postcode": "4120",
        "property_class": "residential",
        "property_type": "House",
        "status": "leased",
        "bedrooms": 3,
        "bathrooms": 2,
        "car_spaces": 2,
        "land_area": 450.0,
        "building_area": 140.0,
        "price_display": "$650/week",
        "price_value": 650.0,
        "description": "Family home with large backyard. Close to schools and shops.",
        "features": ["Air Conditioning", "Fenced Yard", "Garden Shed"],
        "agent_ids": ["agent_003"],
    },
]


# =============================================================================
# VaultRE Mock Contacts
# =============================================================================

MOCK_CONTACTS: List[Dict[str, Any]] = [
    # Owners for prop_001
    {
        "id": "contact_owner_001",
        "property_id": "prop_001",
        "first_name": "Robert",
        "last_name": "Johnson",
        "email": "robert.johnson@email.com",
        "phone": "07 3456 7890",
        "mobile": "0412 111 222",
        "contact_type": "owner",
    },
    {
        "id": "contact_owner_002",
        "property_id": "prop_001",
        "first_name": "Mary",
        "last_name": "Johnson",
        "email": "mary.johnson@email.com",
        "mobile": "0412 111 223",
        "contact_type": "owner",
    },
    # Buyer interested in prop_001
    {
        "id": "contact_buyer_001",
        "property_id": "prop_001",
        "first_name": "Michael",
        "last_name": "Brown",
        "email": "michael.brown@email.com",
        "mobile": "0412 333 444",
        "contact_type": "buyer",
    },
    # Owner for prop_002
    {
        "id": "contact_owner_003",
        "property_id": "prop_002",
        "first_name": "Sarah",
        "last_name": "Wilson",
        "email": "sarah.wilson@email.com",
        "mobile": "0423 456 789",
        "contact_type": "owner",
    },
    # Landlord for prop_lease_001
    {
        "id": "contact_landlord_001",
        "property_id": "prop_lease_001",
        "first_name": "David",
        "last_name": "Chen",
        "email": "david.chen@email.com",
        "mobile": "0434 567 890",
        "contact_type": "landlord",
    },
    # Tenant for prop_lease_001
    {
        "id": "contact_tenant_001",
        "property_id": "prop_lease_001",
        "first_name": "James",
        "last_name": "Wilson",
        "email": "james.wilson@email.com",
        "mobile": "0412 555 666",
        "contact_type": "tenant",
    },
]


# =============================================================================
# VaultRE Mock Feedback
# =============================================================================

def get_mock_feedback() -> List[Dict[str, Any]]:
    """Generate mock feedback with relative dates."""
    base_date = datetime.now()
    return [
        {
            "id": "feedback_001",
            "property_id": "prop_001",
            "contact_id": "contact_buyer_001",
            "contact_name": "Michael Brown",
            "feedback_date": (base_date - timedelta(days=3)).isoformat(),
            "rating": 4,
            "interest_level": "High",
            "comments": "Love the layout and location. Need to discuss price with partner.",
            "source": "open_home",
        },
        {
            "id": "feedback_002",
            "property_id": "prop_001",
            "contact_name": "Sarah Thompson",
            "feedback_date": (base_date - timedelta(days=3)).isoformat(),
            "rating": 5,
            "interest_level": "Very High",
            "comments": "Perfect for our family. Will be making an offer this week.",
            "source": "open_home",
        },
        {
            "id": "feedback_003",
            "property_id": "prop_001",
            "contact_name": "David Lee",
            "feedback_date": (base_date - timedelta(days=3)).isoformat(),
            "rating": 3,
            "interest_level": "Medium",
            "comments": "Nice property but slightly above our budget. Would consider if price drops.",
            "source": "private_inspection",
        },
        {
            "id": "feedback_004",
            "property_id": "prop_002",
            "contact_name": "Emma Davis",
            "feedback_date": (base_date - timedelta(days=5)).isoformat(),
            "rating": 4,
            "interest_level": "High",
            "comments": "Great character features. Love the Paddington location.",
            "source": "open_home",
        },
    ]


# =============================================================================
# VaultRE Mock Open Homes
# =============================================================================

def get_mock_open_homes() -> List[Dict[str, Any]]:
    """Generate mock open homes with relative dates."""
    now = datetime.now()
    return [
        # Upcoming open homes
        {
            "id": "oh_001",
            "property_id": "prop_001",
            "start_time": (now + timedelta(days=2, hours=10)).isoformat(),
            "end_time": (now + timedelta(days=2, hours=10, minutes=30)).isoformat(),
            "agent_id": "agent_001",
            "attendee_count": 0,
        },
        {
            "id": "oh_002",
            "property_id": "prop_002",
            "start_time": (now + timedelta(days=2, hours=11)).isoformat(),
            "end_time": (now + timedelta(days=2, hours=11, minutes=30)).isoformat(),
            "agent_id": "agent_002",
            "attendee_count": 0,
        },
        {
            "id": "oh_003",
            "property_id": "prop_001",
            "start_time": (now + timedelta(days=9, hours=10)).isoformat(),
            "end_time": (now + timedelta(days=9, hours=10, minutes=30)).isoformat(),
            "agent_id": "agent_001",
            "attendee_count": 0,
        },
        # Past open home
        {
            "id": "oh_past_001",
            "property_id": "prop_001",
            "start_time": (now - timedelta(days=5, hours=10)).isoformat(),
            "end_time": (now - timedelta(days=5, hours=9, minutes=30)).isoformat(),
            "agent_id": "agent_001",
            "attendee_count": 15,
            "notes": "Great turnout, multiple interested parties",
        },
    ]


# =============================================================================
# Gmail Mock Emails
# =============================================================================

def get_mock_emails() -> List[Dict[str, Any]]:
    """Generate mock emails with relative dates."""
    now = datetime.now()
    return [
        {
            "id": "msg_001",
            "thread_id": "thread_001",
            "property_id": "prop_001",
            "contact_email": "robert.johnson@email.com",
            "sender": "robert.johnson@email.com",
            "recipient": "agent@raywhite.com",
            "subject": "Re: Weekly Update - 123 Main Street",
            "snippet": "Thanks for the update. Happy with the progress so far. Looking forward to the open home this weekend.",
            "body_preview": "Thanks for the update on 123 Main Street...",
            "label_ids": ["INBOX", "IMPORTANT"],
            "internal_date": int((now - timedelta(days=1)).timestamp() * 1000),
            "has_attachments": False,
        },
        {
            "id": "msg_002",
            "thread_id": "thread_001",
            "property_id": "prop_001",
            "contact_email": "agent@raywhite.com",
            "sender": "agent@raywhite.com",
            "recipient": "robert.johnson@email.com",
            "subject": "Weekly Update - 123 Main Street",
            "snippet": "Hi Robert, Here's your weekly update on the property. We've had strong interest...",
            "body_preview": "Hi Robert,\n\nHere's your weekly update on the property at 123 Main Street...",
            "label_ids": ["SENT"],
            "internal_date": int((now - timedelta(days=2)).timestamp() * 1000),
            "has_attachments": True,
        },
        {
            "id": "msg_003",
            "thread_id": "thread_002",
            "property_id": "prop_001",
            "contact_email": "michael.brown@email.com",
            "sender": "michael.brown@email.com",
            "recipient": "agent@raywhite.com",
            "subject": "Inquiry - 123 Main Street",
            "snippet": "Hi, I visited the open home last weekend and I'm very interested in the property...",
            "body_preview": "Hi,\n\nI visited the open home last weekend and I'm very interested...",
            "label_ids": ["INBOX"],
            "internal_date": int((now - timedelta(days=4)).timestamp() * 1000),
            "has_attachments": False,
        },
        {
            "id": "msg_004",
            "thread_id": "thread_003",
            "property_id": "prop_lease_001",
            "contact_email": "james.wilson@email.com",
            "sender": "james.wilson@email.com",
            "recipient": "agent@raywhite.com",
            "subject": "Maintenance Request - 15 Park Lane",
            "snippet": "Hi, The air conditioning unit in the living room has stopped working...",
            "body_preview": "Hi,\n\nThe air conditioning unit in the living room has stopped working...",
            "label_ids": ["INBOX"],
            "internal_date": int((now - timedelta(days=2)).timestamp() * 1000),
            "has_attachments": False,
        },
    ]


# =============================================================================
# Google Drive Mock Files
# =============================================================================

def get_mock_drive_files() -> List[Dict[str, Any]]:
    """Generate mock Drive files with relative dates."""
    now = datetime.now()
    today = date.today()
    return [
        {
            "id": "file_001",
            "name": "Contract_of_Sale_123_Main_St.pdf",
            "mime_type": "application/pdf",
            "property_id": "prop_001",
            "parent_folder_id": "folder_prop_001",
            "size_bytes": 256000,
            "web_view_link": "https://drive.google.com/file/d/file_001/view",
            "owner_email": "agent@raywhite.com",
            "shared": True,
            "created_time": (now - timedelta(days=30)).isoformat(),
            "modified_time": (now - timedelta(days=5)).isoformat(),
            "expiry_date": None,
        },
        {
            "id": "file_002",
            "name": "Building_Inspection_Report.pdf",
            "mime_type": "application/pdf",
            "property_id": "prop_001",
            "parent_folder_id": "folder_prop_001",
            "size_bytes": 512000,
            "web_view_link": "https://drive.google.com/file/d/file_002/view",
            "owner_email": "inspector@example.com",
            "shared": True,
            "created_time": (now - timedelta(days=60)).isoformat(),
            "modified_time": (now - timedelta(days=60)).isoformat(),
            "expiry_date": None,
        },
        {
            "id": "file_003",
            "name": "Strata_Report.pdf",
            "mime_type": "application/pdf",
            "property_id": "prop_002",
            "parent_folder_id": "folder_prop_002",
            "size_bytes": 384000,
            "web_view_link": "https://drive.google.com/file/d/file_003/view",
            "owner_email": "strata@example.com",
            "shared": True,
            "created_time": (now - timedelta(days=45)).isoformat(),
            "modified_time": (now - timedelta(days=45)).isoformat(),
            "expiry_date": None,
        },
        {
            "id": "file_004",
            "name": "Smoke_Alarm_Certificate.pdf",
            "mime_type": "application/pdf",
            "property_id": "prop_lease_001",
            "parent_folder_id": "folder_prop_lease_001",
            "size_bytes": 128000,
            "web_view_link": "https://drive.google.com/file/d/file_004/view",
            "owner_email": "agent@raywhite.com",
            "shared": False,
            "created_time": (now - timedelta(days=350)).isoformat(),
            "modified_time": (now - timedelta(days=350)).isoformat(),
            "expiry_date": (today + timedelta(days=15)).isoformat(),  # Expiring soon
        },
        {
            "id": "file_005",
            "name": "Pool_Safety_Certificate.pdf",
            "mime_type": "application/pdf",
            "property_id": "prop_001",
            "parent_folder_id": "folder_prop_001",
            "size_bytes": 96000,
            "web_view_link": "https://drive.google.com/file/d/file_005/view",
            "owner_email": "agent@raywhite.com",
            "shared": False,
            "created_time": (now - timedelta(days=700)).isoformat(),
            "modified_time": (now - timedelta(days=700)).isoformat(),
            "expiry_date": (today - timedelta(days=5)).isoformat(),  # Already expired
        },
        {
            "id": "file_006",
            "name": "Lease_Agreement_15_Park_Lane.pdf",
            "mime_type": "application/pdf",
            "property_id": "prop_lease_001",
            "parent_folder_id": "folder_prop_lease_001",
            "size_bytes": 180000,
            "web_view_link": "https://drive.google.com/file/d/file_006/view",
            "owner_email": "agent@raywhite.com",
            "shared": True,
            "created_time": (now - timedelta(days=180)).isoformat(),
            "modified_time": (now - timedelta(days=180)).isoformat(),
            "expiry_date": (today + timedelta(days=185)).isoformat(),  # Lease end
        },
    ]


# =============================================================================
# Ailo Mock Ledgers
# =============================================================================

def get_mock_ledgers() -> List[Dict[str, Any]]:
    """Generate mock ledgers with relative dates."""
    today = date.today()
    return [
        # Current tenant - no arrears
        {
            "id": "ledger_001",
            "tenancy_id": "tenancy_001",
            "property_id": "prop_lease_001",
            "tenant_id": "tenant_001",
            "current_balance": 0.0,
            "rent_amount": 550.0,
            "rent_frequency": "weekly",
            "next_due_date": (today + timedelta(days=3)).isoformat(),
            "arrears_days": 0,
            "arrears_status": "current",
            "last_payment_date": (today - timedelta(days=4)).isoformat(),
            "last_payment_amount": 550.0,
        },
        # Minor arrears
        {
            "id": "ledger_002",
            "tenancy_id": "tenancy_002",
            "property_id": "prop_lease_002",
            "tenant_id": "tenant_002",
            "current_balance": 450.0,
            "rent_amount": 450.0,
            "rent_frequency": "weekly",
            "next_due_date": (today - timedelta(days=3)).isoformat(),
            "arrears_days": 5,
            "arrears_status": "minor",
            "last_payment_date": (today - timedelta(days=10)).isoformat(),
            "last_payment_amount": 450.0,
        },
        # Moderate arrears
        {
            "id": "ledger_003",
            "tenancy_id": "tenancy_003",
            "property_id": "prop_lease_003",
            "tenant_id": "tenant_003",
            "current_balance": 650.0,
            "rent_amount": 650.0,
            "rent_frequency": "fortnightly",
            "next_due_date": (today - timedelta(days=10)).isoformat(),
            "arrears_days": 12,
            "arrears_status": "moderate",
            "last_payment_date": (today - timedelta(days=24)).isoformat(),
            "last_payment_amount": 650.0,
        },
        # Critical arrears
        {
            "id": "ledger_004",
            "tenancy_id": "tenancy_004",
            "property_id": "prop_lease_004",
            "tenant_id": "tenant_004",
            "current_balance": 2000.0,
            "rent_amount": 500.0,
            "rent_frequency": "weekly",
            "next_due_date": (today - timedelta(days=21)).isoformat(),
            "arrears_days": 28,
            "arrears_status": "critical",
            "last_payment_date": (today - timedelta(days=35)).isoformat(),
            "last_payment_amount": 500.0,
        },
    ]


# =============================================================================
# Ailo Mock Tenants
# =============================================================================

def get_mock_tenants() -> List[Dict[str, Any]]:
    """Generate mock tenants with relative dates."""
    today = date.today()
    return [
        {
            "id": "tenant_001",
            "tenancy_id": "tenancy_001",
            "name": "James Wilson",
            "email": "james.wilson@email.com",
            "phone": "0412 555 666",
            "lease_start": (today - timedelta(days=180)).isoformat(),
            "lease_end": (today + timedelta(days=185)).isoformat(),
            "is_primary": True,
            "emergency_contact": "Susan Wilson - 0423 456 789",
        },
        {
            "id": "tenant_002",
            "tenancy_id": "tenancy_002",
            "name": "Emily Brown",
            "email": "emily.brown@email.com",
            "phone": "0423 666 777",
            "lease_start": (today - timedelta(days=90)).isoformat(),
            "lease_end": (today + timedelta(days=275)).isoformat(),
            "is_primary": True,
        },
        {
            "id": "tenant_003",
            "tenancy_id": "tenancy_003",
            "name": "Mark Taylor",
            "email": "mark.taylor@email.com",
            "phone": "0434 777 888",
            "lease_start": (today - timedelta(days=365)).isoformat(),
            "lease_end": (today + timedelta(days=30)).isoformat(),  # Lease ending soon
            "is_primary": True,
        },
        {
            "id": "tenant_004",
            "tenancy_id": "tenancy_004",
            "name": "Lisa Anderson",
            "email": "lisa.anderson@email.com",
            "phone": "0445 888 999",
            "lease_start": (today - timedelta(days=200)).isoformat(),
            "lease_end": (today + timedelta(days=165)).isoformat(),
            "is_primary": True,
        },
    ]


# =============================================================================
# Ailo Mock Payments
# =============================================================================

def get_mock_payments() -> List[Dict[str, Any]]:
    """Generate mock payment history."""
    today = date.today()
    payments = []

    # Generate payment history for each ledger
    ledgers = get_mock_ledgers()
    for ledger in ledgers:
        ledger_id = ledger["id"]
        rent_amount = ledger["rent_amount"]
        frequency_days = 7 if ledger["rent_frequency"] == "weekly" else 14

        # Generate 8 weeks of payment history
        for i in range(8):
            payment_date = today - timedelta(days=frequency_days * (i + 1))
            payments.append({
                "id": f"payment_{ledger_id}_{i}",
                "ledger_id": ledger_id,
                "amount": rent_amount,
                "payment_date": payment_date.isoformat(),
                "payment_type": "rent",
                "reference": f"RENT-{payment_date.strftime('%Y%m%d')}",
                "status": "completed",
            })

    return payments


# =============================================================================
# Seed Function
# =============================================================================

def seed_all_mock_data(clear_existing: bool = True) -> Dict[str, int]:
    """Seed all mock data into the database.
    
    Args:
        clear_existing: If True, clears existing mock data before seeding.
        
    Returns:
        Dict with counts of seeded records per table.
    """
    db = get_db()

    if clear_existing:
        db.clear_mock_data()

    # Prepare all data
    data = {
        "properties": MOCK_PROPERTIES,
        "contacts": MOCK_CONTACTS,
        "feedback": get_mock_feedback(),
        "open_homes": get_mock_open_homes(),
        "emails": get_mock_emails(),
        "drive_files": get_mock_drive_files(),
        "ledgers": get_mock_ledgers(),
        "tenants": get_mock_tenants(),
        "payments": get_mock_payments(),
    }

    # Seed data
    db.seed_mock_data(data)

    # Return counts
    return {key: len(records) for key, records in data.items()}


def get_all_fixtures() -> Dict[str, List[Dict[str, Any]]]:
    """Get all fixture data without seeding.
    
    Returns:
        Dict of all fixture data by category.
    """
    return {
        "properties": MOCK_PROPERTIES,
        "contacts": MOCK_CONTACTS,
        "feedback": get_mock_feedback(),
        "open_homes": get_mock_open_homes(),
        "emails": get_mock_emails(),
        "drive_files": get_mock_drive_files(),
        "ledgers": get_mock_ledgers(),
        "tenants": get_mock_tenants(),
        "payments": get_mock_payments(),
    }
