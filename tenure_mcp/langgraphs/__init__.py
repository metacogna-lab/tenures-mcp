"""LangGraph workflows for MCP Server."""

from tenure_mcp.langgraphs.registry import (
    WorkflowRegistry,
    get_workflow_registry,
    register_workflow,
)

__all__ = ["WorkflowRegistry", "get_workflow_registry", "register_workflow"]
