"""Tier B (Sequencer) Agent manifests."""

from mcp.agents import register_agent
from mcp.schemas.base import AgentManifest


def register_tier_b_agents() -> None:
    """Register all Tier B LangGraph sequencer agents."""

    # Agent: weekly_vendor_report
    register_agent(
        AgentManifest(
            agent_id="agent.pm.weekly_vendor_report",
            version="v1.0.0",
            input_schema={
                "type": "object",
                "properties": {
                    "property_id": {"type": "string", "minLength": 1, "maxLength": 100},
                },
                "required": ["property_id"],
            },
            output_schema={
                "type": "object",
                "properties": {
                    "property_id": {"type": "string"},
                    "report_date": {"type": "string", "format": "date-time"},
                    "feedback_summary": {"type": "object"},
                    "recommendations": {"type": "array", "items": {"type": "string"}},
                },
            },
            permitted_tools=[
                "analyze_open_home_feedback",
                "generate_vendor_report",
            ],
            permitted_resources=[
                "vault://properties/{id}/details",
                "vault://properties/{id}/feedback",
            ],
            rbac_policy_level="Medium",
            workflow_version="v1.0.0",
            prompt_hash=None,
        )
    )

    # Agent: arrears_detection
    register_agent(
        AgentManifest(
            agent_id="agent.pm.arrears_detection",
            version="v1.0.0",
            input_schema={
                "type": "object",
                "properties": {
                    "tenancy_id": {"type": "string", "minLength": 1, "maxLength": 100},
                },
                "required": ["tenancy_id"],
            },
            output_schema={
                "type": "object",
                "properties": {
                    "classification": {"type": "object"},
                    "breach_status": {"type": "object"},
                },
            },
            permitted_tools=["calculate_breach_status"],
            permitted_resources=["ailo://ledgers/{tenancy_id}/summary"],
            rbac_policy_level="Medium",
            workflow_version="v1.0.0",
            prompt_hash=None,
        )
    )

    # Agent: compliance_audit
    register_agent(
        AgentManifest(
            agent_id="agent.pm.compliance_audit",
            version="v1.0.0",
            input_schema={
                "type": "object",
                "properties": {
                    "property_id": {"type": "string", "minLength": 1, "maxLength": 100},
                },
                "required": ["property_id"],
            },
            output_schema={
                "type": "object",
                "properties": {
                    "compliance_status": {"type": "string"},
                    "extracted_dates": {"type": "array"},
                    "issues": {"type": "array"},
                },
            },
            permitted_tools=["ocr_document", "extract_expiry_date"],
            permitted_resources=["vault://properties/{id}/documents"],
            rbac_policy_level="Medium",
            workflow_version="v1.0.0",
            prompt_hash=None,
        )
    )
