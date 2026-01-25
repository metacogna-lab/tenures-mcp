Product Requirements Document (PRD)

Product Name: Tenure RE Tech – MVP
Version: 1.0
Date: January 2026
Owner: Tenure Product Architecture Team
Target Client: Ray White Franchise Offices (Pilot: QLD/NSW)

1. Executive Summary

Tenure RE Tech is building an agentic real estate middleware platform that transforms how Ray White agents interact with property, CRM, and financial data. This MVP introduces the foundational platform: an Agentic Orchestrator (LangGraph-based), a policy-aware MCP Server, and a Middleware abstraction for legacy real estate systems (e.g., VaultRE, Ailo). The MVP will enable intelligent workflows for reporting, prospecting, and compliance—packaged as a single-tenant Dockerized service per franchise office.

2. Product Goals and Scope
2.1 Goals

Enable AI-driven workflows in Ray White offices without compromising on security or compliance.

Provide a standardized interface (MCP) to legacy systems through a modular integration layer.

Create a developer-ready monolith that can evolve into a multi-tenant SaaS.

2.2 Scope (MVP)

Single-tenant deployment per Ray White office.

LangGraph-powered Agent Orchestrator with scripted workflows.

MCP Server exposing tools/resources via REST.

Middleware abstraction for VaultRE and Ailo (mocked).

Basic RBAC and policy enforcement via an MCP Gateway.

3. System Architecture Overview
3.1 High-Level Diagram (Text Description)

Agent Interface (LLM Orchestrator) ⇄ MCP Server (LangGraph-embedded) ⇄ Middleware (Mock Integrations)
↳ VaultRE, Ailo, NurtureCloud (via abstract clients)
↳ MCP Gateway enforces policy, RBAC, HITL.

All services run in a Docker container per office. Communication is REST/SSE. Tokens managed via OAuth 2.1 mock flows.

4. Functional Requirements
4.1 MCP Server

Serve REST interface for tools/resources

Handle orchestration sequences (e.g., generate_vendor_report → get_feedback → summarize)

Enforce Pydantic schema for input/output

Rate limiting and logging enabled

4.2 Tools

get_property_details(property_id)

analyze_open_home_feedback(property_id)

check_ledger_arrears(tenant_id)

ocr_document(document_id)

4.3 Resources

vault://property/{id}/details

vault://property/{id}/feedback

ailo://ledger/{id}/status

4.4 Prompts (Predefined Agent Workflows)

generate_weekly_vendor_report(property_id)

prepare_breach_notice(tenant_id)

5. Interface Definitions and Versioning
Pydantic Versioning Strategy

All input/output schemas versioned as v1.PropertyFeedback, etc.

Shared schema library across MCP and Middleware

REST Contracts

/tools/{name} → POST → Execute tool

/resources/{path} → GET → Retrieve resource

/healthz, /version endpoints included

6. Security and Policy
6.1 Gateway Architecture

All traffic to MCP Server routes through MCP Gateway

Policy enforced via code: RBAC, data minimization, HITL

6.2 Zero Trust Enforcement

Service account credentials stored in secrets manager

No long-lived client tokens passed

Mock OAuth 2.1 flow with scoped tokens

6.3 HITL Workflow

Tools with Risk Level High (e.g. payment authorization) blocked unless HITL_CONFIRM_TOKEN provided

7. Middleware Design (Mocked)
7.1 VaultRE

Abstract client mimicking property/feedback endpoints

JSON stub responses defined in vault_mock.py

7.2 Ailo

Ledger API stubbed with ledger balance and transaction list

HITL prompts for any state mutation

8. Deployment Topology
8.1 Monolith Container

Built in Python 3.11 using FastAPI + LangGraph + Pydantic

Dockerized per office

Configurable via .env or secret store

SSE support for LLM communication

Policy engine and API served over HTTPS behind NGINX proxy

9. Testing & Validation

Contract Tests: Schema contract enforcement using Pytest + Schemathesis

Workflow Tests: LangGraph nodes tested in isolation and end-to-end

Security Tests: Simulated injection attempts, token misuse scenarios

Performance: Caching mocks to simulate real latency (~500ms budget per tool call)

10. Observability & Reliability

Built-in logging with correlation IDs per request

Prometheus-compatible metrics exposed at /metrics

Error tracking via Sentry (planned)

Retry/backoff policy in VaultRE client stub

11. MVP Exclusions
Excluded Feature	Rationale
Real integration to VaultRE/Ailo	Stubbing allows fast iteration. Real integration requires commercial/legal agreements.
Multi-tenant deployment	Complexity of tenant isolation, billing, and RBAC too high for MVP.
HITL UI & Notification System	Will use token injection via environment or mock manual interface.
Agent Desktop GUI	LLM interface is assumed to be CLI or developer-controlled in MVP.
Data Lake and NurtureCloud	Too complex to mock accurately in MVP timeframe. Focus on VaultRE/Ailo.
Entra ID/GSuite Auth	OAuth flows mocked. Real IdP integration deferred to production.
12. Roadmap to Production
Phase 2 (Post-MVP)

Real API connections to VaultRE/Ailo (via certified partner)

HITL workflow dashboard for PMs

Multi-tenant cloud orchestration

Compliance audit layer (APPs, ISO)

Full tracing across agent/tool interactions

Tenant scoping with workspace-aware routing

Phase 3

Marketplace for MCP tools across offices

Automated RAG on document archives

Mobile-first agent UI integration