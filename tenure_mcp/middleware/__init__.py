"""Middleware layer for external integrations."""

from tenure_mcp.middleware.clients import AiloClient, VaultREClient, get_ailo_client, get_vaultre_client

__all__ = ["VaultREClient", "AiloClient", "get_vaultre_client", "get_ailo_client"]
