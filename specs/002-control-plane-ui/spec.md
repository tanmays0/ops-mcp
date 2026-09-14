# Feature Specification: OpsMCP Control Plane UI

**Feature Branch**: `002-control-plane-ui`

**Created**: 2026-09-15

**Status**: Draft → Clarified (GitHub Pages)

**Input**: User description: "ops-mcp can have a UI as a deployed companion control plane (v1.1 retrofit). Recruiters can open: tool catalog (8 tools + schemas), health / recent tool-call logs, Try tool playground (safe dry-run), setup snippet for Cursor (.cursor/mcp.json). MCP stays Cursor ↔ stdio ↔ tools. UI is docs + demo + observability. Start with GitHub Pages (free); Vercel/Netlify later optional."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recruiter opens the public control plane (Priority: P1)

A recruiter or hiring manager opens a public URL for OpsMCP and immediately understands what the project is: an MCP tool server with eight capabilities. They can browse a catalog of the eight tools with human-readable descriptions and input/output shapes, without installing anything or running Cursor.

**Why this priority**: The primary motivation for the UI is portfolio visibility. If only this story ships, the feature still delivers recruiter value.

**Independent Test**: Open the deployed homepage on a phone or laptop with no local setup; confirm all eight tools appear with schemas and a clear statement that the MCP server remains a separate local stdio process.

**Acceptance Scenarios**:

1. **Given** a visitor with only a browser, **When** they open the control plane URL, **Then** they see the product name, one-line purpose, and a catalog of exactly the eight OpsMCP tools.
2. **Given** the tool catalog, **When** they select any tool, **Then** they see its purpose, inputs, outputs, and safety notes (e.g. dry-run default, SELECT-only, path sandbox) without needing source code.
3. **Given** the homepage, **When** they look for architecture context, **Then** they see that AI agents talk to OpsMCP over MCP/stdio and that this UI does not replace that path.

---

### User Story 2 - Cursor setup without reading the whole README (Priority: P1)

A visitor (recruiter, interviewer, or the builder demoing) wants the exact Cursor wiring snippet so they understand how a host launches OpsMCP locally.

**Why this priority**: Setup clarity is part of “demo + docs” and unblocks live MCP demos after the catalog.

**Independent Test**: From the UI alone, copy a Cursor MCP config example that matches the project’s documented example pattern (absolute command paths, env from `.env`, no committed secrets).

**Acceptance Scenarios**:

1. **Given** the setup section, **When** a visitor views it, **Then** they see a complete example MCP client config for Cursor consistent with the repo’s example file.
2. **Given** the setup section, **When** secrets are mentioned, **Then** the UI states that tokens and database URLs stay in local environment files and must never be pasted into the public UI.
3. **Given** the setup section, **When** a visitor follows the high-level steps, **Then** they understand: clone → configure env → run server → point Cursor at it (UI does not run the MCP server in the browser).

---

### User Story 3 - Safe “Try tool” playground (Priority: P2)

A visitor wants to click through a dry-run / safe simulation of tool calls to feel how OpsMCP behaves (especially write defaults and rejection of unsafe SQL/paths), without gaining unrestricted power over the builder’s real systems from the public internet.

**Why this priority**: High demo value, but secondary to a solid catalog + setup because public playgrounds have a larger safety blast radius.

**Independent Test**: From the UI, invoke at least one read-shaped demo and one write-shaped dry-run demo and see structured results; attempt an explicitly unsafe example and see a refusal explained in plain language.

**Acceptance Scenarios**:

1. **Given** the playground, **When** a visitor runs a GitHub-create-issue style demo, **Then** the result is clearly marked dry-run / non-mutating and is **simulated in the browser** (no remote GitHub write).
2. **Given** the playground, **When** a visitor submits an unsafe SQL or path example provided by the UI, **Then** they see a fail-closed refusal with a short explanation aligned with OpsMCP’s security model (client-side simulation of the same policy).
3. **Given** the playground, **When** a visitor might expect live credentials, **Then** the UI states that v1.1 playground is **simulated only** — no tokens or database URLs are accepted or stored.

---

### User Story 4 - Health and sample observability (Priority: P3)

A visitor wants to see what OpsMCP’s structured tool-call observability looks like, using **sample/demo events** bundled with the static site (not a live feed from a private laptop MCP process).

**Why this priority**: Supports the observability pitch on a free static host; live log shipping is deferred.

**Independent Test**: Open health/observability; confirm sample events render without secret material; confirm messaging that these are illustrative samples.

**Acceptance Scenarios**:

1. **Given** the health view, **When** the static site loads, **Then** visitors see companion status as available (static asset reachable) plus a clear note that this is not the local MCP process health.
2. **Given** sample tool-call events are shown, **When** any event is displayed, **Then** fields are limited to safe operational metadata (tool name, ok/err, latency, redacted error class) — never tokens, DSNs, or raw file bodies.
3. **Given** the observability section, **When** a visitor reads the caption, **Then** they understand events are **demo samples** illustrating `log_tool_call`-style records, not live production traffic.

---

### Edge Cases

- Visitor opens the UI while the local MCP server is not running: UI remains fully useful (static catalog/setup/simulated playground/sample logs).
- Visitor pastes a secret into a playground field: UI MUST refuse to persist or echo secrets; warn that secrets belong only in local env; strip/redact obvious token-shaped input in the display.
- Extremely large simulated output: UI truncates display and labels truncation.
- Mobile viewport: catalog and setup remain readable; playground usable for core demos.
- Public spam: N/A for simulated static playground (no backend to abuse); still no secret collection.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a publicly reachable companion control plane that does not replace the local MCP stdio server.
- **FR-002**: System MUST present a catalog of all eight OpsMCP tools with purpose, inputs, outputs, and safety notes derived from the product’s actual tool contracts.
- **FR-003**: System MUST include a Cursor MCP setup section with a copyable config example and explicit secret-handling guidance.
- **FR-004**: System MUST state architecture clearly: Agent/Cursor → MCP stdio → OpsMCP tools → security → adapters → systems; UI is docs/demo/observability only.
- **FR-005**: System MUST offer a “Try tool” playground limited to **browser-side simulations** (dry-run create-issue, SELECT allow, DROP/path refusal demos at minimum).
- **FR-006**: Playground MUST NOT accept or store operator GitHub tokens or database URLs from visitors in v1.1.
- **FR-007**: System MUST expose a health/observability view for the companion site with **bundled sample events** (not live MCP logs).
- **FR-008**: When tool-call style events are shown, System MUST omit secrets and sensitive payloads.
- **FR-009**: System MUST be deployable via **GitHub Pages** to a public URL suitable for resume/portfolio and the GitHub repo Website field.
- **FR-010**: Primary deploy host for v1.1 MUST be **GitHub Pages**. Vercel/Netlify remain optional future ports and MUST NOT block v1.1.
- **FR-011**: The existing eight MCP tools and their fail-closed guards remain authoritative; the UI MUST NOT weaken dry-run defaults, SQL allowlisting, or path sandbox semantics in documentation or demos.
- **FR-012**: System MUST remain single-operator / portfolio-scoped — not a multi-tenant OAuth product.
- **FR-013**: Site MUST be fully static for v1.1 (no server-side secrets, no visitor-authenticated API).

### Key Entities

- **Tool Catalog Entry**: One of the eight tools; name, summary, parameters, result shape, safety notes.
- **Setup Snippet**: Example host configuration for launching OpsMCP locally; placeholders only.
- **Playground Invocation**: Browser-side demo with tool name, sanitized inputs, structured simulated result or refusal.
- **Health Snapshot**: Static companion “available” status plus caption distinguishing site vs MCP process.
- **Safe Event (sample)**: Illustrative observability record with tool name, ok/err, latency, redacted error — no secrets/payloads.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A first-time visitor can identify all eight tools and the MCP vs UI boundary within 60 seconds on the homepage.
- **SC-002**: A visitor can copy a Cursor setup example from the UI in under 2 minutes without opening the GitHub README (README may still exist as source of truth).
- **SC-003**: At least three playground demonstrations work end-to-end offline in the browser: one list/read-shaped simulation, one dry-run write-shaped, one deliberate security refusal.
- **SC-004**: GitHub Pages URL loads on desktop and a common mobile browser without local installs.
- **SC-005**: Spot-check of displayed sample events finds zero tokens, DSNs, or raw secret-looking values.
- **SC-006**: The GitHub repository About “Website” field can point at the Pages URL.

## Assumptions

- OpsMCP v1 MCP server remains the core product; this is a companion retrofit labeled v1.1.
- UI audience: recruiters, interviewers, and demos — not a multi-team ops console.
- Catalog content stays consistent with real tool contracts (synced manually or from a checked-in JSON for the static site).
- Sample logs are illustrative; live log bridging is out of scope for Pages v1.1.
- Constitution allows a static companion control plane that is not a multi-tenant OAuth dashboard.
- Future Vercel/Netlify deploy is a hosting port of the same static assets, not a redesign gate.
- Interview study guide markdown is personal study material and not part of this feature’s public surface.
