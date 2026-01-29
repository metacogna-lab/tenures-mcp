# Tenure MCP Server - Configuration & API Reference

## Product Overview

**Tenure MCP Server** is an orchestration-ready Model Context Protocol (MCP) server for Ray White real estate offices. It enables conversational agents to generate vendor reports, detect rent arrears, and process unstructured documents via secure, policy-enforced tools and resources.

**Current Status:** MVP (v0.1.0) - Core MCP server implemented with mock integrations for VaultRE and Ailo.

---

## API Endpoints

### Health & Diagnostics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Liveness probe - returns `{"status": "healthy"}` |
| `/ready` | GET | Readiness probe - checks database, tools, and resources |
| `/version` | GET | Returns API version metadata |
| `/metrics` | GET | Prometheus-compatible metrics stub |

### Tool Execution

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/tools/{tool_name}` | POST | Execute a registered tool |

**Required Headers:**
- `Authorization: Bearer <token>`
- `X-User-ID`, `X-Tenant-ID`, `X-Auth-Context`, `X-Role`
- `X-HITL-Token` (for Tier C mutation tools)

### Workflow Execution

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/workflows/{workflow_name}` | POST | Execute a LangGraph workflow |

### Query Agent

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/agent/query` | POST | Run query agent: natural language query, returns answer and tool calls used |

**Request body:** `AgentQueryInput` (query, optional max_steps). **Headers:** Same as workflow execution (X-User-ID, X-Tenant-ID, X-Auth-Context, X-Role).

### Resource Retrieval

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/resources/{resource_path}` | GET | Retrieve a read-only resource |

---

## Registered Tools

### Tier A - Stateless Utility Tools (Low Policy)

| Tool Name | Input | Description |
|-----------|-------|-------------|
| `analyze_open_home_feedback` | `property_id` | Sentiment analysis of open home feedback |
| `calculate_breach_status` | `tenancy_id` | Breach risk calculation based on arrears |
| `ocr_document` | `document_url` | OCR text extraction from documents |
| `extract_expiry_date` | `text` | Extract expiry dates from text via regex |

### Tier B - Composite Tools (Medium Policy)

| Tool Name | Input | Description |
|-----------|-------|-------------|
| `generate_vendor_report` | `property_id` | Generate weekly vendor report combining feedback and market trends |

### Tier C - Mutation Tools (High Policy, HITL Required)

| Tool Name | Input | Description |
|-----------|-------|-------------|
| `prepare_breach_notice` | `tenancy_id`, `breach_type` | Draft breach notice document (draft-only in MVP) |
| `web_search` | `query`, optional `max_results` | Search the web (Tavily); use when query needs current/external info |

---

## Registered Resources

| URI Pattern | Source | Description |
|-------------|--------|-------------|
| `vault://properties/{id}/details` | VaultRE | Property listing summary |
| `vault://properties/{id}/feedback` | VaultRE | Open home feedback entries |
| `vault://properties/{id}/documents` | VaultRE | Document URLs (contracts, certificates) |
| `ailo://ledgers/{tenancy_id}/summary` | Ailo | Ledger balance and arrears status |

---

## LangGraph Workflows

| Workflow Name | Input | Flow |
|---------------|-------|------|
| `weekly_vendor_report` | `property_id` | fetch_property → analyze_feedback → generate_report |
| `arrears_detection` | `tenancy_id` | fetch_ledger → calculate_breach → classify_risk |
| `compliance_audit` | `property_id` | fetch_documents → OCR → extract_dates → audit |

---

## Agent Manifests

### Tier A Agents (Stateless Utility)
- `agent.pm.analyze_open_home_feedback` (v1.0.0)
- `agent.pm.calculate_breach_status` (v1.0.0)
- `agent.pm.ocr_document` (v1.0.0)
- `agent.pm.extract_expiry_date` (v1.0.0)
- `agent.pm.get_property_details` (v1.0.0)

### Tier B Agents (Sequencer)
- `agent.pm.weekly_vendor_report` (v1.0.0)
- `agent.pm.arrears_detection` (v1.0.0)
- `agent.pm.compliance_audit` (v1.0.0)

### Tier C Agents (Mutation)
- `agent.pm.prepare_breach_notice` (v1.0.0)

---

## Integration Clients

| Client | Status | Description |
|--------|--------|-------------|
| `VaultREClient` | Mock | Property management data (listings, feedback, documents) |
| `AiloClient` | Mock | Financial ledger data (arrears, payments) |

---

## Policy & Security

### RBAC Matrix

| Role | Access Level |
|------|--------------|
| `agent` | All Tier A/B tools, read-only resources |
| `admin` | All tools including Tier C, no PII redaction |

### HITL (Human-in-the-Loop)

Tools in `HITL_REQUIRED` list require explicit confirmation token via `X-HITL-Token` header:
- `prepare_breach_notice`
- `archive_listing`

### PII Redaction

Non-admin responses automatically redact:
- Email addresses → `[EMAIL]`
- Phone numbers → `[PHONE]`

---

## Storage (SQLite)

| Table | Purpose |
|-------|---------|
| `tool_executions` | Tool execution logs with input/output |
| `workflow_executions` | LangGraph workflow state snapshots |
| `agent_manifests` | Registered agent definitions |
| `audit_log` | Policy decisions and security events |

---

## Configuration (Environment Variables)

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_HOST` | `0.0.0.0` | Server bind address |
| `MCP_SERVER_PORT` | `8000` | Server port |
| `BEARER_TOKEN` | `dev-token-insecure` | API authentication token |
| `ROLE` | `agent` | Default role |
| `DATABASE_PATH` | `./data/tenure_mcp.db` | SQLite database path |
| `VAULTRE_MOCK_ENABLED` | `true` | Use mock VaultRE client |
| `AILO_MOCK_ENABLED` | `true` | Use mock Ailo client |
| `HITL_ENABLED` | `true` | Enable HITL gating |
| `HITL_TOKEN_SECRET` | - | Secret for HITL token validation |
| `LANGSMITH_API_KEY` | - | LangSmith tracing |
| `OPENTELEMETRY_ENABLED` | `true` | Enable OpenTelemetry |
| `OPENAI_API_KEY` | - | OpenAI API key for query agent LLM (required for `/v1/agent/query`) |
| `QUERY_AGENT_MODEL` | `gpt-4o-mini` | Model for query agent |
| `QUERY_AGENT_MAX_STEPS` | `5` | Max tool-calling steps per query |
| `TAVILY_API_KEY` | - | Tavily API key for web_search tool |
| `WEB_SEARCH_MAX_RESULTS` | `5` | Default max results for web search |
| `MCP_SSE_URL` | `http://127.0.0.1:8000/sse` | Base URL for MCP SSE (for future langchain-mcp-adapters client) |

---

## Next Steps

### Phase 1 - MVP Completion
- [ ] Complete unit test coverage for all tools
- [ ] Add integration tests for LangGraph workflows
- [ ] Implement CLI tool (`mcp/cli.py`) for local tool/workflow execution
- [ ] Deploy to Railway with Docker containerization

### Phase 2 - Production Integrations
- [ ] Implement real VaultRE API client (`middleware/vaultre_real.py`)
- [ ] Implement real Ailo API client (`middleware/ailo_real.py`)
- [ ] Add CoreLogic market data integration
- [ ] Migrate from SQLite to PostgreSQL

### Phase 3 - Advanced Features
- [ ] Multi-tenant control plane
- [ ] HITL Panel UI for approval workflows
- [ ] A/B tool version routing
- [ ] LangGraph state persistence and replay
- [ ] Signed agent manifests for supply chain security

### Phase 4 - Observability & Compliance
- [ ] Full Langfuse export with anonymized I/O
- [ ] Cost attribution per agent run
- [ ] Compliance audit dashboard
- [ ] Agent canary runs for change detection

---

## MCP Server launch and architecture

- **Canonical launch:** From repository root: `uv run uvicorn backend.main:app --reload`. Run from repo root so `backend` and `mcp` are importable.
- **Host/port:** Env `MCP_SERVER_HOST`, `MCP_SERVER_PORT`; or pass `--host` / `--port` to uvicorn.
- **Folder layout, transport, CLI:** See [docs/mcp-architecture.md](mcp-architecture.md).

---

## Quick Start

```bash
# Install dependencies (from repo root)
uv sync --extra dev

# Start server
uv run uvicorn backend.main:app --reload

# Test tool execution
curl -X POST http://localhost:8000/v1/tools/analyze_open_home_feedback \
  -H "Authorization: Bearer dev-token-insecure" \
  -H "Content-Type: application/json" \
  -d '{
    "correlation_id": "test-001",
    "context": {
      "user_id": "user_1",
      "tenant_id": "tenant_1",
      "auth_context": "bearer",
      "role": "agent"
    },
    "input_data": {"property_id": "prop_001"}
  }'
```

---

## Docker Deployment

The MCP server can be deployed as a Docker container for local development or production environments.

### Quick Start with Docker Compose

```bash
# Build and start the container
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f mcp-server

# Stop the container
docker-compose down
```

### Manual Docker Build

```bash
# Build the image
docker build -t tenure-mcp-server .

# Run the container
docker run -d \
  --name mcp-server \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  --env-file .env.docker \
  tenure-mcp-server

# Check health
curl http://localhost:8000/healthz
```

### Docker Configuration

The `.env.docker` file contains Docker-specific configuration:

| Variable | Docker Default | Description |
|----------|----------------|-------------|
| `DATABASE_PATH` | `/app/data/tenure_mcp.db` | SQLite path inside container |
| `BEARER_TOKEN` | `docker-dev-token-change-me` | **Change in production!** |
| `HITL_TOKEN_SECRET` | `docker-hitl-secret-change-me` | **Change in production!** |

**Important:** Update `BEARER_TOKEN` and `HITL_TOKEN_SECRET` before deploying to production.

---

## MCP SSE Transport

The server exposes an SSE (Server-Sent Events) endpoint for LLM agent integration using the Model Context Protocol.

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sse/sse` | GET | SSE connection endpoint for MCP clients |
| `/sse/messages/` | POST | Message handling for SSE transport |

### Available Tools via SSE

All Tier A and B tools are exposed via SSE:
- `analyze_open_home_feedback` - Sentiment analysis of property feedback
- `calculate_breach_status` - Tenancy breach risk calculation
- `ocr_document` - Document text extraction
- `extract_expiry_date` - Date extraction from text
- `generate_vendor_report` - Weekly vendor report generation
- `web_search` - Web search via Tavily API

### Connecting MCP Clients

#### Claude Desktop / MCP Client

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "tenure": {
      "url": "http://localhost:8000/sse/sse",
      "transport": "sse"
    }
  }
}
```

#### LangChain MCP Adapter

```python
from langchain_mcp_adapters import MCPToolkit

toolkit = MCPToolkit(
    sse_url="http://localhost:8000/sse/sse",
    messages_url="http://localhost:8000/sse/messages/"
)

# Get tools
tools = toolkit.get_tools()
```

#### Testing SSE Connection

```bash
# Test SSE endpoint is accessible
curl -N http://localhost:8000/sse/sse

# List available tools (requires MCP client)
# The SSE endpoint follows the MCP protocol specification
```

---

## Transport Protocols

The MCP server supports two transport protocols:

| Protocol | Endpoint | Use Case |
|----------|----------|----------|
| **REST API** | `/v1/tools/*`, `/v1/workflows/*` | Direct HTTP integration, CLI, frontend apps |
| **MCP SSE** | `/sse/*` | LLM agent integration (Claude, LangChain, etc.) |

Both protocols provide access to the same tools and resources, with REST offering more flexibility for custom integrations and SSE providing standard MCP protocol compatibility for AI agents.
