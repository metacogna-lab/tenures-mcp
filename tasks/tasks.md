### 🧱 1. MCP Server Core Build

**Ticket:** mcp-core-init

**Description:** Implement the core MCP FastAPI server with support for resource and tool endpoints, integrated policy enforcement, and LangGraph compatibility.

**Subtasks:**

* Scaffold FastAPI server with Pydantic-based input/output models
* Implement versioning via route prefixing (e.g., /v1/tools)
* Integrate SQLite3 for persistence (basic table for tasks/logs)
* Load environment variables securely from `.env`
* CLI entrypoint to start dev server with flag for SSE vs HTTP
* Add basic OpenAPI doc auto-generation
* Configure rate limiting and request ID middleware
* Integration with LangGraph task engine

---

### ⚙️ 2. Tool & Resource Surface Definition

**Ticket:** mcp-surface-init

**Description:** Define and implement the minimal viable MCP tools and resources exposed through the MCP Server.

**Subtasks:**

* Define `get_property_summary` resource with hardcoded JSON return
* Define `analyze_open_home_feedback` tool with structured response
* Validate all inputs with Pydantic schemas, enforce field constraints
* Include versioning annotation for each tool/resource
* Register tools and resources in FastAPI routes
* Write validation unit tests for each schema using `pytest`

---

### 🧠 3. LangGraph Orchestration Engine

**Ticket:** mcp-langgraph-v1

**Description:** Define LangGraph workflows that invoke MCP tools to fulfill common workflows like "generate vendor report."

**Subtasks:**

* Create in-memory LangGraph runtime with deterministic paths
* Define sample workflow: Vendor Feedback Report (fetch resource + call tool)
* Add orchestration log table in SQLite for tracing
* Export graph structure as JSON for observability
* Add CLI to execute workflow with parameter
* Unit tests with LangGraph mocking tools/resources

---

### 🧩 4. Middleware Integration Layer

**Ticket:** middleware-mocks-init

**Description:** Create high-fidelity mock clients for VaultRE and Ailo with realistic latency and schema.

**Subtasks:**

* Define abstract service client interfaces for VaultRE and Ailo
* Implement mock versions with fixture data and simulated delays
* Validate response structure against known schema contracts
* Route calls through middleware abstraction layer in server
* Add logging to track integration call usage
* Add tests for stubbed clients with edge cases

---

### 🔐 5. MCP Gateway and Policy Enforcement

**Ticket:** mcp-policy-gateway

**Description:** Introduce embedded policy enforcement that validates user access, tool usage rules, and RBAC logic.

**Subtasks:**

* Define RBAC matrix for each tool (read-only vs critical)
* Implement a policy middleware that runs before tool execution
* Parse and validate request context (user, org, IP)
* Add redaction layer to sanitize outputs based on scope
* Implement logging audit trail for blocked/allowed actions
* Add CLI for simulating different access levels

---

### 📦 6. Deployment Topology and Configuration

**Ticket:** mcp-deployment-railway

**Description:** Package the full stack into a Railway-compatible Docker deployment with secure configuration.

**Subtasks:**

* Write Dockerfile with FastAPI, LangGraph, and SQLite setup
* Add entrypoint script to start server via CLI
* Configure Railway environment secrets injection
* Expose port and health check endpoint
* Document dev vs prod deployment flags
* Test Railway deployment with mock data

---

### 🧪 7. Testing & Validation Infrastructure

**Ticket:** test-suite-init

**Description:** Implement a full test suite including schema validation, tool inputs/outputs, and E2E flow.

**Subtasks:**

* Write unit tests for Pydantic schema edge cases
* Create integration tests for each tool with mocked VaultRE
* Use Jest for CLI commands if TypeScript utilities are added
* Setup LangGraph E2E simulation with sample inputs
* Implement CI step for schema contract checks
* Test failure paths (missing fields, invalid types, tool errors)

---

### 📈 8. Observability & Logging

**Ticket:** mcp-observability

**Description:** Integrate Langfuse with OpenTelemetry and structured logging for traceability.

**Subtasks:**

* Instrument FastAPI with OpenTelemetry trace ID middleware
* Emit structured logs per tool execution
* Export trace context to Langfuse with tags
* Log tool inputs/outputs (anonymized)
* Write SQLite-backed log audit table
* Configure Langfuse project + keys in `.env`

---

### 🚫 9. MVP Exclusion Gates

**Ticket:** mvp-scope-gates

**Description:** Prevent use of unsupported Phase 2/3 features (e.g., HITL dashboards, prod data writes).

**Subtasks:**

* Mark all unsafe endpoints/tools as `@disabled` or raise `NotImplementedError`
* Block production data write commands in middleware
* Gate HITL token validation with stub
* Add warning logs for any Phase 2+ call attempts
* Write tests to ensure disallowed paths raise 403/501

---

### 🗺️ 10. Production Readiness Roadmap & Stubs

**Ticket:** prod-phase2-scaffold

**Description:** Leave architectural stubs for future multi-tenant support, HITL dashboards, and real integrations.

**Subtasks:**

* Add `tenant_id` scoping param to all tool/resource schemas
* Create dashboard-auth module stub with HITL token validation
* Define separate `vaultre_real.py` and `ailo_real.py` modules with `NotImplemented`
* Document upgrade path to PostgreSQL
* Add CLI flags for switching to multi-tenant mode
* Create roadmap markdown file for Phase 2+ deliverables
