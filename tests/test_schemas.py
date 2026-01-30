"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from tenure_mcp.schemas.tools import (
    AnalyzeFeedbackInput,
    CalculateBreachInput,
    ExtractExpiryInput,
    OCRDocumentInput,
)


def test_analyze_feedback_input_valid():
    """Test valid AnalyzeFeedbackInput."""
    input_data = AnalyzeFeedbackInput(property_id="prop_001")
    assert input_data.property_id == "prop_001"
    assert input_data.version == "v1"


def test_analyze_feedback_input_invalid():
    """Test invalid AnalyzeFeedbackInput."""
    with pytest.raises(ValidationError):
        AnalyzeFeedbackInput(property_id="")  # Empty string

    with pytest.raises(ValidationError):
        AnalyzeFeedbackInput(property_id="prop@001")  # Invalid characters


def test_calculate_breach_input_valid():
    """Test valid CalculateBreachInput."""
    input_data = CalculateBreachInput(tenancy_id="tenancy_001")
    assert input_data.tenancy_id == "tenancy_001"


def test_ocr_document_input_valid():
    """Test valid OCRDocumentInput."""
    input_data = OCRDocumentInput(document_url="https://example.com/doc.pdf")
    assert input_data.document_url == "https://example.com/doc.pdf"

    input_data = OCRDocumentInput(document_url="vault://documents/doc_001.pdf")
    assert input_data.document_url == "vault://documents/doc_001.pdf"


def test_ocr_document_input_invalid():
    """Test invalid OCRDocumentInput."""
    with pytest.raises(ValidationError):
        OCRDocumentInput(document_url="invalid-url")  # Not http/https/vault


def test_extract_expiry_input_valid():
    """Test valid ExtractExpiryInput."""
    input_data = ExtractExpiryInput(text="This document expires on 31/12/2025")
    assert len(input_data.text) > 0


def test_extract_expiry_input_invalid():
    """Test invalid ExtractExpiryInput."""
    with pytest.raises(ValidationError):
        ExtractExpiryInput(text="short")  # Too short
