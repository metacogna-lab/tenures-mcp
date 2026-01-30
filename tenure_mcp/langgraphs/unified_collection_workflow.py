"""Unified data collection workflow across all integrations."""

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from tenure_mcp.middleware.clients import (
    get_ailo_client,
    get_gmail_client,
    get_google_drive_client,
    get_vaultre_client,
)
from tenure_mcp.schemas.base import RequestContext
from tenure_mcp.schemas.integrations import (
    AiloCollectionResult,
    ComplianceAlert,
    CommunicationEntry,
    DocumentInfo,
    DriveCollectionResult,
    GmailCollectionResult,
    LedgerSummary,
    UnifiedPropertyData,
    VaultRECollectionResult,
)


class UnifiedCollectionState(TypedDict):
    """State for unified data collection workflow."""

    property_id: str
    collection_scope: List[str]
    context: RequestContext

    # Collection results from each integration
    gmail_data: Optional[GmailCollectionResult]
    drive_data: Optional[DriveCollectionResult]
    vaultre_data: Optional[VaultRECollectionResult]
    ailo_data: Optional[AiloCollectionResult]

    # Unified output
    unified_output: Optional[UnifiedPropertyData]
    errors: List[str]

    # Timing
    start_time: float
    execution_time_ms: Optional[float]


def build_unified_collection_workflow() -> StateGraph:
    """Build the unified data collection workflow.
    
    Workflow collects data from Gmail, Google Drive, VaultRE, and Ailo
    integrations in parallel (where possible), then merges and transforms
    the data into a unified property view.
    
    Flow:
        parse_input → parallel_collection → merge_results → 
        transform_data → validate_output → END
    """
    graph = StateGraph(UnifiedCollectionState)

    async def parse_input(state: UnifiedCollectionState) -> UnifiedCollectionState:
        """Parse and validate input parameters."""
        state["start_time"] = time.time()
        state["errors"] = []

        # Validate collection scope
        valid_scopes = {"gmail", "drive", "vaultre", "ailo"}
        scope = state.get("collection_scope", list(valid_scopes))
        state["collection_scope"] = [s for s in scope if s in valid_scopes]

        if not state["collection_scope"]:
            state["errors"].append("No valid collection scopes specified")

        return state

    async def collect_gmail(state: UnifiedCollectionState) -> UnifiedCollectionState:
        """Collect data from Gmail integration."""
        if "gmail" not in state["collection_scope"]:
            state["gmail_data"] = None
            return state

        try:
            client = get_gmail_client()

            # Get emails for the property
            emails = await client.get_property_emails(
                property_id=state["property_id"],
                days_back=30,
            )

            state["gmail_data"] = GmailCollectionResult(
                emails=emails,
                threads=[],  # Would populate from thread search
                total_count=len(emails),
                collected_at=datetime.now(),
            )

        except Exception as e:
            state["errors"].append(f"Gmail collection failed: {str(e)}")
            state["gmail_data"] = None

        return state

    async def collect_drive(state: UnifiedCollectionState) -> UnifiedCollectionState:
        """Collect data from Google Drive integration."""
        if "drive" not in state["collection_scope"]:
            state["drive_data"] = None
            return state

        try:
            client = get_google_drive_client()

            # Get documents for the property
            documents = await client.get_property_documents(
                property_id=state["property_id"],
            )

            # Check for expiry alerts
            alerts = await client.check_document_expiry(
                property_id=state["property_id"],
                days_ahead=30,
            )

            state["drive_data"] = DriveCollectionResult(
                documents=documents,
                expiry_alerts=alerts,
                total_count=len(documents),
                collected_at=datetime.now(),
            )

        except Exception as e:
            state["errors"].append(f"Drive collection failed: {str(e)}")
            state["drive_data"] = None

        return state

    async def collect_vaultre(state: UnifiedCollectionState) -> UnifiedCollectionState:
        """Collect data from VaultRE integration."""
        if "vaultre" not in state["collection_scope"]:
            state["vaultre_data"] = None
            return state

        try:
            client = get_vaultre_client()

            # Get property details
            property_data = await client.get_property(state["property_id"])

            # Get contacts
            contacts = await client.get_property_contacts(state["property_id"])

            # Get feedback
            feedback = await client.list_property_feedback(state["property_id"])

            # Get open homes
            open_homes = await client.get_open_homes(
                state["property_id"], include_past=False
            )

            state["vaultre_data"] = VaultRECollectionResult(
                property=property_data,
                contacts=contacts,
                feedback=feedback,
                open_homes=open_homes,
                collected_at=datetime.now(),
            )

        except Exception as e:
            state["errors"].append(f"VaultRE collection failed: {str(e)}")
            state["vaultre_data"] = None

        return state

    async def collect_ailo(state: UnifiedCollectionState) -> UnifiedCollectionState:
        """Collect data from Ailo integration."""
        if "ailo" not in state["collection_scope"]:
            state["ailo_data"] = None
            return state

        try:
            client = get_ailo_client()

            # Find tenancy for this property (simplified lookup)
            # In real implementation, would have property -> tenancy mapping
            tenancy_id = f"tenancy_{state['property_id']}"

            try:
                ledger = await client.get_ledger(tenancy_id)
                tenant = await client.get_tenant_details(tenancy_id)
                payments = await client.get_payment_history(tenancy_id, limit=5)

                state["ailo_data"] = AiloCollectionResult(
                    ledger=ledger,
                    tenant=tenant,
                    payment_history=payments,
                    collected_at=datetime.now(),
                )
            except Exception:
                # Property may not have a tenancy (e.g., for sale property)
                state["ailo_data"] = AiloCollectionResult(
                    ledger=None,
                    tenant=None,
                    payment_history=[],
                    collected_at=datetime.now(),
                )

        except Exception as e:
            state["errors"].append(f"Ailo collection failed: {str(e)}")
            state["ailo_data"] = None

        return state

    async def merge_results(state: UnifiedCollectionState) -> UnifiedCollectionState:
        """Merge results from all integrations."""
        # Results are already in state - this node serves as a sync point
        # after parallel collection would complete
        return state

    async def transform_data(state: UnifiedCollectionState) -> UnifiedCollectionState:
        """Transform collected data into unified output."""
        try:
            # Extract property details
            property_details = None
            owner_contacts = []
            if state["vaultre_data"]:
                property_details = state["vaultre_data"].property
                if state["vaultre_data"].contacts:
                    owner_contacts = state["vaultre_data"].contacts.owners

            # Extract tenant info
            tenant_info = None
            financial_status = None
            if state["ailo_data"]:
                tenant_info = state["ailo_data"].tenant
                if state["ailo_data"].ledger:
                    ledger = state["ailo_data"].ledger
                    financial_status = LedgerSummary(
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

            # Extract communications
            recent_communications = []
            if state["gmail_data"]:
                for email in state["gmail_data"].emails[:10]:
                    recent_communications.append(
                        CommunicationEntry(
                            id=email.message_id,
                            type="email",
                            direction="inbound" if "INBOX" in email.labels else "outbound",
                            subject=email.subject,
                            snippet=email.snippet,
                            timestamp=email.received_at,
                            contact_email=email.sender,
                        )
                    )

            # Extract documents
            documents = []
            if state["drive_data"]:
                documents = state["drive_data"].documents

            # Generate compliance alerts
            compliance_alerts = []
            if state["drive_data"]:
                for alert in state["drive_data"].expiry_alerts:
                    compliance_alerts.append(
                        ComplianceAlert(
                            alert_type="document_expiry",
                            severity=alert.alert_level,
                            message=f"{alert.document_name} {'expired' if alert.days_until_expiry < 0 else 'expires'} in {abs(alert.days_until_expiry)} days",
                            due_date=alert.expiry_date,
                            related_document_id=alert.file_id,
                        )
                    )

            # Add arrears alert if applicable
            if financial_status and financial_status.arrears_days > 0:
                severity = "critical" if financial_status.arrears_days > 14 else "warning"
                compliance_alerts.append(
                    ComplianceAlert(
                        alert_type="arrears",
                        severity=severity,
                        message=f"Tenant is {financial_status.arrears_days} days in arrears (${financial_status.current_balance:.2f} owing)",
                        related_tenancy_id=financial_status.tenancy_id,
                    )
                )

            # Build unified output
            state["unified_output"] = UnifiedPropertyData(
                property_id=state["property_id"],
                property_details=property_details,
                owner_contacts=owner_contacts,
                tenant_info=tenant_info,
                financial_status=financial_status,
                recent_communications=recent_communications,
                documents=documents,
                compliance_alerts=compliance_alerts,
                collected_at=datetime.now(),
            )

        except Exception as e:
            state["errors"].append(f"Data transformation failed: {str(e)}")
            state["unified_output"] = None

        return state

    async def validate_output(state: UnifiedCollectionState) -> UnifiedCollectionState:
        """Validate unified output and calculate execution time."""
        # Calculate execution time
        if state.get("start_time"):
            state["execution_time_ms"] = (time.time() - state["start_time"]) * 1000

        # Validate output
        if state["unified_output"] is None and not state["errors"]:
            state["errors"].append("Failed to generate unified output")

        return state

    # Build graph
    graph.add_node("parse_input", parse_input)
    graph.add_node("collect_gmail", collect_gmail)
    graph.add_node("collect_drive", collect_drive)
    graph.add_node("collect_vaultre", collect_vaultre)
    graph.add_node("collect_ailo", collect_ailo)
    graph.add_node("merge_results", merge_results)
    graph.add_node("transform_data", transform_data)
    graph.add_node("validate_output", validate_output)

    # Set entry point
    graph.set_entry_point("parse_input")

    # Add edges - collection happens sequentially in LangGraph
    # (parallel would require different approach or async gathering)
    graph.add_edge("parse_input", "collect_vaultre")
    graph.add_edge("collect_vaultre", "collect_ailo")
    graph.add_edge("collect_ailo", "collect_gmail")
    graph.add_edge("collect_gmail", "collect_drive")
    graph.add_edge("collect_drive", "merge_results")
    graph.add_edge("merge_results", "transform_data")
    graph.add_edge("transform_data", "validate_output")
    graph.add_edge("validate_output", END)

    return graph


def build_parallel_unified_collection_workflow() -> StateGraph:
    """Build workflow with parallel collection using conditional routing.
    
    This version uses async gather within nodes to achieve parallel collection.
    """
    graph = StateGraph(UnifiedCollectionState)

    async def parse_input(state: UnifiedCollectionState) -> UnifiedCollectionState:
        """Parse and validate input parameters."""
        state["start_time"] = time.time()
        state["errors"] = []

        valid_scopes = {"gmail", "drive", "vaultre", "ailo"}
        scope = state.get("collection_scope", list(valid_scopes))
        state["collection_scope"] = [s for s in scope if s in valid_scopes]

        if not state["collection_scope"]:
            state["errors"].append("No valid collection scopes specified")

        return state

    async def parallel_collect_all(state: UnifiedCollectionState) -> UnifiedCollectionState:
        """Collect data from all integrations in parallel."""
        property_id = state["property_id"]
        scope = state["collection_scope"]

        async def collect_gmail_data() -> Optional[GmailCollectionResult]:
            if "gmail" not in scope:
                return None
            try:
                client = get_gmail_client()
                emails = await client.get_property_emails(property_id, days_back=30)
                return GmailCollectionResult(
                    emails=emails,
                    threads=[],
                    total_count=len(emails),
                    collected_at=datetime.now(),
                )
            except Exception as e:
                state["errors"].append(f"Gmail: {str(e)}")
                return None

        async def collect_drive_data() -> Optional[DriveCollectionResult]:
            if "drive" not in scope:
                return None
            try:
                client = get_google_drive_client()
                documents = await client.get_property_documents(property_id)
                alerts = await client.check_document_expiry(property_id, days_ahead=30)
                return DriveCollectionResult(
                    documents=documents,
                    expiry_alerts=alerts,
                    total_count=len(documents),
                    collected_at=datetime.now(),
                )
            except Exception as e:
                state["errors"].append(f"Drive: {str(e)}")
                return None

        async def collect_vaultre_data() -> Optional[VaultRECollectionResult]:
            if "vaultre" not in scope:
                return None
            try:
                client = get_vaultre_client()
                prop = await client.get_property(property_id)
                contacts = await client.get_property_contacts(property_id)
                feedback = await client.list_property_feedback(property_id)
                open_homes = await client.get_open_homes(property_id, include_past=False)
                return VaultRECollectionResult(
                    property=prop,
                    contacts=contacts,
                    feedback=feedback,
                    open_homes=open_homes,
                    collected_at=datetime.now(),
                )
            except Exception as e:
                state["errors"].append(f"VaultRE: {str(e)}")
                return None

        async def collect_ailo_data() -> Optional[AiloCollectionResult]:
            if "ailo" not in scope:
                return None
            try:
                client = get_ailo_client()
                tenancy_id = f"tenancy_{property_id}"
                try:
                    ledger = await client.get_ledger(tenancy_id)
                    tenant = await client.get_tenant_details(tenancy_id)
                    payments = await client.get_payment_history(tenancy_id, limit=5)
                    return AiloCollectionResult(
                        ledger=ledger,
                        tenant=tenant,
                        payment_history=payments,
                        collected_at=datetime.now(),
                    )
                except Exception:
                    return AiloCollectionResult(
                        ledger=None,
                        tenant=None,
                        payment_history=[],
                        collected_at=datetime.now(),
                    )
            except Exception as e:
                state["errors"].append(f"Ailo: {str(e)}")
                return None

        # Run all collections in parallel
        results = await asyncio.gather(
            collect_gmail_data(),
            collect_drive_data(),
            collect_vaultre_data(),
            collect_ailo_data(),
        )

        state["gmail_data"] = results[0]
        state["drive_data"] = results[1]
        state["vaultre_data"] = results[2]
        state["ailo_data"] = results[3]

        return state

    async def transform_and_validate(state: UnifiedCollectionState) -> UnifiedCollectionState:
        """Transform data and validate output."""
        try:
            # Extract property details
            property_details = None
            owner_contacts = []
            if state["vaultre_data"]:
                property_details = state["vaultre_data"].property
                if state["vaultre_data"].contacts:
                    owner_contacts = state["vaultre_data"].contacts.owners

            # Extract tenant info
            tenant_info = None
            financial_status = None
            if state["ailo_data"]:
                tenant_info = state["ailo_data"].tenant
                if state["ailo_data"].ledger:
                    ledger = state["ailo_data"].ledger
                    financial_status = LedgerSummary(
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

            # Extract communications
            recent_communications = []
            if state["gmail_data"]:
                for email in state["gmail_data"].emails[:10]:
                    recent_communications.append(
                        CommunicationEntry(
                            id=email.message_id,
                            type="email",
                            direction="inbound" if "INBOX" in email.labels else "outbound",
                            subject=email.subject,
                            snippet=email.snippet,
                            timestamp=email.received_at,
                            contact_email=email.sender,
                        )
                    )

            # Extract documents and alerts
            documents = []
            compliance_alerts = []
            if state["drive_data"]:
                documents = state["drive_data"].documents
                for alert in state["drive_data"].expiry_alerts:
                    compliance_alerts.append(
                        ComplianceAlert(
                            alert_type="document_expiry",
                            severity=alert.alert_level,
                            message=f"{alert.document_name} {'expired' if alert.days_until_expiry < 0 else 'expires'} in {abs(alert.days_until_expiry)} days",
                            due_date=alert.expiry_date,
                            related_document_id=alert.file_id,
                        )
                    )

            # Add arrears alert
            if financial_status and financial_status.arrears_days > 0:
                severity = "critical" if financial_status.arrears_days > 14 else "warning"
                compliance_alerts.append(
                    ComplianceAlert(
                        alert_type="arrears",
                        severity=severity,
                        message=f"Tenant is {financial_status.arrears_days} days in arrears (${financial_status.current_balance:.2f} owing)",
                        related_tenancy_id=financial_status.tenancy_id,
                    )
                )

            state["unified_output"] = UnifiedPropertyData(
                property_id=state["property_id"],
                property_details=property_details,
                owner_contacts=owner_contacts,
                tenant_info=tenant_info,
                financial_status=financial_status,
                recent_communications=recent_communications,
                documents=documents,
                compliance_alerts=compliance_alerts,
                collected_at=datetime.now(),
            )

        except Exception as e:
            state["errors"].append(f"Transform failed: {str(e)}")
            state["unified_output"] = None

        # Calculate execution time
        if state.get("start_time"):
            state["execution_time_ms"] = (time.time() - state["start_time"]) * 1000

        return state

    # Build graph
    graph.add_node("parse_input", parse_input)
    graph.add_node("parallel_collect", parallel_collect_all)
    graph.add_node("transform_validate", transform_and_validate)

    graph.set_entry_point("parse_input")
    graph.add_edge("parse_input", "parallel_collect")
    graph.add_edge("parallel_collect", "transform_validate")
    graph.add_edge("transform_validate", END)

    return graph
