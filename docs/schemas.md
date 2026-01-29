# Tenure MCP Server - Schema Reference

## Overview

All schemas are defined using Pydantic v2 and follow a versioned schema pattern. Tool schemas inherit from `VersionedSchema` which includes a `version` field (default: `v1`).

---

## Base Schemas

### RequestContext

Context object required for all API requests. Used for authentication, RBAC, and audit logging.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string | ✓ | User identifier |
| `tenant_id` | string | ✓ | Tenant/organization identifier |
| `auth_context` | string | ✓ | Authentication context token |
| `ip_address` | string | | Client IP address |
| `role` | string | | User role: `agent` or `admin` (default: `agent`) |

```json
{
  "user_id": "user_123",
  "tenant_id": "tenant_456",
  "auth_context": "bearer_token_xyz",
  "role": "agent"
}
```

### ToolExecutionRequest

Request payload for tool execution endpoint.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `context` | RequestContext | ✓ | Request context for policy |
| `correlation_id` | string | | UUID for request tracing (auto-generated) |
| `tool_name` | string | ✓ | Name of tool to execute |
| `input_data` | object | ✓ | Tool-specific input parameters |

### ToolExecutionResponse

Response from tool execution.

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Execution success status |
| `correlation_id` | string | Request correlation ID |
| `timestamp` | datetime | Response timestamp |
| `tool_name` | string | Executed tool name |
| `output_data` | object | Tool-specific output |
| `execution_time_ms` | float | Execution duration in milliseconds |
| `trace_id` | string | OpenTelemetry trace ID |

### ErrorResponse

Error response schema.

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `false` |
| `correlation_id` | string | Request correlation ID |
| `timestamp` | datetime | Response timestamp |
| `error` | string | Error message |
| `error_code` | string | Machine-readable error code |
| `details` | object | Additional error details |

---

## Tool Input/Output Schemas

### analyze_open_home_feedback

**Input: `AnalyzeFeedbackInput`**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `property_id` | string | ✓ | 1-100 chars, alphanumeric/hyphen/underscore | Property identifier |
| `version` | string | | default: `v1` | Schema version |

**Output: `AnalyzeFeedbackOutput`**

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | string | Property identifier |
| `total_feedback_count` | integer | Total feedback entries |
| `sentiment_categories` | SentimentCategory[] | Sentiment breakdown |
| `top_comments` | string[] | Top 10 comments |
| `version` | string | Schema version |

**SentimentCategory**

| Field | Type | Description |
|-------|------|-------------|
| `category` | string | Sentiment type (positive/neutral/negative) |
| `count` | integer | Number of entries |
| `percentage` | float | Percentage of total |

---

### calculate_breach_status

**Input: `CalculateBreachInput`**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `tenancy_id` | string | ✓ | 1-100 chars, alphanumeric/hyphen/underscore | Tenancy identifier |
| `version` | string | | default: `v1` | Schema version |

**Output: `CalculateBreachOutput`**

| Field | Type | Description |
|-------|------|-------------|
| `tenancy_id` | string | Tenancy identifier |
| `breach_risk` | BreachRisk | Risk classification |
| `current_balance` | float | Outstanding balance (if negative) |
| `last_payment_date` | datetime | Last payment timestamp |
| `version` | string | Schema version |

**BreachRisk**

| Field | Type | Description |
|-------|------|-------------|
| `level` | string | `low`, `medium`, `high`, or `critical` |
| `days_overdue` | integer | Days past due |
| `breach_legal_status` | string | `compliant`, `at_risk`, or `breached` |
| `recommended_action` | string | Suggested action |

---

### ocr_document

**Input: `OCRDocumentInput`**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `document_url` | string | ✓ | Must start with `http://`, `https://`, or `vault://` | Document URL |
| `version` | string | | default: `v1` | Schema version |

**Output: `OCRDocumentOutput`**

| Field | Type | Description |
|-------|------|-------------|
| `document_url` | string | Processed document URL |
| `extracted_text` | string | OCR extracted text |
| `confidence_score` | float | OCR confidence (0.0-1.0) |
| `page_count` | integer | Number of pages processed |
| `version` | string | Schema version |

---

### extract_expiry_date

**Input: `ExtractExpiryInput`**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `text` | string | ✓ | 10-10000 chars | Text to extract dates from |
| `version` | string | | default: `v1` | Schema version |

**Output: `ExtractExpiryOutput`**

| Field | Type | Description |
|-------|------|-------------|
| `extracted_dates` | ExtractedDate[] | List of extracted dates |
| `version` | string | Schema version |

**ExtractedDate**

| Field | Type | Description |
|-------|------|-------------|
| `field_name` | string | Date field type (e.g., `expiry_date`, `valid_until`) |
| `date_value` | datetime | Parsed date value |
| `confidence` | float | Extraction confidence (0.0-1.0) |

---

### generate_vendor_report

**Input: `GenerateVendorReportInput`**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `property_id` | string | ✓ | 1-100 chars, alphanumeric/hyphen/underscore | Property identifier |
| `version` | string | | default: `v1` | Schema version |

**Output: `GenerateVendorReportOutput`**

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | string | Property identifier |
| `report_date` | datetime | Report generation timestamp |
| `feedback_summary` | object | Aggregated feedback data |
| `market_trends` | object | Market trend analysis |
| `recommendations` | string[] | Action recommendations |
| `version` | string | Schema version |

---

### prepare_breach_notice (Tier C - HITL Required)

**Input: `PrepareBreachNoticeInput`**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `tenancy_id` | string | ✓ | 1-100 chars, alphanumeric/hyphen/underscore | Tenancy identifier |
| `breach_type` | string | ✓ | `rent_arrears`, `lease_violation`, `property_damage` | Type of breach |
| `version` | string | | default: `v1` | Schema version |

**Output: `PrepareBreachNoticeOutput`**

| Field | Type | Description |
|-------|------|-------------|
| `notice_id` | string | Unique notice identifier |
| `tenancy_id` | string | Tenancy identifier |
| `breach_type` | string | Type of breach |
| `draft_content` | string | Draft breach notice content |
| `status` | string | `draft` or `pending_approval` |
| `created_at` | datetime | Creation timestamp |
| `version` | string | Schema version |

---

### web_search

**Input: `WebSearchInput`**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `query` | string | ✓ | 1-500 chars | Search query |
| `max_results` | integer | | 1-10, default: 5 | Maximum number of results to return |

**Output: `WebSearchOutput`**

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | Original query |
| `results` | WebSearchResultItem[] | List of search results |
| `total_returned` | integer | Number of results returned |

**WebSearchResultItem**

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Result title |
| `url` | string | Result URL |
| `snippet` | string | Short excerpt or summary |

---

## Agent Query Schemas

Used by `POST /v1/agent/query` (variable input, LLM + tools including web search).

### AgentQueryInput

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `query` | string | ✓ | 1-10000 chars | Natural language query |
| `max_steps` | integer | | 1-20, default: 5 | Maximum tool-calling steps |

### AgentQueryOutput

| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | Final answer to the user |
| `tool_calls_used` | object[] | List of tool invocations (name, args) |
| `correlation_id` | string | Request correlation ID |

---

## Agent Manifest Schema

### AgentManifest

Registration schema for agent deployment.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agent_id` | string | ✓ | Agent identifier (e.g., `agent.pm.get_property_details`) |
| `version` | string | ✓ | Semver version (e.g., `v1.0.0`) |
| `input_schema` | object | ✓ | JSON Schema for input validation |
| `output_schema` | object | ✓ | JSON Schema for output validation |
| `permitted_tools` | string[] | | List of allowed tool names |
| `permitted_resources` | string[] | | List of allowed resource URI patterns |
| `rbac_policy_level` | string | ✓ | `Low`, `Medium`, or `High` |
| `workflow_version` | string | | LangGraph workflow version |
| `prompt_hash` | string | | SHA256 hash of static prompts |
| `created_at` | datetime | | Registration timestamp |

---

## Resource Response Schemas

### Property Details Resource

URI: `vault://properties/{id}/details`

```json
{
  "property_id": "prop_001",
  "address": "123 Main Street, Brisbane QLD 4000",
  "property_type": "House",
  "bedrooms": 3,
  "bathrooms": 2,
  "price": 650000,
  "status": "For Sale",
  "listed_date": "2025-01-15"
}
```

### Property Feedback Resource

URI: `vault://properties/{id}/feedback`

```json
{
  "property_id": "prop_001",
  "feedback_entries": [
    {
      "feedback_id": "fb_001",
      "date": "2025-01-20",
      "comment": "Great location, love the neighborhood",
      "sentiment": "positive"
    }
  ]
}
```

### Ledger Summary Resource

URI: `ailo://ledgers/{tenancy_id}/summary`

```json
{
  "tenancy_id": "tenancy_001",
  "property_id": "prop_001",
  "current_balance": -150.0,
  "last_payment_date": "2025-01-10",
  "next_payment_due": "2025-02-10",
  "rent_amount": 500.0,
  "status": "active"
}
```

### Property Documents Resource

URI: `vault://properties/{id}/documents`

```json
{
  "property_id": "prop_001",
  "documents": [
    {
      "document_id": "doc_001",
      "document_type": "contract",
      "url": "vault://documents/doc_001.pdf",
      "uploaded_date": "2025-01-15"
    }
  ]
}
```

---

## Validation Rules

### ID Format

All `property_id` and `tenancy_id` fields must match pattern: `^[a-zA-Z0-9_-]+$`

### URL Format

Document URLs must start with:
- `http://`
- `https://`
- `vault://` (internal document storage)

### Role Validation

`role` field must be one of: `agent`, `admin`

### Breach Type Validation

`breach_type` must be one of: `rent_arrears`, `lease_violation`, `property_damage`

### Confidence Scores

All confidence scores are bounded: `0.0 <= confidence <= 1.0`

---

## Frontend-facing API

This section documents request shapes, headers, flow→MCP mapping, and client-side validation for the agent console frontend. Source of truth for request/response schemas: `mcp/schemas/base.py` and `mcp/schemas/tools.py`.

### Request shapes

**POST /v1/tools/{name}**

Request body must match `ToolExecutionRequest`:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `context` | RequestContext | ✓ | `user_id`, `tenant_id`, `auth_context`, `role` (see Base Schemas) |
| `correlation_id` | string | | Optional; server generates if omitted |
| `tool_name` | string | ✓ | Tool identifier (e.g. `analyze_open_home_feedback`) |
| `input_data` | object | ✓ | Tool-specific input (see Tool Input/Output Schemas above) |

Required headers:

- `Content-Type: application/json`
- `Authorization: Bearer <token>`
- `X-User-ID`, `X-Tenant-ID`, `X-Auth-Context`, `X-Role` (recommended for audit)
- `X-HITL-Token` (required for Tier C / mutation tools when HITL is enabled)

**POST /v1/workflows/{name}**

Request body is a JSON object with either `property_id` or `tenancy_id` depending on the workflow (see Flow→MCP mapping below).

Required headers:

- `Content-Type: application/json`
- `Authorization: Bearer <token>`
- `X-User-ID`
- `X-Tenant-ID`
- `X-Auth-Context`
- `X-Role`

### Flow → MCP mapping

| Flow identifier | MCP endpoint type | MCP endpoint id | Required inputs |
|-----------------|------------------|-----------------|------------------|
| `weekly_vendor_report` | workflow | `weekly_vendor_report` | `property_id` |
| `arrears_detection` | workflow | `arrears_detection` | `tenancy_id` |
| `compliance_audit` | workflow | `compliance_audit` | `property_id` |
| `analyze_open_home_feedback` | tool | `analyze_open_home_feedback` | `property_id` |
| `calculate_breach_status` | tool | `calculate_breach_status` | `tenancy_id` |
| `generate_vendor_report` | tool | `generate_vendor_report` | `property_id` |
| `prepare_breach_notice` | tool | `prepare_breach_notice` | `tenancy_id`, `breach_type` |
| `ocr_document` | tool | `ocr_document` | `document_url` |
| `extract_expiry_date` | tool | `extract_expiry_date` | `text` |

### Client-side validation

The frontend **must** validate all inputs before calling MCP. Do not submit requests until validation passes. Apply the same rules as in **Validation Rules** above:

- **property_id / tenancy_id:** Pattern `^[a-zA-Z0-9_-]+$`, length 1–100.
- **document_url:** Must start with `http://`, `https://`, or `vault://`.
- **breach_type:** One of `rent_arrears`, `lease_violation`, `property_damage`.
- **text** (extract_expiry_date): Length 10–10000.
- **role:** One of `agent`, `admin`.

Show field-level errors from validation and do not call the API until all errors are resolved.
