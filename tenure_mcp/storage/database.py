"""SQLite database for MCP Server persistence."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from tenure_mcp.config import settings


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime, date, and Decimal objects."""

    def default(self, obj):
        """Encode datetime, date, and Decimal objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


class Database:
    """SQLite database manager for MCP Server."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection."""
        self.db_path = db_path or settings.database_path
        self._ensure_db_dir()
        self._init_schema()

    def _ensure_db_dir(self) -> None:
        """Ensure database directory exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _init_schema(self) -> None:
        """Initialize database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Tool execution logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    correlation_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    input_data TEXT,
                    output_data TEXT,
                    execution_time_ms REAL,
                    trace_id TEXT,
                    success BOOLEAN,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # LangGraph workflow executions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    correlation_id TEXT NOT NULL,
                    workflow_name TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    state_snapshot TEXT,
                    trace_id TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)

            # Agent manifests
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_manifests (
                    agent_id TEXT PRIMARY KEY,
                    version TEXT NOT NULL,
                    input_schema TEXT NOT NULL,
                    output_schema TEXT NOT NULL,
                    permitted_tools TEXT,
                    permitted_resources TEXT,
                    rbac_policy_level TEXT NOT NULL,
                    workflow_version TEXT,
                    prompt_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Audit log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    correlation_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    user_id TEXT,
                    tenant_id TEXT,
                    tool_name TEXT,
                    action TEXT,
                    policy_result TEXT,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # =========================================================
            # Mock Data Tables for Integration Testing
            # =========================================================

            # Gmail mock emails
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mock_emails (
                    id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    property_id TEXT,
                    contact_email TEXT,
                    sender TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    snippet TEXT,
                    body_preview TEXT,
                    label_ids TEXT,
                    internal_date INTEGER,
                    has_attachments BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Google Drive mock files
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mock_drive_files (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    mime_type TEXT NOT NULL,
                    property_id TEXT,
                    parent_folder_id TEXT,
                    size_bytes INTEGER,
                    content_hash TEXT,
                    expiry_date DATE,
                    web_view_link TEXT,
                    owner_email TEXT,
                    shared BOOLEAN DEFAULT 0,
                    created_time TIMESTAMP,
                    modified_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # VaultRE mock properties
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mock_properties (
                    id TEXT PRIMARY KEY,
                    address_line1 TEXT NOT NULL,
                    address_line2 TEXT,
                    address_suburb TEXT NOT NULL,
                    address_state TEXT NOT NULL,
                    address_postcode TEXT NOT NULL,
                    property_class TEXT NOT NULL,
                    property_type TEXT,
                    status TEXT NOT NULL,
                    bedrooms INTEGER,
                    bathrooms INTEGER,
                    car_spaces INTEGER,
                    land_area REAL,
                    building_area REAL,
                    price_display TEXT,
                    price_value REAL,
                    description TEXT,
                    features TEXT,
                    agent_ids TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # VaultRE mock contacts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mock_contacts (
                    id TEXT PRIMARY KEY,
                    property_id TEXT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    mobile TEXT,
                    contact_type TEXT NOT NULL,
                    company TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # VaultRE mock property feedback
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mock_feedback (
                    id TEXT PRIMARY KEY,
                    property_id TEXT NOT NULL,
                    contact_id TEXT,
                    contact_name TEXT,
                    feedback_date TIMESTAMP NOT NULL,
                    rating INTEGER,
                    interest_level TEXT,
                    comments TEXT,
                    source TEXT DEFAULT 'open_home',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # VaultRE mock open homes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mock_open_homes (
                    id TEXT PRIMARY KEY,
                    property_id TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    agent_id TEXT,
                    attendee_count INTEGER DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Ailo mock ledgers
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mock_ledgers (
                    id TEXT PRIMARY KEY,
                    tenancy_id TEXT NOT NULL UNIQUE,
                    property_id TEXT,
                    tenant_id TEXT,
                    current_balance REAL DEFAULT 0.0,
                    rent_amount REAL NOT NULL,
                    rent_frequency TEXT NOT NULL,
                    next_due_date DATE,
                    arrears_days INTEGER DEFAULT 0,
                    arrears_status TEXT DEFAULT 'current',
                    last_payment_date DATE,
                    last_payment_amount REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Ailo mock tenants
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mock_tenants (
                    id TEXT PRIMARY KEY,
                    tenancy_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    lease_start DATE NOT NULL,
                    lease_end DATE,
                    is_primary BOOLEAN DEFAULT 1,
                    emergency_contact TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Ailo mock payments
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mock_payments (
                    id TEXT PRIMARY KEY,
                    ledger_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    payment_date DATE NOT NULL,
                    payment_type TEXT DEFAULT 'rent',
                    reference TEXT,
                    status TEXT DEFAULT 'completed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for common queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mock_emails_property ON mock_emails(property_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mock_emails_thread ON mock_emails(thread_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mock_drive_files_property ON mock_drive_files(property_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mock_contacts_property ON mock_contacts(property_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mock_feedback_property ON mock_feedback(property_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mock_open_homes_property ON mock_open_homes(property_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mock_ledgers_tenancy ON mock_ledgers(tenancy_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mock_tenants_tenancy ON mock_tenants(tenancy_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mock_payments_ledger ON mock_payments(ledger_id)")

            conn.commit()

    @contextmanager
    def get_connection(self) -> Iterator[sqlite3.Connection]:
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def log_tool_execution(
        self,
        correlation_id: str,
        tool_name: str,
        user_id: str,
        tenant_id: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]] = None,
        execution_time_ms: Optional[float] = None,
        trace_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> None:
        """Log tool execution to database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tool_executions (
                    correlation_id, tool_name, user_id, tenant_id,
                    input_data, output_data, execution_time_ms, trace_id,
                    success, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    correlation_id,
                    tool_name,
                    user_id,
                    tenant_id,
                    json.dumps(input_data, cls=DateTimeEncoder),
                    json.dumps(output_data, cls=DateTimeEncoder) if output_data else None,
                    execution_time_ms,
                    trace_id,
                    success,
                    error_message,
                ),
            )
            conn.commit()

    def log_audit_event(
        self,
        correlation_id: str,
        event_type: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        action: Optional[str] = None,
        policy_result: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log audit event."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO audit_log (
                    correlation_id, event_type, user_id, tenant_id,
                    tool_name, action, policy_result, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    correlation_id,
                    event_type,
                    user_id,
                    tenant_id,
                    tool_name,
                    action,
                    policy_result,
                    json.dumps(details, cls=DateTimeEncoder) if details else None,
                ),
            )
            conn.commit()

    # =========================================================================
    # Mock Data Management Methods
    # =========================================================================

    def insert_mock_email(self, email_data: Dict[str, Any]) -> None:
        """Insert a mock email record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO mock_emails (
                    id, thread_id, property_id, contact_email, sender, recipient,
                    subject, snippet, body_preview, label_ids, internal_date,
                    has_attachments
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    email_data["id"],
                    email_data["thread_id"],
                    email_data.get("property_id"),
                    email_data.get("contact_email"),
                    email_data["sender"],
                    email_data["recipient"],
                    email_data["subject"],
                    email_data.get("snippet"),
                    email_data.get("body_preview"),
                    json.dumps(email_data.get("label_ids", [])),
                    email_data.get("internal_date"),
                    email_data.get("has_attachments", False),
                ),
            )
            conn.commit()

    def get_mock_emails(
        self, property_id: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get mock emails, optionally filtered by property."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if property_id:
                cursor.execute(
                    "SELECT * FROM mock_emails WHERE property_id = ? ORDER BY internal_date DESC LIMIT ?",
                    (property_id, limit),
                )
            else:
                cursor.execute(
                    "SELECT * FROM mock_emails ORDER BY internal_date DESC LIMIT ?",
                    (limit,),
                )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def insert_mock_drive_file(self, file_data: Dict[str, Any]) -> None:
        """Insert a mock Drive file record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO mock_drive_files (
                    id, name, mime_type, property_id, parent_folder_id,
                    size_bytes, content_hash, expiry_date, web_view_link,
                    owner_email, shared, created_time, modified_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    file_data["id"],
                    file_data["name"],
                    file_data["mime_type"],
                    file_data.get("property_id"),
                    file_data.get("parent_folder_id"),
                    file_data.get("size_bytes"),
                    file_data.get("content_hash"),
                    file_data.get("expiry_date"),
                    file_data.get("web_view_link"),
                    file_data.get("owner_email"),
                    file_data.get("shared", False),
                    file_data.get("created_time"),
                    file_data.get("modified_time"),
                ),
            )
            conn.commit()

    def get_mock_drive_files(
        self, property_id: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get mock Drive files, optionally filtered by property."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if property_id:
                cursor.execute(
                    "SELECT * FROM mock_drive_files WHERE property_id = ? ORDER BY modified_time DESC LIMIT ?",
                    (property_id, limit),
                )
            else:
                cursor.execute(
                    "SELECT * FROM mock_drive_files ORDER BY modified_time DESC LIMIT ?",
                    (limit,),
                )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_expiring_documents(
        self, days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """Get documents expiring within specified days."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM mock_drive_files 
                WHERE expiry_date IS NOT NULL 
                AND expiry_date <= date('now', '+' || ? || ' days')
                ORDER BY expiry_date ASC
            """,
                (days_ahead,),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def insert_mock_property(self, property_data: Dict[str, Any]) -> None:
        """Insert a mock VaultRE property record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO mock_properties (
                    id, address_line1, address_line2, address_suburb,
                    address_state, address_postcode, property_class, property_type,
                    status, bedrooms, bathrooms, car_spaces, land_area,
                    building_area, price_display, price_value, description,
                    features, agent_ids, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
                (
                    property_data["id"],
                    property_data["address_line1"],
                    property_data.get("address_line2"),
                    property_data["address_suburb"],
                    property_data["address_state"],
                    property_data["address_postcode"],
                    property_data["property_class"],
                    property_data.get("property_type"),
                    property_data["status"],
                    property_data.get("bedrooms"),
                    property_data.get("bathrooms"),
                    property_data.get("car_spaces"),
                    property_data.get("land_area"),
                    property_data.get("building_area"),
                    property_data.get("price_display"),
                    property_data.get("price_value"),
                    property_data.get("description"),
                    json.dumps(property_data.get("features", [])),
                    json.dumps(property_data.get("agent_ids", [])),
                ),
            )
            conn.commit()

    def get_mock_property(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get a single mock property by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mock_properties WHERE id = ?", (property_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_mock_properties(
        self, status: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get mock properties, optionally filtered by status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute(
                    "SELECT * FROM mock_properties WHERE status = ? ORDER BY updated_at DESC LIMIT ?",
                    (status, limit),
                )
            else:
                cursor.execute(
                    "SELECT * FROM mock_properties ORDER BY updated_at DESC LIMIT ?",
                    (limit,),
                )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def insert_mock_contact(self, contact_data: Dict[str, Any]) -> None:
        """Insert a mock VaultRE contact record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO mock_contacts (
                    id, property_id, first_name, last_name, email, phone,
                    mobile, contact_type, company, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    contact_data["id"],
                    contact_data.get("property_id"),
                    contact_data["first_name"],
                    contact_data["last_name"],
                    contact_data.get("email"),
                    contact_data.get("phone"),
                    contact_data.get("mobile"),
                    contact_data["contact_type"],
                    contact_data.get("company"),
                    contact_data.get("notes"),
                ),
            )
            conn.commit()

    def get_mock_contacts(
        self, property_id: Optional[str] = None, contact_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get mock contacts, optionally filtered."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            conditions = []
            params = []

            if property_id:
                conditions.append("property_id = ?")
                params.append(property_id)
            if contact_type:
                conditions.append("contact_type = ?")
                params.append(contact_type)

            query = "SELECT * FROM mock_contacts"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY created_at DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def insert_mock_feedback(self, feedback_data: Dict[str, Any]) -> None:
        """Insert a mock property feedback record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO mock_feedback (
                    id, property_id, contact_id, contact_name, feedback_date,
                    rating, interest_level, comments, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    feedback_data["id"],
                    feedback_data["property_id"],
                    feedback_data.get("contact_id"),
                    feedback_data.get("contact_name"),
                    feedback_data["feedback_date"],
                    feedback_data.get("rating"),
                    feedback_data.get("interest_level"),
                    feedback_data.get("comments"),
                    feedback_data.get("source", "open_home"),
                ),
            )
            conn.commit()

    def get_mock_feedback(
        self, property_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get mock feedback for a property."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM mock_feedback WHERE property_id = ? ORDER BY feedback_date DESC LIMIT ?",
                (property_id, limit),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def insert_mock_open_home(self, open_home_data: Dict[str, Any]) -> None:
        """Insert a mock open home record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO mock_open_homes (
                    id, property_id, start_time, end_time, agent_id,
                    attendee_count, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    open_home_data["id"],
                    open_home_data["property_id"],
                    open_home_data["start_time"],
                    open_home_data["end_time"],
                    open_home_data.get("agent_id"),
                    open_home_data.get("attendee_count", 0),
                    open_home_data.get("notes"),
                ),
            )
            conn.commit()

    def get_mock_open_homes(
        self, property_id: Optional[str] = None, upcoming_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get mock open homes."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            conditions = []
            params = []

            if property_id:
                conditions.append("property_id = ?")
                params.append(property_id)
            if upcoming_only:
                conditions.append("start_time > datetime('now')")

            query = "SELECT * FROM mock_open_homes"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY start_time ASC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def insert_mock_ledger(self, ledger_data: Dict[str, Any]) -> None:
        """Insert a mock Ailo ledger record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO mock_ledgers (
                    id, tenancy_id, property_id, tenant_id, current_balance,
                    rent_amount, rent_frequency, next_due_date, arrears_days,
                    arrears_status, last_payment_date, last_payment_amount
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    ledger_data["id"],
                    ledger_data["tenancy_id"],
                    ledger_data.get("property_id"),
                    ledger_data.get("tenant_id"),
                    ledger_data.get("current_balance", 0.0),
                    ledger_data["rent_amount"],
                    ledger_data["rent_frequency"],
                    ledger_data.get("next_due_date"),
                    ledger_data.get("arrears_days", 0),
                    ledger_data.get("arrears_status", "current"),
                    ledger_data.get("last_payment_date"),
                    ledger_data.get("last_payment_amount"),
                ),
            )
            conn.commit()

    def get_mock_ledger(self, tenancy_id: str) -> Optional[Dict[str, Any]]:
        """Get a single mock ledger by tenancy ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mock_ledgers WHERE tenancy_id = ?", (tenancy_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_mock_arrears_ledgers(
        self, min_days: int = 1, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get ledgers in arrears."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM mock_ledgers 
                WHERE arrears_days >= ? 
                ORDER BY arrears_days DESC 
                LIMIT ?
            """,
                (min_days, limit),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def insert_mock_tenant(self, tenant_data: Dict[str, Any]) -> None:
        """Insert a mock Ailo tenant record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO mock_tenants (
                    id, tenancy_id, name, email, phone, lease_start,
                    lease_end, is_primary, emergency_contact
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    tenant_data["id"],
                    tenant_data["tenancy_id"],
                    tenant_data["name"],
                    tenant_data["email"],
                    tenant_data.get("phone"),
                    tenant_data["lease_start"],
                    tenant_data.get("lease_end"),
                    tenant_data.get("is_primary", True),
                    tenant_data.get("emergency_contact"),
                ),
            )
            conn.commit()

    def get_mock_tenant(self, tenancy_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant by tenancy ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM mock_tenants WHERE tenancy_id = ? AND is_primary = 1",
                (tenancy_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def insert_mock_payment(self, payment_data: Dict[str, Any]) -> None:
        """Insert a mock payment record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO mock_payments (
                    id, ledger_id, amount, payment_date, payment_type,
                    reference, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    payment_data["id"],
                    payment_data["ledger_id"],
                    payment_data["amount"],
                    payment_data["payment_date"],
                    payment_data.get("payment_type", "rent"),
                    payment_data.get("reference"),
                    payment_data.get("status", "completed"),
                ),
            )
            conn.commit()

    def get_mock_payments(
        self, ledger_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get payments for a ledger."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM mock_payments WHERE ledger_id = ? ORDER BY payment_date DESC LIMIT ?",
                (ledger_id, limit),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def clear_mock_data(self, table: Optional[str] = None) -> None:
        """Clear mock data from tables. If table is None, clears all mock tables."""
        mock_tables = [
            "mock_emails",
            "mock_drive_files",
            "mock_properties",
            "mock_contacts",
            "mock_feedback",
            "mock_open_homes",
            "mock_ledgers",
            "mock_tenants",
            "mock_payments",
        ]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            if table:
                if table in mock_tables:
                    cursor.execute(f"DELETE FROM {table}")
            else:
                for t in mock_tables:
                    cursor.execute(f"DELETE FROM {t}")
            conn.commit()

    def seed_mock_data(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        """Seed mock data from a dictionary of table -> records.
        
        Args:
            data: Dict mapping table names to lists of records.
                  Keys: 'emails', 'drive_files', 'properties', 'contacts',
                        'feedback', 'open_homes', 'ledgers', 'tenants', 'payments'
        """
        insert_methods = {
            "emails": self.insert_mock_email,
            "drive_files": self.insert_mock_drive_file,
            "properties": self.insert_mock_property,
            "contacts": self.insert_mock_contact,
            "feedback": self.insert_mock_feedback,
            "open_homes": self.insert_mock_open_home,
            "ledgers": self.insert_mock_ledger,
            "tenants": self.insert_mock_tenant,
            "payments": self.insert_mock_payment,
        }

        for table_key, records in data.items():
            if table_key in insert_methods:
                for record in records:
                    insert_methods[table_key](record)


# Global database instance
_db: Optional[Database] = None


def get_db() -> Database:
    """Get global database instance."""
    global _db
    if _db is None:
        _db = Database()
    return _db
