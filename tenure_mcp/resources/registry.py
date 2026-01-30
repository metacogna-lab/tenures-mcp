"""Resource registry for MCP Server."""

from typing import Any, Callable, Dict, Optional


class ResourceRegistry:
    """Registry for MCP resources."""

    def __init__(self):
        """Initialize resource registry."""
        self._resources: Dict[str, Callable] = {}
        self._resource_metadata: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        uri_pattern: str,
        func: Callable,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a resource."""
        self._resources[uri_pattern] = func
        self._resource_metadata[uri_pattern] = metadata or {}

    def get(self, uri: str) -> Optional[tuple[Callable, Dict[str, Any]]]:
        """
        Get a resource handler for URI.

        Returns (handler_func, metadata) or None.
        """
        # Simple pattern matching - in production would use proper URI routing
        for pattern, func in self._resources.items():
            if self._match_pattern(pattern, uri):
                return func, self._resource_metadata.get(pattern, {})
        return None

    def _match_pattern(self, pattern: str, uri: str) -> bool:
        """Simple pattern matching for resource URIs."""
        # Convert pattern to regex-like matching
        pattern_parts = pattern.split("/")
        uri_parts = uri.split("/")

        if len(pattern_parts) != len(uri_parts):
            return False

        for p, u in zip(pattern_parts, uri_parts):
            if p.startswith("{") and p.endswith("}"):
                continue  # Wildcard match
            if p != u:
                return False
        return True

    def list_resources(self) -> list[str]:
        """List all registered resource patterns."""
        return list(self._resources.keys())


# Global resource registry
_resource_registry: Optional[ResourceRegistry] = None


def get_resource_registry() -> ResourceRegistry:
    """Get global resource registry."""
    global _resource_registry
    if _resource_registry is None:
        _resource_registry = ResourceRegistry()
    return _resource_registry


def register_resource(
    uri_pattern: str, func: Callable, metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Register a resource in the global registry."""
    get_resource_registry().register(uri_pattern, func, metadata)


def get_resource(uri: str) -> Optional[tuple[Callable, Dict[str, Any]]]:
    """Get a resource handler from the global registry."""
    return get_resource_registry().get(uri)
