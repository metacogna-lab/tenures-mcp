# API Reference

Short summary of the Tenure MCP Server REST API. For full request/response schemas and examples, see the OpenAPI spec.

**Full API spec:** [openapi.yaml](../openapi.yaml) (OpenAPI 3.0.3)

---

## Base URL

- **Local:** `http://localhost:8000`
- **Production (placeholder):** `https://mcp.tenure.com.au`

---

## Authentication

All non-health endpoints require:

- **Header:** `Authorization: Bearer <token>`
- **Context headers (recommended):** `X-User-ID`, `X-Tenant-ID`, `X-Auth-Context`, `X-Role`  
- **Tier C (mutation) tools:** `X-HITL-Token` when HITL is enabled

---

## Endpoints

### Health and diagnostics

| Method | Path       | Description                    |
|--------|------------|--------------------------------|
| GET    | `/healthz` | Liveness — server is running  |
| GET    | `/ready`   | Readiness — DB, tools, resources |
| GET    | `/version` | API version metadata           |
| GET    | `/metrics` | Prometheus-compatible metrics  |

### Tools

| Method | Path                    | Description           |
|--------|-------------------------|-----------------------|
| POST   | `/v1/tools/{tool_name}` | Execute a registered tool |

Tool names: `analyze_open_home_feedback`, `calculate_breach_status`, `ocr_document`, `extract_expiry_date`, `generate_vendor_report`, `prepare_breach_notice`.

### Workflows

| Method | Path                           | Description              |
|--------|--------------------------------|--------------------------|
| POST   | `/v1/workflows/{workflow_name}` | Run a LangGraph workflow |

Workflow names: `weekly_vendor_report`, `arrears_detection`, `compliance_audit`.

### Resources

| Method | Path                          | Description        |
|--------|-------------------------------|--------------------|
| GET    | `/v1/resources/{resource_path}` | Retrieve a resource |

Resource paths follow URI patterns (e.g. `vault://properties/{id}/details`, `ailo://ledgers/{tenancy_id}/summary`). See [configuration.md](configuration.md) for the full list.

---

For request bodies, headers, and response schemas, use [openapi.yaml](../openapi.yaml) or [schemas.md](schemas.md).
