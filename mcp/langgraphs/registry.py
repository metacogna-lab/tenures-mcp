"""Workflow registry for LangGraph workflows."""

from typing import Any, Callable, Dict, Optional


class WorkflowRegistry:
    """Registry for LangGraph workflows."""

    def __init__(self):
        """Initialize workflow registry."""
        self._workflows: Dict[str, Callable] = {}
        self._workflow_metadata: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        name: str,
        workflow_func: Callable,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a workflow."""
        self._workflows[name] = workflow_func
        self._workflow_metadata[name] = metadata or {}

    def get(self, name: str) -> Optional[Callable]:
        """Get a workflow by name."""
        return self._workflows.get(name)

    def get_metadata(self, name: str) -> Dict[str, Any]:
        """Get workflow metadata."""
        return self._workflow_metadata.get(name, {})

    def list_workflows(self) -> list[str]:
        """List all registered workflows."""
        return list(self._workflows.keys())


# Global workflow registry
_workflow_registry: Optional[WorkflowRegistry] = None


def get_workflow_registry() -> WorkflowRegistry:
    """Get global workflow registry."""
    global _workflow_registry
    if _workflow_registry is None:
        _workflow_registry = WorkflowRegistry()
    return _workflow_registry


def register_workflow(
    name: str, workflow_func: Callable, metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Register a workflow in the global registry."""
    get_workflow_registry().register(name, workflow_func, metadata)
