"""Pydantic schemas for MCP Server."""

from mcp.schemas.base import (
    AgentManifest,
    BaseRequest,
    BaseResponse,
    ErrorResponse,
    RequestContext,
    ToolExecutionRequest,
    ToolExecutionResponse,
)
from mcp.schemas.tools import (
    AnalyzeFeedbackInput,
    AnalyzeFeedbackOutput,
    CalculateBreachInput,
    CalculateBreachOutput,
    ExtractExpiryInput,
    ExtractExpiryOutput,
    GenerateVendorReportInput,
    GenerateVendorReportOutput,
    OCRDocumentInput,
    OCRDocumentOutput,
    PrepareBreachNoticeInput,
    PrepareBreachNoticeOutput,
)
from mcp.schemas.versioning import VersionedSchema

__all__ = [
    "BaseRequest",
    "BaseResponse",
    "ErrorResponse",
    "RequestContext",
    "ToolExecutionRequest",
    "ToolExecutionResponse",
    "AgentManifest",
    "VersionedSchema",
    "AnalyzeFeedbackInput",
    "AnalyzeFeedbackOutput",
    "CalculateBreachInput",
    "CalculateBreachOutput",
    "ExtractExpiryInput",
    "ExtractExpiryOutput",
    "GenerateVendorReportInput",
    "GenerateVendorReportOutput",
    "OCRDocumentInput",
    "OCRDocumentOutput",
    "PrepareBreachNoticeInput",
    "PrepareBreachNoticeOutput",
]
