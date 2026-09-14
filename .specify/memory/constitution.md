<!--
Sync Impact Report
- Version change: 1.0.0 → 1.1.0
- Modified principles: VI — allow static companion control plane (v1.1);
  still forbid multi-tenant OAuth dashboards and live public secret backends
- Added sections: none
- Removed sections: none
- Follow-up TODOs: none
-->
# OpsMCP Constitution

## Core Principles

### I. Security-First Tool Design (NON-NEGOTIABLE)
Every tool that touches a real system MUST fail closed on anything outside
its allowlist. Filesystem tools MUST reject path escapes (including `..`
traversal and symlink resolution outside allowlisted roots). Postgres tools
MUST reject anything that is not a parameterized SELECT. GitHub write tools
MUST default to `dry_run=true`. There are no exceptions to add scope faster.

### II. Test-First for Every Guardrail (NON-NEGOTIABLE)
Any security boundary (path sandbox, SQL allowlist, dry-run gate) MUST have
a failing test written before the guardrail is implemented, proving the
attack it blocks. Guardrails without attack-proving tests MUST NOT ship.

### III. Typed, Documented Tool Schemas
Every MCP tool MUST expose a typed input/output schema and a docstring an
agent can reason about without reading the implementation. Schemas are the
contract; undocumented tools are incomplete.

### IV. No Secrets Ever Leave the Process
Tokens and credentials MUST be read from environment variables via Pydantic
Settings. They MUST never be logged, never echoed in a tool response, and
never committed to the repository. Secret redaction MUST run on log
emission paths.

### V. Structured Observability
Every tool call MUST emit a structured JSON log with latency and ok/err
status. Print-debugging MUST NOT ship in the server.

### VI. Minimal Core + Optional Companion UI
Exactly the eight tools in the product specification ship in the MCP core.
OAuth multi-tenant dashboards, write-heavy database tools, and Kubernetes
controllers remain out of scope for the core server.

A **static companion control plane** (docs, tool catalog, Cursor setup,
simulated playground, sample observability) MAY ship as v1.1+ for portfolio
demo on a free static host (e.g. GitHub Pages). The companion MUST NOT
replace stdio MCP, MUST NOT collect visitor secrets, MUST NOT weaken core
guardrail semantics, and MUST NOT claim live multi-tenant operations.

## Quality Bar

- Runtime: Python 3.12 or newer
- Server framework: FastMCP (standalone `fastmcp` package) over stdio for
  local Cursor use; Docker packaging for remote/demo
- Tests: pytest MUST be green in CI on every commit
- A dependency and secret scan MUST pass before anything is called shipped

## Threat Model & Documentation

The README MUST document the threat model: the agent is untrusted input;
allowlists and dry-run defaults are the primary controls; residual risk
includes readable secrets inside allowlisted filesystem roots. The threat
model MUST stay current as tools are added.

## Governance

This constitution supersedes conflicting practices in plans, tasks, or ad
hoc implementation notes. Amendments require an updated Sync Impact Report,
a semantic version bump (MAJOR for principle removal/redefinition, MINOR
for new principles or material expansion, PATCH for clarifications), and
review against existing specs. All PRs and reviews MUST verify compliance
with principles I–VI and the quality bar. Complexity that weakens a
fail-closed guardrail is rejected by default.

**Version**: 1.1.0 | **Ratified**: 2026-09-11 | **Last Amended**: 2026-09-15
