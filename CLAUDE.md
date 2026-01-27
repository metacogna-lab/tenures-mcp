# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**TenureMCPAgent** is an orchestration-ready Model Context Protocol (MCP) server for Ray White real estate offices. It enables conversational agents to generate vendor reports, detect rent arrears, and process unstructured documents via secure, policy-enforced tools and resources.

**Status:** Active development - Core MCP server implemented (~3000 lines), tools and workflows in place, testing infrastructure established.

## Architecture

### Core Components

- **MCP Server**: FastAPI-based REST interface exposing versioned tools and resources
- **LangGraph Orchestrator**: Deterministic workflow engine for multi-step agent tasks
- **Middleware Layer**: Abstract client interfaces for VaultRE and Ailo (mocked for MVP)
- **Policy Gateway**: RBAC enforcement, data redaction, and HITL (Human-in-the-Loop) gating
- **Storage**: SQLite3 for persistence (tool execution logs, workflow state, resource history)

### Directory Structure

```
mcp/                      # Core MCP server implementation (~31 Python files)
├── config.py             # Pydantic settings (env config)
├── langgraphs/           # LangGraph workflow definitions
│   ├── executor.py       # Workflow execution engine
│   ├── registry.py       # Workflow registration
│   └── workflows.py      # Workflow implementations
├── middleware/           # Integration layer
│   └── clients.py        # Mock VaultRE/Ailo clients
├── resources/            # MCP resource implementations
│   ├── implementations.py
│   └── registry.py
├── tools/                # MCP tool implementations
│   ├── implementations.py  # Core tools (feedback, breach, OCR)
│   ├── mutation_tools.py   # High-risk mutation tools
│   └── registry.py         # Tool registration
└── schemas/              # Pydantic schema definitions
    ├── base.py           # Base schemas (RequestContext)
    ├── tools.py          # Tool input/output schemas
    └── resources.py      # Resource schemas

backend/
├── db/                   # SQLite schemas and migrations
├── graph/                # Additional graph utilities
├── integrations/         # Integration helpers
├── llm/                  # LLM utilities
├── models/               # Data models
├── src/                  # Core server logic (FastAPI routes)
└── main.py               # FastAPI application entrypoint

tests/                    # Test suite
├── test_schemas.py       # Schema validation tests
├── test_tools.py         # Tool execution tests
├── test_policy.py        # RBAC/policy tests
├── test_workflows.py     # LangGraph workflow tests
└── test_tier_c_agents.py # Agent integration tests

tasks/
├── prd.md                # Product requirements document
├── mcp-tasks.md          # MVP MCP definition
├── tasks.md              # Implementation roadmap
└── architecture.md       # Architecture design

pyproject.toml            # Project dependencies and tooling config
.env.example              # Environment variable template
```

## Development Commands

### Environment Setup

**Python 3.11+** required. Use `uv` for all package management (NOT pip):

```bash
# Install project with dependencies
uv sync

# Install development dependencies
uv sync --extra dev

# Add new dependency
uv add <package>

# Add development dependency
uv add --dev <package>

# Start development server
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**NEVER create requirements.txt** - use `uv add` commands exclusively per Cursor rules.

**Key Dependencies (from pyproject.toml):**
- FastAPI 0.104+ - REST API framework
- Pydantic 2.5+ - Schema validation and settings
- LangGraph 0.0.40+ - Workflow orchestration
- LangSmith 0.1+ - LangGraph tracing
- OpenTelemetry 1.21+ - Distributed tracing
- pytest 7.4+ - Testing framework
- ruff, black, mypy - Code quality tools

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_tools.py

# Run with coverage
uv run pytest --cov=mcp --cov=backend

# Run async tests
uv run pytest -v tests/test_workflows.py
```

### Code Quality

```bash
# Format code with Black (100 char line length)
uv run black mcp/ backend/ tests/

# Lint with Ruff
uv run ruff check mcp/ backend/ tests/

# Fix auto-fixable lint issues
uv run ruff check --fix mcp/ backend/ tests/

# Type checking with mypy
uv run mypy mcp/ backend/

# Run all quality checks
uv run black mcp/ backend/ tests/ && uv run ruff check mcp/ backend/ tests/ && uv run mypy mcp/ backend/
```

### MCP CLI (planned)

```bash
# Execute individual tool
uv run python mcp/cli.py run-tool <tool_name> --input input.json

# Execute LangGraph workflow
uv run python mcp/cli.py run-graph <graph_name> --input state.json

# Generate HITL confirmation token
uv run python mcp/cli.py generate-token --tool <tool_name>
```

## MCP Surface

### Resources (read-only)

Resources return structured data without side effects:

- `vault://properties/{id}/details` - Property listing summary
- `vault://properties/{id}/feedback` - Open home feedback entries
- `ailo://ledgers/{tenancy_id}/summary` - Ledger balance and arrears status
- `vault://properties/{id}/documents` - Document URLs (contracts, certificates)

### Tools (invokable)

Tools perform operations and return typed outputs:

- `analyze_open_home_feedback(property_id)` - Sentiment analysis and comment categorization
- `calculate_breach_status(tenancy_id)` - Arrears detection and breach risk classification
- `generate_vendor_report(property_id)` - Weekly vendor report generation
- `ocr_document(document_url)` - Text extraction from uploaded documents
- `extract_expiry_date(text)` - Parse expiry dates from extracted text

### Orchestrated Workflows (LangGraph)

Multi-step deterministic workflows:

- `WeeklyVendorReportFlow` - Combines property details, feedback analysis, and market trends
- `ArrearsDetectionFlow` - Detects overdue accounts and calculates breach risk
- `ComplianceAuditFlow` - OCR and expiry scanning for compliance documents

## Implementation Patterns

### Tool Registration System

Tools are registered via a global registry pattern (`mcp/tools/registry.py`):

```python
from mcp.tools.registry import register_tool

# Register a tool with metadata
register_tool(
    name="analyze_feedback",
    func=analyze_feedback_implementation,
    metadata={
        "version": "v1.0",
        "requires_hitl": False,
        "allowed_roles": ["agent", "admin"]
    }
)

# Retrieve and execute
tool = get_tool("analyze_feedback")
result = await tool(input_data, context)
```

### Resource URI Pattern

Resources follow URI-based addressing (`vault://`, `ailo://`):

```python
# Resource URIs
vault://properties/{property_id}/details
vault://properties/{property_id}/feedback
ailo://ledgers/{tenancy_id}/summary
vault://properties/{property_id}/documents
```

### Schema-First Development

All tool inputs/outputs are Pydantic models in `mcp/schemas/tools.py`:

```python
class AnalyzeFeedbackInput(BaseModel):
    property_id: str = Field(..., pattern=r"^prop_\d+$")

class AnalyzeFeedbackOutput(BaseModel):
    property_id: str
    total_feedback: int
    sentiment_breakdown: Dict[SentimentCategory, int]
    comments_by_sentiment: Dict[SentimentCategory, List[str]]
```

### Request Context

All operations receive a `RequestContext` for authentication and tracing:

```python
class RequestContext(BaseModel):
    user_id: str
    role: str  # "agent" or "admin"
    tenant_id: Optional[str] = None
    correlation_id: str
    timestamp: datetime
```

## Implementation Standards

### Agent Development (per AGENTS.md)

**Security Controls:**
- All agents must declare `permitted_tools` in manifest
- RBAC enforcement via Policy Gateway (role: `agent` or `admin`)
- HITL tokens required for mutation tools
- Full audit trail with correlation IDs and trace logging

**Agent Types:**
1. **Stateless Utility Agents** - Atomic, side-effect-free tools (low policy level)
2. **Sequencer Agents** - Multi-tool workflows via LangGraph (medium policy level)
3. **Mutation Agents** - Side effects requiring HITL tokens (high policy level)

**Naming Convention:** `agent.[scope].[function]` (e.g., `agent.pm.arrears_detection`)

**Versioning:** Semver (`v1.0.0`), emit version in all logs and trace metadata

**Explicitly Disallowed:**
- Unbounded LLM prompting
- Dynamic tool injection at runtime
- External HTTP calls from graph nodes
- Mutation without trace logging

### Python Patterns

**Schema Validation:**
- All tool inputs/outputs defined with Pydantic 2.0 schemas
- Enforce field constraints (max_length, regex, content filtering)
- Version all schemas (e.g., `v1.PropertyFeedback`)

**Error Handling:**
- Use typed exceptions, not generic `Exception`
- Log all errors with correlation IDs
- Return structured error responses

**LangGraph Workflows:**
- Define clear single-responsibility nodes
- Use TypedDict for state definitions
- Prefer DAGs over cycles (use cycles only for essential feedback loops)
- Colocate workflow definitions in `backend/graph/`
- Include path tests for each workflow

**Observability:**
- OpenTelemetry trace ID middleware on all requests
- JSON-structured logs with correlation IDs
- LangSmith tracing for all LangGraph executions
- Langfuse export with anonymized tool I/O

### API Design

**Versioning:**
- Route prefixing: `/v1/tools/{name}`, `/v1/resources/{path}`
- Schema versioning: `v1.*` namespace for Pydantic models

**Endpoints:**
- `POST /v1/tools/{name}` - Execute tool with JSON payload
- `GET /v1/resources/{path}` - Retrieve resource by URI
- `GET /healthz` - Health check endpoint
- `GET /version` - Server version metadata
- `GET /metrics` - Prometheus-compatible metrics

**Middleware:**
- Request ID generation and propagation
- RBAC policy enforcement
- Data redaction for PII
- Rate limiting
- CORS configuration

## Security Model

### Authentication
- Local bearer token per container (configured via `.env`)
- Token format: `Authorization: Bearer <token>`

### RBAC
- Static roles: `agent` (read + tool execution), `admin` (full access)
- Role enforcement at Policy Gateway layer
- Per-tool permission matrix defined in policy config

### HITL (Human-in-the-Loop)
- High-risk/mutation tools require confirmation token
- Token generation: CLI-based in MVP
- Request logged as "pending" until confirmed
- Audit trail for all HITL approvals/rejections

### Data Protection
- PII redaction in resource responses
- Anonymized I/O logging
- No production data writes in MVP (middleware mocked)

## Testing Strategy

### Unit Tests
- Pydantic schema validation edge cases
- Individual tool logic with mocked dependencies
- Policy enforcement rules
- Error handling paths

### Integration Tests
- Tool execution with mocked VaultRE/Ailo clients
- LangGraph workflow paths with sample inputs
- FastAPI endpoint contract validation

### E2E Tests
- Full workflow simulation (resource → tool → output)
- Policy enforcement scenarios (RBAC, HITL)
- Failure path validation (missing fields, invalid types)

## MVP Scope Limitations

**Explicitly excluded from MVP:**
- ❌ Production VaultRE/Ailo/CoreLogic integrations (mocked only)
- ❌ Multi-tenant control plane (single-tenant per container)
- ❌ User-facing dashboard or UI (CLI/API only)
- ❌ Long-term output storage (ephemeral/local only)
- ❌ Advanced RBAC (simple role flags only)
- ❌ A/B tool version routing
- ❌ Auto-HITL workflows (manual CLI approval only)

**Phase 2 scaffolding:**
- `tenant_id` parameter added to schemas but not enforced
- Separate `vaultre_real.py` and `ailo_real.py` stub modules
- PostgreSQL upgrade path documented
- Multi-tenant mode CLI flags (disabled)

## Implementation Roadmap

The 10 core MVP tickets are tracked in `tasks/tasks.md`:

1. **mcp-core-init** - FastAPI server scaffold, versioning, SQLite, middleware
2. **mcp-surface-init** - Tool/resource definitions and schema validation
3. **mcp-langgraph-v1** - LangGraph runtime and sample workflows
4. **middleware-mocks-init** - VaultRE/Ailo mock clients with fixtures
5. **mcp-policy-gateway** - RBAC, redaction, audit trail
6. **mcp-deployment-railway** - Docker packaging and Railway deployment
7. **test-suite-init** - Unit/integration/E2E test infrastructure
8. **mcp-observability** - OpenTelemetry, Langfuse, structured logging
9. **mvp-scope-gates** - Hard blocks for excluded features
10. **prod-phase2-scaffold** - Forward-looking stubs for production evolution

## Configuration

### Environment Variables

Configuration managed via Pydantic Settings (loads from `.env` automatically). See `mcp/config.py` for all settings:

**Server:**
- `MCP_SERVER_HOST` - Server bind address (default: `0.0.0.0`)
- `MCP_SERVER_PORT` - Server port (default: `8000`)
- `MCP_API_VERSION` - API version prefix (default: `v1`)

**Authentication:**
- `BEARER_TOKEN` - Bearer token for API authentication (REQUIRED)
- `ROLE` - Role for this instance: `agent` or `admin` (default: `agent`)

**Database:**
- `DATABASE_PATH` - SQLite database path (default: `./data/tenure_mcp.db`)

**Observability:**
- `LANGSMITH_API_KEY` - LangSmith API key for tracing
- `LANGSMITH_PROJECT` - LangSmith project name (default: `tenure-mcp-mvp`)
- `OPENTELEMETRY_ENABLED` - Enable OpenTelemetry (default: `true`)
- `LANGFUSE_SECRET_KEY` - Langfuse secret key
- `LANGFUSE_PUBLIC_KEY` - Langfuse public key
- `LANGFUSE_HOST` - Langfuse endpoint (default: `https://cloud.langfuse.com`)

**Mock Integrations:**
- `VAULTRE_MOCK_ENABLED` - Use mock VaultRE client (default: `true`)
- `AILO_MOCK_ENABLED` - Use mock Ailo client (default: `true`)
- `MOCK_LATENCY_MS` - Simulated API latency (default: `500`)

**HITL:**
- `HITL_ENABLED` - Enable Human-in-the-Loop gating (default: `true`)
- `HITL_TOKEN_SECRET` - Secret for HITL token generation

**Feature Flags:**
- `MULTI_TENANT_ENABLED` - Enable multi-tenant mode (default: `false`, MVP excluded)
- `PRODUCTION_INTEGRATIONS_ENABLED` - Use real APIs (default: `false`, MVP excluded)

### Observability Targets

- **LangSmith** - Trace LangGraph workflow execution
- **Langfuse** - Export tool I/O with anonymization
- **OpenTelemetry** - Request correlation and trace propagation
- **Prometheus** - Metrics export via `/metrics` endpoint

## Contributing Guidelines

1. **Schema-first development** - Define Pydantic models before implementation
2. **Small, reviewable PRs** - Map each PR to a single ticket in `tasks/tasks.md`
3. **Deterministic, auditable tools** - No dynamic behavior or unbounded prompting
4. **Test coverage required** - Unit tests for all tools, integration tests for workflows
5. **Security by default** - RBAC checks, PII redaction, HITL gating for mutations
6. **Observability mandatory** - Correlation IDs, structured logs, trace exports

## Quick Start

```bash
# 1. Create .env file from example
cp .env.example .env

# 2. Edit .env and set BEARER_TOKEN
echo "BEARER_TOKEN=your-secret-token-here" >> .env

# 3. Install dependencies
uv sync --extra dev

# 4. Run tests to verify setup
uv run pytest

# 5. Start the server
uv run uvicorn backend.main:app --reload
```

## Common Development Workflows

### Adding a New Tool

1. Define input/output schemas in `mcp/schemas/tools.py`
2. Implement tool logic in `mcp/tools/implementations.py`
3. Register tool in `mcp/tools/registry.py`
4. Add unit tests in `tests/test_tools.py`
5. Update RBAC policy if needed

### Adding a New Resource

1. Define resource URI pattern in documentation
2. Implement resource handler in `mcp/resources/implementations.py`
3. Register resource in `mcp/resources/registry.py`
4. Add retrieval tests in `tests/test_resources.py`

### Creating a LangGraph Workflow

1. Define workflow state TypedDict in `mcp/langgraphs/workflows.py`
2. Create node functions (single responsibility)
3. Build graph with `StateGraph` from langgraph
4. Register in `mcp/langgraphs/registry.py`
5. Add path tests in `tests/test_workflows.py`

### Running Integration Tests

```bash
# Test tool execution with mocked clients
uv run pytest tests/test_tools.py -v

# Test LangGraph workflows
uv run pytest tests/test_workflows.py -v

# Test policy enforcement
uv run pytest tests/test_policy.py -v
```

## Key Files to Review

**Architecture & Planning:**
- `tasks/prd.md` - Complete product requirements and architecture
- `tasks/mcp-tasks.md` - MVP MCP definition and capabilities
- `tasks/tasks.md` - 10 implementation tickets with subtasks
- `AGENTS.md` - Opinionated agent implementation standards

**Implementation Core:**
- `mcp/config.py` - Settings and environment configuration
- `mcp/tools/implementations.py` - Core tool logic
- `mcp/schemas/tools.py` - Input/output schemas
- `mcp/langgraphs/workflows.py` - Workflow definitions

**Standards & Rules:**
- `.cursor/rules/mcp.mdc` - MCP development standards
- `.cursor/rules/langgraph.mdc` - LangGraph best practices
- `.cursor/rules/python.mdc` - Python tooling standards (uv usage)
- `.cursor/rules/docker.mdc` - Docker/container best practices

**Configuration:**
- `pyproject.toml` - Dependencies and tool configuration
- `.env.example` - Environment variable template
- `.gitignore` - Version control exclusions
