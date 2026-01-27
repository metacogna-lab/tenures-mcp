"""Tier A (Stateless Utility) Agent manifests."""

from mcp.agents import register_agent
from mcp.schemas.base import AgentManifest
from mcp.schemas.tools import (
    AnalyzeFeedbackInput,
    AnalyzeFeedbackOutput,
    CalculateBreachInput,
    CalculateBreachOutput,
    ExtractExpiryInput,
    ExtractExpiryOutput,
    OCRDocumentInput,
    OCRDocumentOutput,
)


def register_tier_a_agents() -> None:
    """Register all Tier A stateless utility agents."""

    # Agent: analyze_open_home_feedback
    register_agent(
        AgentManifest(
            agent_id="agent.pm.analyze_open_home_feedback",
            version="v1.0.0",
            input_schema=AnalyzeFeedbackInput.model_json_schema(),
            output_schema=AnalyzeFeedbackOutput.model_json_schema(),
            permitted_tools=["analyze_open_home_feedback"],
            permitted_resources=["vault://properties/{id}/feedback"],
            rbac_policy_level="Low",
            workflow_version=None,
            prompt_hash=None,
        )
    )

    # Agent: calculate_breach_status
    register_agent(
        AgentManifest(
            agent_id="agent.pm.calculate_breach_status",
            version="v1.0.0",
            input_schema=CalculateBreachInput.model_json_schema(),
            output_schema=CalculateBreachOutput.model_json_schema(),
            permitted_tools=["calculate_breach_status"],
            permitted_resources=["ailo://ledgers/{tenancy_id}/summary"],
            rbac_policy_level="Low",
            workflow_version=None,
            prompt_hash=None,
        )
    )

    # Agent: ocr_document
    register_agent(
        AgentManifest(
            agent_id="agent.pm.ocr_document",
            version="v1.0.0",
            input_schema=OCRDocumentInput.model_json_schema(),
            output_schema=OCRDocumentOutput.model_json_schema(),
            permitted_tools=["ocr_document"],
            permitted_resources=["vault://properties/{id}/documents"],
            rbac_policy_level="Low",
            workflow_version=None,
            prompt_hash=None,
        )
    )

    # Agent: extract_expiry_date
    register_agent(
        AgentManifest(
            agent_id="agent.pm.extract_expiry_date",
            version="v1.0.0",
            input_schema=ExtractExpiryInput.model_json_schema(),
            output_schema=ExtractExpiryOutput.model_json_schema(),
            permitted_tools=["extract_expiry_date"],
            permitted_resources=[],
            rbac_policy_level="Low",
            workflow_version=None,
            prompt_hash=None,
        )
    )

    # Agent: get_property_details (resource-backed)
    register_agent(
        AgentManifest(
            agent_id="agent.pm.get_property_details",
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
                    "address": {"type": "string"},
                    "property_type": {"type": "string"},
                },
            },
            permitted_tools=[],
            permitted_resources=["vault://properties/{id}/details"],
            rbac_policy_level="Low",
            workflow_version=None,
            prompt_hash=None,
        )
    )
