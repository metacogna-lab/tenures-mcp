# MCP Overview

The **Tenure MCP Server** is a Model Context Protocol (MCP) server that exposes tools, workflows, and resources for Ray White–style real estate operations. It runs behind a policy layer (RBAC, HITL) and integrates with property and ledger data (VaultRE and Ailo, mocked in MVP).

---

## What the MCP server provides

- **Tools** — Single-step operations: analyse open home feedback, calculate breach status, OCR documents, extract expiry dates, generate vendor reports, prepare breach notices (with approval).
- **Workflows** — Multi-step flows: weekly vendor report (property → feedback → report), arrears detection (ledger → breach → risk), compliance audit (documents → OCR → expiry).
- **Resources** — Read-only data: property details/feedback/documents, ledger summary. Addressed by URI (e.g. `vault://properties/{id}/details`, `ailo://ledgers/{tenancy_id}/summary`).

---

## Where to go next

- **[Configuration & API](configuration.md)** — Full list of tools, workflows, resources, endpoints, and environment variables.
- **[Schemas](schemas.md)** — Request/response shapes and validation for tools and workflows.
- **[API Reference](api-reference.md)** — Endpoint summary and link to the full OpenAPI spec ([openapi.yaml](../openapi.yaml)).
