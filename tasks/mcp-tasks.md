**Tenure MCP MVP Definition for Agent Generator**

---

### Agent Name:

`TenureMCPAgent`

### Description:

An orchestration-ready MCP server for Ray White real estate offices, enabling conversational agents to generate vendor reports, detect arrears, and process unstructured documents via secure, scoped tools and resources.

### Capabilities:

#### Resources:

* `vault://properties/{id}/details` – Summarized listing information
* `vault://properties/{id}/feedback` – Structured feedback entries
* `ailo://ledgers/{tenancy_id}/summary` – Ledger state and balance data
* `vault://properties/{id}/documents` – Unstructured document URLs

#### Tools:

* `analyze_open_home_feedback(property_id: str)` → Returns sentiment categories and comment breakdown
* `calculate_breach_status(tenancy_id: str)` → Returns legality and breach risk based on rent status and lease terms
* `generate_vendor_report(property_id: str)` → Combines feedback, REA stats, and trends for weekly report generation
* `ocr_document(document_url: str)` → Extracts text from uploaded contracts/certificates
* `extract_expiry_date(text: str)` → Returns parsed date fields from documents

#### Orchestrated Workflows (LangGraph):

* `WeeklyVendorReportFlow`: Runs vendor report generation toolchain
* `ArrearsDetectionFlow`: Detects overdue accounts and returns classification
* `ComplianceAuditFlow`: OCR + expiry scan for unstructured property docs

### Input Validation:

* Pydantic 2.0 Schemas
* JSON tool inputs only (no freeform text allowed)
* Regex-based constraints, max_lengths, and content filtering enforced on all fields

### Data Persistence:

* LangGraph node persistence via SQLite
* Task-level caching in memory (FastAPI lifespan scope)

### Security:

* Authentication via local bearer token in `.env` for each container
* HITL tokens CLI: `tenure-token generate --tool {tool_name}`
* Role: `agent`, `admin` (via static ENV var config)

### Observability:

* LangSmith tracing + OpenTelemetry hooks
* Logging: JSON-structured logs with trace IDs

### Deployment:

* Containerized via Docker
* Single-tenant instance
* Hosted on Railway
* Environment-specific `.env` for VaultRE and Ailo API mocks

### Limitations (Excluded from MVP):

* ❌ No production VaultRE/Ailo/CoreLogic integration
* ❌ No user-facing dashboard or UI shell
* ❌ No multi-tenant control plane
* ❌ No auto-HITL workflows (approval is CLI only)
* ❌ No long-term storage of output (ephemeral cache only)
* ❌ No RBAC beyond role flag
* ❌ No A/B tool version routing

### Tags:

`raywhite`, `realestate`, `vendorreporting`, `ailo`, `vaultre`, `mcp`, `langgraph`, `compliance`, `agenticinfra`

---

This definition can now be copy-pasted into your Agent Generator tooling or LangGraph orchestration stack.
