# Frontend – Agent Console

## Overview

The frontend is an **agent console** for Ray White–style workflows. It integrates with the MCP server to run tools and workflows (vendor reports, rental arrears, breach notices, open home feedback, document OCR, expiry extraction). The experience is **function-first**: after a minimal landing screen, the primary surface is the console where users select flows and execute them. The stack is procedural MCP calls today, with optional LLM integration later.

## Design system

Design tokens and global styles live in:

- **CSS variables and base styles:** `frontend/src/index.css`
- **Tailwind theme:** `frontend/tailwind.config.js`

**Colour**

- **Base:** Black/dark stack (`#09090b`, `#0f0f12`, `#18181b`) for backgrounds.
- **Accent:** Yellow primary (`#FACC15` / `#EAB308`) for primary actions, highlights, and glow shadows. Use `accent-primary`, `accent-primary-hover`, and `shadow-glow-sm` (or equivalent) only—no hard-coded hex for accent.
- **Semantic:** Success, danger, warning, and info colours are defined in the theme for status and feedback.

**Typography**

- **Sans:** Inter for UI.
- **Mono:** JetBrains Mono for code and IDs.
- Section labels use optional uppercase + letter-spacing via the `.label-uppercase` utility.

**Spacing and density**

- Use the existing spacing scale. Layouts (Landing, Console) use generous padding and margins for **low information density** and a single primary action per screen where possible.

## Architecture

**Routing**

- `/` – Landing: minimal hero (headline, subhead, primary CTA “Open Console” → `/console`). Function-first: one click to the console.
- `/console` – Primary work surface: console shell with flow cards, execution form, and result area.
- `/console/flow/:id` – Focused flow view: same console with the selected flow (e.g. `weekly_vendor_report`, `prepare_breach_notice`).

**Layout**

- **Header:** Logo/brand, connection status, version.
- **Tabs:** Flows (primary), Testing Guide, LangGraph Demo.
- **Main (Flows tab):** Left: flow cards. Right: input form and response (success/error + JSON or terminal-style output).
- **Footer:** MCP connection status and version.

**Data and API**

- All MCP calls go through `frontend/src/hooks/useMcpApi.ts`: `checkHealth`, `checkReady`, `executeTool`, `executeWorkflow`, `fetchResource`. No API contract changes required for the current plan.

## Mock data

Mock data is aligned to `mcp/schemas/` and `docs/schemas.md` for demos, form defaults, and optional fallback when MCP is unavailable.

- **Location:** `frontend/src/data/mock.ts` (and flow list in `frontend/src/data/flowConfig.ts`).
- **Content:** Tool input/output mocks, resource response mocks, and `RequestContext` for demo requests. All use **Australian real estate and Ray White terminology** (vendor, tenant, listing, open home, bond, rent, arrears, breach type, inspection, condition report). Addresses use Australian format (suburb, state, postcode).
- **Prefill:** `MOCK_FLOW_PREFILL` and flow config drive one-click demo prefill (e.g. `property_id` `prop_001`, `tenancy_id` `tenancy_001`).

## Terminology

The UI uses **Ray White and Australian real estate** terms consistently:

- **Flows and concepts:** Vendor Report, Weekly Vendor Report, Rental Arrears, Arrears & Breach, Open Home Feedback, Property Details, Ledger Summary, Breach Notice, Document OCR, Expiry Extraction.
- **Labels:** Property ID, Tenancy ID, Vendor, Tenant, Listing, Open home, Bond, Rent, Arrears, Breach type (rent arrears / lease violation / property damage).
- **Address:** Suburb, state, postcode; inspection, condition report where relevant.

## Flows and MCP

Flows map to MCP tools or workflows as defined in the **Flow → MCP mapping** table in `docs/schemas.md`. The console flow list is driven by `frontend/src/data/flowConfig.ts` (id, name, description, workflow/tool id, input fields). Execution calls `executeTool` or `executeWorkflow` with the appropriate endpoint id and validated payload.

## Validation

- **Library:** Zod (`frontend/src/lib/validation.ts`).
- **Source of truth:** Validation rules in `docs/schemas.md` (ID format, URL format, breach type, role, confidence bounds).
- **Behaviour:** On submit, the frontend runs the validators; if invalid, it shows field errors and **does not** call MCP. On success, it calls `executeTool` or `executeWorkflow` with the validated payload.

## MCP integration

- **Base URL:** Dev proxy `/api` to MCP (see `frontend/vite.config.ts`). Production: env-driven `VITE_API_BASE` (default `/api`).
- **Auth and headers:** `Authorization: Bearer` plus `X-User-ID`, `X-Tenant-ID`, `X-Auth-Context`, `X-Role`. Token from env: `VITE_MCP_AUTH_TOKEN`. For Tier C (e.g. breach notice), `X-HITL-Token` is sent when provided.
- **Status:** Footer (and header) show connection status using `checkHealth` / `checkReady` and the design-system status indicator (accent dot when ready, label + version).

See `docs/configuration.md` for API and environment details.

## Development

- **Run:** From `frontend/`: `bun run dev` or `npm run dev`.
- **Proxy:** Vite proxies `/api` to the MCP server; ensure the backend is running for full behaviour.
- **Env:** Set `VITE_MCP_AUTH_TOKEN` (and optionally `VITE_API_BASE`) for auth and API base.
