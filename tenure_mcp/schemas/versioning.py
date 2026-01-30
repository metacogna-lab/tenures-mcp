"""Versioning utilities for schemas."""

from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class VersionedSchema(BaseModel):
    """Base class for versioned schemas."""

    version: str = "v1"

    @classmethod
    def get_version(cls) -> str:
        """Get schema version."""
        return getattr(cls, "version", "v1")
