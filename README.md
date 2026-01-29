## Tenure RE Tech — MCP Server MVP (`TenureMCPAgent`)

An orchestration-ready **Model Context Protocol (MCP) server** for Ray White real estate offices. This MVP focuses on a **policy-aware tool/resource API**, **LangGraph workflows**, and a **mocked middleware layer** for legacy systems (e.g., VaultRE, Ailo) to enable safe, auditable AI workflows like vendor reporting, arrears detection, and document compliance checks.

### Status

This repository is currently a **scaffold**: the PRD, MCP definition, and implementation tasks are defined, while the server and integrations are still being built.

### What this MVP delivers

- **Single-tenant deployment**: one Dockerized service per franchise office.
- **MCP server**: REST interface for tools and resources (versioned contracts).
- **LangGraph orchestrator**: scripted workflows composed from MCP tools/resources.
- **Middleware abstraction**: mocked VaultRE/Ailo clients with realistic schemas/latency.
- **Security controls**: basic RBAC/policy enforcement and HITL gating for risky tools.
- **Observability hooks**: structured logging, correlation IDs, and tracing/metrics targets.

### Non-goals (explicit MVP exclusions)

- No production VaultRE/Ailo/CoreLogic integrations (mocked only)
- No multi-tenant control plane
- No UI/dashboard (HITL is CLI/token based)
- No long-term output storage (ephemeral / local persistence only)
- No advanced RBAC beyond simple role flags

---

## Architecture (high level)

**Agent Interface (LLM Orchestrator)** ⇄ **MCP Server (LangGraph-embedded)** ⇄ **Middleware (Mock Integrations)**  
↳ VaultRE, Ailo, NurtureCloud (via abstract clients)  
↳ **MCP Gateway** enforces policy, RBAC, data minimization, and HITL.

### Core components (MVP)

- **MCP Server**: exposes versioned REST endpoints for tools/resources and orchestrated flows.
- **LangGraph Workflows**: deterministic DAGs for repeatable agent behavior.
- **Middleware Layer**: abstract clients with mock implementations + fixtures.
- **Policy/Gateway Layer**: request-context validation, RBAC rules, output redaction, HITL gating.

---

## MCP surface (draft)

### Resources (read-only)

Draft URI schemes referenced in the PRD and MVP definition (final naming will be normalized during implementation):

- `vault://property/{id}/details` / `vault://properties/{id}/details`
- `vault://property/{id}/feedback` / `vault://properties/{id}/feedback`
- `ailo://ledger/{id}/status` / `ailo://ledgers/{tenancy_id}/summary`
- `vault://properties/{id}/documents` (unstructured document URLs)

### Tools (invokable)

Tools referenced across the PRD + MVP definition (final naming will be normalized during implementation):

- `get_property_details(property_id)`
- `analyze_open_home_feedback(property_id)` → sentiment categories + comment breakdown
- `check_ledger_arrears(tenant_id)` / `calculate_breach_status(tenancy_id)` → arrears/breach risk classification
- `ocr_document(document_id|document_url)` → extract text from uploaded documents
- `extract_expiry_date(text)` → parse expiry dates from extracted text
- `generate_vendor_report(property_id)` → combine feedback + trends into a weekly report payload

---

## Orchestrated workflows (LangGraph)

Planned “predefined agent workflows” / graphs:

- **WeeklyVendorReportFlow**: generate a weekly vendor report from property details + feedback analysis
- **ArrearsDetectionFlow**: detect overdue accounts and classify breach risk
- **ComplianceAuditFlow**: OCR + expiry scan for compliance documents

---

## API contract (planned)

From the PRD:

- **Tool execution**: `POST /tools/{name}`
- **Resource retrieval**: `GET /resources/{path}`
- **Health/version**: `GET /healthz`, `GET /version`
- **Metrics target**: `GET /metrics` (Prometheus-compatible)

### Schema & versioning

- **Pydantic-enforced inputs/outputs**: JSON tool inputs only (no freeform payloads).
- **Versioned schema strategy**: `v1.*` (e.g., `v1.PropertyFeedback`) and versioned routes (e.g., `/v1/tools`).

---

## Security model (MVP)

- **Authentication**: local bearer token (configured per container via `.env`).
- **RBAC**: simple static roles (`agent`, `admin`) used to permit/deny tool calls.
- **Policy enforcement**: middleware that runs before tool execution (RBAC + request context validation + redaction).
- **HITL (Human-in-the-loop)**: “high risk” / mutation tools require a confirmation token (CLI/token-based in MVP).

---

## Observability (targets)

- **Request correlation**: request ID middleware; trace IDs carried through tool execution.
- **Structured logging**: JSON logs with correlation IDs.
- **Tracing**: OpenTelemetry hooks; LangSmith tracing referenced in MVP definition.
- **Langfuse**: planned export of trace context and tags (see tasks).

---

## Repository layout

Current scaffold:

- `tasks/prd.md`: product requirements and architecture overview
- `tasks/mcp-tasks.md`: MVP MCP definition (tools/resources/workflows/security/limits)
- `tasks/tasks.md`: implementation tickets and subtasks
- `backend/`: server implementation location (currently stubbed)
- `.env.example`: environment variable template (currently stubbed)

---

## Getting started (dev)

### Prerequisites

- **Python**: 3.11+
- **uv**: Python package manager ([install uv](https://docs.astral.sh/uv/getting-started/installation/))
- **Docker**: for container deployment (optional for local dev)

### Quick Start

```bash
# Clone and enter the repository
cd tenures-agent

# Copy environment template
cp .env.example .env

# Install dependencies
uv sync --extra dev

# Run the server
uv run uvicorn backend.main:app --reload
```

The server starts at `http://localhost:8000`. Test with:

```bash
curl http://localhost:8000/healthz
```

**Important:** Always use `uv run` to execute commands. This ensures the local `mcp` and `backend` packages are on the Python path. Running `uvicorn` directly with system Python will fail with `ModuleNotFoundError`.

### Running Tests

```bash
uv run pytest
```

### Additional Resources

- **PRD**: `tasks/prd.md`
- **MCP definition**: `tasks/mcp-tasks.md`
- **Implementation plan**: `tasks/tasks.md`
- **API reference**: `docs/configuration.md`

---

## Implementation plan (tickets)

The work is tracked as a set of MVP tickets in `tasks/tasks.md`, including:

- `mcp-core-init`: FastAPI server scaffold, versioning, persistence, env loading, middleware, OpenAPI
- `mcp-surface-init`: define minimal tools/resources + schema validation tests
- `mcp-langgraph-v1`: LangGraph runtime + sample vendor report workflow + orchestration logging
- `middleware-mocks-init`: mocked VaultRE/Ailo client layer + fixtures + latency simulation
- `mcp-policy-gateway`: RBAC matrix, policy middleware, redaction, audit trail
- `mcp-deployment-railway`: Docker/Railway packaging + env + health checks
- `test-suite-init`: unit/integration/e2e workflow tests + CI contract checks
- `mcp-observability`: OpenTelemetry + Langfuse instrumentation + anonymized I/O logging
- `mvp-scope-gates`: hard blocks for excluded features and unsafe paths
- `prod-phase2-scaffold`: forward-looking stubs (tenant_id scoping, real integrations, upgrade path)

---

## Contributing

- Keep tools/resources **schema-first** (Pydantic), deterministic, and auditable.
- Do not add dynamic tool injection or unbounded prompting (see `AGENTS.md`).
- Prefer small, reviewable PRs that map to a single ticket in `tasks/tasks.md`.

---

## License

TBD.
