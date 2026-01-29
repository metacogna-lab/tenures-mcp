"""Verify core modules are importable.

Sanity test to ensure the mcp package and key modules can be imported
when running via uv (with the local packages on the Python path).
"""

import pytest


def test_mcp_package_importable():
    """Ensure mcp package and key modules can be imported."""
    from mcp import __version__
    from mcp.config import settings
    from mcp.server import create_app

    assert __version__ == "0.1.0"
    assert settings is not None
    assert callable(create_app)


def test_backend_main_importable():
    """Ensure backend.main module can be imported."""
    from backend.main import app

    assert app is not None
