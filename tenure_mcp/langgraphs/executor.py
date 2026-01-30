"""LangGraph workflow executor."""

import uuid
from typing import Any, Dict, List, Optional

from tenure_mcp.schemas.base import RequestContext
from tenure_mcp.storage import get_db
from tenure_mcp.langgraphs.workflows import (
    WorkflowState,
    build_arrears_detection_flow,
    build_compliance_audit_flow,
    build_weekly_vendor_report_flow,
)
from tenure_mcp.langgraphs.unified_collection_workflow import (
    UnifiedCollectionState,
    build_parallel_unified_collection_workflow,
)


class WorkflowExecutor:
    """Executor for LangGraph workflows."""

    def __init__(self):
        """Initialize workflow executor."""
        self.db = get_db()
        # Compile workflows
        self._weekly_vendor_report = build_weekly_vendor_report_flow().compile()
        self._arrears_detection = build_arrears_detection_flow().compile()
        self._compliance_audit = build_compliance_audit_flow().compile()
        self._unified_collection = build_parallel_unified_collection_workflow().compile()

    async def execute_weekly_vendor_report(
        self, property_id: str, context: RequestContext
    ) -> Dict[str, Any]:
        """Execute WeeklyVendorReportFlow."""
        correlation_id = str(uuid.uuid4())

        initial_state: WorkflowState = {
            "property_id": property_id,
            "tenancy_id": None,
            "context": context,
            "step_results": {},
            "final_output": None,
            "error": None,
        }

        try:
            # Execute workflow
            result = await self._weekly_vendor_report.ainvoke(initial_state)

            # Log execution
            self.db.log_audit_event(
                correlation_id=correlation_id,
                event_type="workflow_execution",
                user_id=context.user_id,
                tenant_id=context.tenant_id,
                action="weekly_vendor_report",
                policy_result="completed",
                details={"property_id": property_id, "result": result.get("final_output")},
            )

            return {
                "success": True,
                "correlation_id": correlation_id,
                "workflow_name": "weekly_vendor_report",
                "output": result.get("final_output"),
            }

        except Exception as e:
            self.db.log_audit_event(
                correlation_id=correlation_id,
                event_type="workflow_execution",
                user_id=context.user_id,
                tenant_id=context.tenant_id,
                action="weekly_vendor_report",
                policy_result="failed",
                details={"error": str(e)},
            )
            raise

    async def execute_arrears_detection(
        self, tenancy_id: str, context: RequestContext
    ) -> Dict[str, Any]:
        """Execute ArrearsDetectionFlow."""
        correlation_id = str(uuid.uuid4())

        initial_state: WorkflowState = {
            "property_id": "",
            "tenancy_id": tenancy_id,
            "context": context,
            "step_results": {},
            "final_output": None,
            "error": None,
        }

        try:
            result = await self._arrears_detection.ainvoke(initial_state)

            self.db.log_audit_event(
                correlation_id=correlation_id,
                event_type="workflow_execution",
                user_id=context.user_id,
                tenant_id=context.tenant_id,
                action="arrears_detection",
                policy_result="completed",
                details={"tenancy_id": tenancy_id, "result": result.get("final_output")},
            )

            return {
                "success": True,
                "correlation_id": correlation_id,
                "workflow_name": "arrears_detection",
                "output": result.get("final_output"),
            }

        except Exception as e:
            self.db.log_audit_event(
                correlation_id=correlation_id,
                event_type="workflow_execution",
                user_id=context.user_id,
                tenant_id=context.tenant_id,
                action="arrears_detection",
                policy_result="failed",
                details={"error": str(e)},
            )
            raise

    async def execute_compliance_audit(
        self, property_id: str, context: RequestContext
    ) -> Dict[str, Any]:
        """Execute ComplianceAuditFlow."""
        correlation_id = str(uuid.uuid4())

        initial_state: WorkflowState = {
            "property_id": property_id,
            "tenancy_id": None,
            "context": context,
            "step_results": {},
            "final_output": None,
            "error": None,
        }

        try:
            result = await self._compliance_audit.ainvoke(initial_state)

            self.db.log_audit_event(
                correlation_id=correlation_id,
                event_type="workflow_execution",
                user_id=context.user_id,
                tenant_id=context.tenant_id,
                action="compliance_audit",
                policy_result="completed",
                details={"property_id": property_id, "result": result.get("final_output")},
            )

            return {
                "success": True,
                "correlation_id": correlation_id,
                "workflow_name": "compliance_audit",
                "output": result.get("final_output"),
            }

        except Exception as e:
            self.db.log_audit_event(
                correlation_id=correlation_id,
                event_type="workflow_execution",
                user_id=context.user_id,
                tenant_id=context.tenant_id,
                action="compliance_audit",
                policy_result="failed",
                details={"error": str(e)},
            )
            raise

    async def execute_unified_collection(
        self,
        property_id: str,
        context: RequestContext,
        collection_scope: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Execute UnifiedDataCollection workflow.
        
        Collects data from Gmail, Google Drive, VaultRE, and Ailo integrations
        and returns a unified property data view.
        """
        correlation_id = str(uuid.uuid4())

        initial_state: UnifiedCollectionState = {
            "property_id": property_id,
            "collection_scope": collection_scope or ["gmail", "drive", "vaultre", "ailo"],
            "context": context,
            "gmail_data": None,
            "drive_data": None,
            "vaultre_data": None,
            "ailo_data": None,
            "unified_output": None,
            "errors": [],
            "start_time": 0.0,
            "execution_time_ms": None,
        }

        try:
            result = await self._unified_collection.ainvoke(initial_state)

            self.db.log_audit_event(
                correlation_id=correlation_id,
                event_type="workflow_execution",
                user_id=context.user_id,
                tenant_id=context.tenant_id,
                action="unified_collection",
                policy_result="completed",
                details={
                    "property_id": property_id,
                    "scope": collection_scope,
                    "errors": result.get("errors", []),
                },
            )

            # Serialize output
            output = None
            if result.get("unified_output"):
                output = result["unified_output"].model_dump()

            return {
                "success": True,
                "correlation_id": correlation_id,
                "workflow_name": "unified_collection",
                "output": output,
                "errors": result.get("errors", []),
                "execution_time_ms": result.get("execution_time_ms"),
            }

        except Exception as e:
            self.db.log_audit_event(
                correlation_id=correlation_id,
                event_type="workflow_execution",
                user_id=context.user_id,
                tenant_id=context.tenant_id,
                action="unified_collection",
                policy_result="failed",
                details={"error": str(e)},
            )
            raise


# Global executor
_workflow_executor: WorkflowExecutor | None = None


def get_workflow_executor() -> WorkflowExecutor:
    """Get global workflow executor."""
    global _workflow_executor
    if _workflow_executor is None:
        _workflow_executor = WorkflowExecutor()
    return _workflow_executor
