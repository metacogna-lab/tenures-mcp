# Opinionated Guide to Agent Implementation with MCP

## Purpose

This document defines the strict implementation patterns and security posture for building and managing agents that interact with the MCP (Model Context Protocol) Server. It assumes an agentic execution model orchestrated via LangGraph and governed by policy enforcement via the MCP Gateway.

## Guiding Principles

1. **Least Privilege by Default**: Agents may only invoke tools and read resources they are explicitly scoped to via RBAC.
2. **Immutable Inputs, Deterministic Outputs**: Every tool and resource must enforce schema validation via Pydantic.
3. **Prompt Discipline**: All prompts must be versioned, statically defined, and auditable.
4. **Auditability and Traceability**: Every agent interaction must emit logs, traces, and correlation IDs.
5. **No Tool Chaining Without Policy Check**: Agent-to-agent tool handoff must be explicitly authorized.

---

## Agent Types

### 1. **Stateless Utility Agents**

* Purpose: Execute atomic, side-effect-free functions (e.g., `get_property_details`, `fetch_market_data`).
* Policy Level: Low
* Execution Pattern: Tool-only
* LangGraph Nodes: Stateless, return-only

### 2. **Sequencer Agents**

* Purpose: Compose multiple tools into workflows (e.g., `generate_vendor_report`, `detect_rent_arrears`).
* Policy Level: Medium
* Execution Pattern: Graph with `resource -> tool -> transform -> output`
* Must define and persist workflow DAGs with static configuration.

### 3. **Mutation Agents**

* Purpose: Agents that invoke tools with side effects (e.g., `draft_breach_notice`, `archive_listing`).
* Policy Level: High
* Execution Pattern: Requires HITL token
* Audit Trail: Full serialization of state pre/post invocation
* Observability: LangSmith + OTel required

---

## Naming Conventions

* All agent slugs must follow: `agent.[scope].[function]`

  * Example: `agent.pm.arrears_detection`
* Agent classes should extend `BaseAgent` and define:

  * `input_schema`
  * `output_schema`
  * `permitted_tools`
  * `workflow_version`

---

## Versioning

* Agents must be versioned independently of tools using semver (`v1.2.0`).
* Breaking changes to agent inputs, outputs, or workflows must increment major version.
* Agents must emit their version in all logs and trace metadata.

---

## Security Controls

* Agents must be wrapped in a policy enforcement layer:

  * RBAC: Bound to tenant + user role
  * Redaction: Strip PII before resource delivery
  * HITL: Validate `HITL_TOKEN` for any mutation tools
* No agent may perform tool invocation without explicit declaration of intent via a policy-approved manifest.

---

## Local Development Rules

* Use `.env.agent` for scoped agent variables
* Unit tests must mock all tool executions
* Integration tests must stub API clients and test LangGraph edges

---

## Deployment Contract

Each agent deployment must:

* Include an `AGENT_MANIFEST.json` with version, inputs, tools used, RBAC, and prompt hashes
* Be registered with the Gateway policy engine
* Emit runtime logs to Langfuse and expose trace IDs for user-facing systems

---

## Rejection Criteria

The following are *explicitly disallowed* in MCP agent development:

* Unbounded LLM prompting
* Dynamic tool injection at runtime
* External HTTP calls from within agent graph nodes
* Mutation without trace logging

---

## Future Work

* Integrate signed agent manifests for supply chain security
* Incorporate fine-grained cost attribution per agent run
* Deploy agent canary runs for change detection

---

## Maintainers

* **Primary Owner**: `@mcp-architects`
* **Last Reviewed**: 2026-01-26
* **Next Review Due**: 2026-03-01
