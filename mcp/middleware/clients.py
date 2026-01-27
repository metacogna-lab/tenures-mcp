"""Mock clients for VaultRE and Ailo integrations."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict

from mcp.config import settings


class BaseIntegrationClient(ABC):
    """Base class for integration clients."""

    def __init__(self, mock_enabled: bool = True):
        """Initialize client."""
        self.mock_enabled = mock_enabled

    async def _simulate_latency(self) -> None:
        """Simulate network latency."""
        if self.mock_enabled:
            latency_ms = settings.mock_latency_ms
            await asyncio.sleep(latency_ms / 1000.0)

    @abstractmethod
    async def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """Get property details."""
        pass


class VaultREClient(BaseIntegrationClient):
    """Mock VaultRE client."""

    def __init__(self, mock_enabled: bool = True):
        """Initialize VaultRE client."""
        super().__init__(mock_enabled)
        if not mock_enabled and not settings.production_integrations_enabled:
            raise NotImplementedError("Production VaultRE integration not enabled in MVP")

    async def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """Get property details from VaultRE."""
        await self._simulate_latency()
        # Mock implementation
        return {
            "property_id": property_id,
            "address": "123 Main Street, Brisbane QLD 4000",
            "status": "For Sale",
        }

    async def get_property_feedback(self, property_id: str) -> Dict[str, Any]:
        """Get property feedback from VaultRE."""
        await self._simulate_latency()
        return {
            "property_id": property_id,
            "feedback": [],
        }


class AiloClient(BaseIntegrationClient):
    """Mock Ailo client."""

    def __init__(self, mock_enabled: bool = True):
        """Initialize Ailo client."""
        super().__init__(mock_enabled)
        if not mock_enabled and not settings.production_integrations_enabled:
            raise NotImplementedError("Production Ailo integration not enabled in MVP")

    async def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """Get property details (not typically used for Ailo)."""
        await self._simulate_latency()
        return {}

    async def get_ledger_summary(self, tenancy_id: str) -> Dict[str, Any]:
        """Get ledger summary from Ailo."""
        await self._simulate_latency()
        return {
            "tenancy_id": tenancy_id,
            "current_balance": 0.0,
            "status": "active",
        }


# Global client instances
_vaultre_client: VaultREClient | None = None
_ailo_client: AiloClient | None = None


def get_vaultre_client() -> VaultREClient:
    """Get global VaultRE client."""
    global _vaultre_client
    if _vaultre_client is None:
        _vaultre_client = VaultREClient(mock_enabled=settings.vaultre_mock_enabled)
    return _vaultre_client


def get_ailo_client() -> AiloClient:
    """Get global Ailo client."""
    global _ailo_client
    if _ailo_client is None:
        _ailo_client = AiloClient(mock_enabled=settings.ailo_mock_enabled)
    return _ailo_client
