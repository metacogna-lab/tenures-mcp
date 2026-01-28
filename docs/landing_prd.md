# Tenures MCP Landing Page PRD

**Product:** Tenures MCP Server  
**Version:** Beta 0.1.0  
**Status:** Beta  
**Live Application:** https://tenures-mcp-production.up.railway.app  
**Last Updated:** 2026-01-28

---

## 1. Overview

A professional landing page for Tenures MCP - a Model Context Protocol server enabling AI agents to orchestrate real estate workflows for Ray White offices. The design follows the Metacogna design language with a darker, enterprise-focused palette suitable for B2B real estate technology.

---

## 2. Data Requirements

### 2.1 API Endpoints to Display

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/healthz` | GET | Liveness probe | Live |
| `/ready` | GET | Readiness with dependency checks | Live |
| `/v1/tools/{name}` | POST | Execute MCP tools | Beta |
| `/v1/workflows/{name}` | POST | Execute LangGraph workflows | Beta |
| `/v1/resources/{path}` | GET | Retrieve MCP resources | Beta |

### 2.2 Tools Feature Data

```json
{
  "tools": [
    {
      "id": "analyze_open_home_feedback",
      "name": "Feedback Analysis",
      "description": "Sentiment analysis and categorization of open home visitor feedback",
      "tier": "A",
      "status": "beta",
      "icon": "chart-bar"
    },
    {
      "id": "calculate_breach_status",
      "name": "Breach Detection",
      "description": "Arrears detection and breach risk classification for tenancies",
      "tier": "A",
      "status": "beta",
      "icon": "shield-exclamation"
    },
    {
      "id": "ocr_document",
      "name": "Document OCR",
      "description": "Text extraction from property management documents",
      "tier": "A",
      "status": "beta",
      "icon": "document-text"
    },
    {
      "id": "extract_expiry_date",
      "name": "Expiry Extraction",
      "description": "Parse expiry and compliance dates from extracted text",
      "tier": "A",
      "status": "beta",
      "icon": "calendar"
    },
    {
      "id": "generate_vendor_report",
      "name": "Vendor Reports",
      "description": "Weekly vendor report generation with market insights",
      "tier": "B",
      "status": "beta",
      "icon": "document-report"
    },
    {
      "id": "prepare_breach_notice",
      "name": "Breach Notice",
      "description": "Draft breach notice generation with HITL approval",
      "tier": "C",
      "status": "beta",
      "requires_hitl": true,
      "icon": "exclamation-triangle"
    }
  ]
}
```

### 2.3 Workflows Feature Data

```json
{
  "workflows": [
    {
      "id": "weekly_vendor_report",
      "name": "Weekly Vendor Report Flow",
      "description": "Property details → Feedback analysis → Market trends → Report generation",
      "steps": 4,
      "status": "beta"
    },
    {
      "id": "arrears_detection",
      "name": "Arrears Detection Flow",
      "description": "Ledger fetch → Breach calculation → Risk classification → Action recommendation",
      "steps": 4,
      "status": "beta"
    },
    {
      "id": "compliance_audit",
      "name": "Compliance Audit Flow",
      "description": "Document fetch → OCR processing → Date extraction → Compliance validation",
      "steps": 4,
      "status": "beta"
    }
  ]
}
```

### 2.4 Resources Feature Data

```json
{
  "resources": [
    {
      "uri": "vault://properties/{id}/details",
      "name": "Property Details",
      "description": "Property listing summary from VaultRE"
    },
    {
      "uri": "vault://properties/{id}/feedback",
      "name": "Property Feedback",
      "description": "Open home feedback entries"
    },
    {
      "uri": "ailo://ledgers/{tenancy_id}/summary",
      "name": "Ledger Summary",
      "description": "Tenancy ledger balance and arrears status"
    },
    {
      "uri": "vault://properties/{id}/documents",
      "name": "Property Documents",
      "description": "Document URLs for contracts and certificates"
    }
  ]
}
```

### 2.5 Stats/Metrics Data

```json
{
  "stats": {
    "tools_available": 6,
    "workflows_available": 3,
    "resources_available": 4,
    "test_coverage": "41 tests passing",
    "uptime": "99.9%"
  }
}
```

---

## 3. Design System

### 3.1 Color Palette (Dark Professional)

```css
:root {
  /* Background layers */
  --bg-primary: #0a0a0f;      /* Deep navy black */
  --bg-secondary: #12121a;    /* Elevated surfaces */
  --bg-tertiary: #1a1a24;     /* Cards and containers */
  --bg-hover: #22222e;        /* Interactive hover states */
  
  /* Accent colors */
  --accent-primary: #6366f1;   /* Indigo - primary actions */
  --accent-secondary: #8b5cf6; /* Violet - secondary highlights */
  --accent-success: #10b981;   /* Emerald - success states */
  --accent-warning: #f59e0b;   /* Amber - warnings/beta badges */
  --accent-danger: #ef4444;    /* Red - critical/HITL required */
  
  /* Text hierarchy */
  --text-primary: #f8fafc;     /* Primary text - slate-50 */
  --text-secondary: #94a3b8;   /* Secondary text - slate-400 */
  --text-muted: #64748b;       /* Muted text - slate-500 */
  
  /* Borders */
  --border-subtle: #1e293b;    /* Subtle borders - slate-800 */
  --border-default: #334155;   /* Default borders - slate-700 */
  
  /* Gradients */
  --gradient-primary: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  --gradient-glow: radial-gradient(ellipse at center, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
}
```

### 3.2 Typography

```css
/* Font Stack */
--font-display: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Type Scale */
--text-xs: 0.75rem;    /* 12px - badges, labels */
--text-sm: 0.875rem;   /* 14px - body small */
--text-base: 1rem;     /* 16px - body */
--text-lg: 1.125rem;   /* 18px - lead text */
--text-xl: 1.25rem;    /* 20px - section headers */
--text-2xl: 1.5rem;    /* 24px - card titles */
--text-3xl: 1.875rem;  /* 30px - page sections */
--text-4xl: 2.25rem;   /* 36px - hero subtitle */
--text-5xl: 3rem;      /* 48px - hero title */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### 3.3 Component Styles

#### Beta Badge
```css
.badge-beta {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: #0a0a0f;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

#### Feature Card
```css
.feature-card {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: 0.75rem;
  padding: 1.5rem;
  transition: all 0.2s ease;
}

.feature-card:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
  transform: translateY(-2px);
}
```

#### Tool Tier Indicators
```css
.tier-a { border-left: 3px solid var(--accent-success); }
.tier-b { border-left: 3px solid var(--accent-primary); }
.tier-c { border-left: 3px solid var(--accent-danger); }
```

### 3.4 Layout Grid

```css
/* Container */
.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

/* Section Spacing */
.section {
  padding: 5rem 0;
}

/* Grid */
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }

@media (max-width: 768px) {
  .grid-3, .grid-2 { grid-template-columns: 1fr; }
}
```

---

## 4. Page Sections

### 4.1 Navigation
- Logo: Tenures MCP wordmark
- Links: Features, Workflows, API Docs, Status
- CTA: "View Documentation" button
- Beta badge next to logo

### 4.2 Hero Section
- Headline: "MCP Server for Real Estate Intelligence"
- Subheadline: "Policy-enforced AI workflows for Ray White property management. Tools, resources, and orchestration - all in one protocol."
- Primary CTA: "Explore API" → Documentation
- Secondary CTA: "View on GitHub" → Repository
- Beta indicator badge
- Background: Subtle gradient glow

### 4.3 Stats Bar
- 6 Tools Available (Beta)
- 3 Orchestrated Workflows (Beta)
- 4 Resource Endpoints (Beta)
- 41 Tests Passing

### 4.4 Tools Section
- Section title: "MCP Tools" with Beta badge
- Subtitle: "Versioned, schema-validated tools for property management automation"
- 3-column grid of tool cards
- Each card shows: Icon, Name, Description, Tier badge, Beta status

### 4.5 Workflows Section
- Section title: "LangGraph Workflows" with Beta badge
- Subtitle: "Deterministic multi-step orchestration for complex operations"
- Visual flow diagrams for each workflow
- Step indicators

### 4.6 Resources Section
- Section title: "Resource Endpoints" with Beta badge
- Subtitle: "URI-addressable data sources with PII redaction"
- Table or card list of resource URIs

### 4.7 Architecture Section
- Section title: "Built for Production"
- Key features:
  - RBAC Policy Gateway
  - HITL Confirmation for Mutations
  - SQLite Audit Logging
  - OpenTelemetry Tracing
- Architecture diagram (optional)

### 4.8 Integration Section
- Section title: "Connect Your Agents"
- Code examples for tool execution
- Authentication documentation link
- Railway deployment status

### 4.9 Footer
- Logo and tagline
- Links: Documentation, GitHub, Status, Support
- "Powered by Metacogna" attribution
- Copyright

---

## 5. Tasks

### 5.1 Data Layer
- [ ] **TASK-001: Create static data files**
  - [ ] Create `data/tools.json` with tool definitions
  - [ ] Create `data/workflows.json` with workflow definitions
  - [ ] Create `data/resources.json` with resource URIs
  - [ ] Create `data/stats.json` with metrics

- [ ] **TASK-002: API integration (optional)**
  - [ ] Fetch live health status from `/healthz`
  - [ ] Fetch readiness status from `/ready`
  - [ ] Display real-time connection status

### 5.2 Design Implementation
- [ ] **TASK-003: Setup project structure**
  - [ ] Initialize React + Vite + TypeScript project
  - [ ] Configure Tailwind CSS with custom theme
  - [ ] Add Inter and JetBrains Mono fonts
  - [ ] Setup CSS variables for design tokens

- [ ] **TASK-004: Build base components**
  - [ ] Create `<Badge>` component (beta, tier, status variants)
  - [ ] Create `<Card>` component with hover states
  - [ ] Create `<Button>` component (primary, secondary, ghost)
  - [ ] Create `<Container>` and `<Section>` layout components
  - [ ] Create `<CodeBlock>` component for API examples

- [ ] **TASK-005: Build navigation**
  - [ ] Create `<Navbar>` with logo, links, CTA
  - [ ] Add mobile responsive menu
  - [ ] Add Beta badge to branding

- [ ] **TASK-006: Build hero section**
  - [ ] Create hero layout with headline and CTAs
  - [ ] Add gradient background glow effect
  - [ ] Add animated Beta badge
  - [ ] Implement responsive typography

- [ ] **TASK-007: Build stats bar**
  - [ ] Create stats counter component
  - [ ] Display tool/workflow/resource counts
  - [ ] Add subtle animation on scroll

- [ ] **TASK-008: Build tools section**
  - [ ] Create tool card component with tier indicator
  - [ ] Implement 3-column responsive grid
  - [ ] Add Beta badges to each tool
  - [ ] Add HITL indicator for Tier C tools

- [ ] **TASK-009: Build workflows section**
  - [ ] Create workflow card with step visualization
  - [ ] Show flow: step1 → step2 → step3 → step4
  - [ ] Add Beta indicators
  - [ ] Implement responsive layout

- [ ] **TASK-010: Build resources section**
  - [ ] Create resource URI display component
  - [ ] Show protocol prefix styling (vault://, ailo://)
  - [ ] Add copy-to-clipboard functionality

- [ ] **TASK-011: Build architecture section**
  - [ ] Create feature highlight cards
  - [ ] Add icons for RBAC, HITL, Logging, Tracing
  - [ ] Optional: Add architecture diagram

- [ ] **TASK-012: Build integration section**
  - [ ] Create code example component
  - [ ] Show curl/Python examples for tool execution
  - [ ] Add "Try it" link to API docs
  - [ ] Display Railway deployment URL

- [ ] **TASK-013: Build footer**
  - [ ] Create footer layout with columns
  - [ ] Add Metacogna attribution
  - [ ] Add social/GitHub links
  - [ ] Add copyright notice

### 5.3 Deployment
- [ ] **TASK-014: Build and deploy**
  - [ ] Configure Vite build for production
  - [ ] Setup Railway or Vercel deployment
  - [ ] Configure custom domain (optional)
  - [ ] Add CI/CD for auto-deploy

- [ ] **TASK-015: SEO and meta**
  - [ ] Add meta tags for SEO
  - [ ] Add Open Graph tags for social sharing
  - [ ] Add favicon and app icons
  - [ ] Configure robots.txt

---

## 6. Acceptance Criteria

1. **Visual Design**
   - [ ] Matches dark professional color palette
   - [ ] All text is readable (contrast ratio ≥ 4.5:1)
   - [ ] Responsive on mobile, tablet, desktop
   - [ ] Beta badges visible on all feature sections

2. **Functionality**
   - [ ] All links work correctly
   - [ ] Code examples are copy-able
   - [ ] Navigation is smooth (anchor links)
   - [ ] Railway application link works

3. **Performance**
   - [ ] Lighthouse score ≥ 90
   - [ ] First Contentful Paint < 1.5s
   - [ ] No layout shift

4. **Accessibility**
   - [ ] Keyboard navigable
   - [ ] Screen reader compatible
   - [ ] Focus states visible

---

## 7. Links

| Resource | URL |
|----------|-----|
| **Live Application** | https://tenures-mcp-production.up.railway.app |
| **Health Check** | https://tenures-mcp-production.up.railway.app/healthz |
| **Readiness Check** | https://tenures-mcp-production.up.railway.app/ready |
| **GitHub Repository** | https://github.com/metacogna-lab/tenures-mcp |
| **API Documentation** | https://tenures-mcp-production.up.railway.app/docs |

---

## 8. Timeline

| Phase | Tasks | Status |
|-------|-------|--------|
| Data Layer | TASK-001, TASK-002 | Pending |
| Design Setup | TASK-003, TASK-004 | Pending |
| Core Sections | TASK-005 → TASK-013 | Pending |
| Deployment | TASK-014, TASK-015 | Pending |

---

## 9. Notes

- The application is currently deployed on Railway with placeholder URL
- All features are marked as "Beta" to indicate early access status
- HITL (Human-in-the-Loop) tools require special badge treatment (red/warning)
- Consider adding a "Request Access" CTA for enterprise inquiries
- Design inspired by Metacogna's Prompt Propel (prompt.metacogna.ai) with darker palette
