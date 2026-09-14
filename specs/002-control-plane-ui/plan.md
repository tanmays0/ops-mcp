# Implementation Plan: OpsMCP Control Plane UI (GitHub Pages)

**Branch**: `002-control-plane-ui` | **Date**: 2026-09-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-control-plane-ui/spec.md`

## Summary

Ship a **static companion control plane** on **GitHub Pages** so recruiters can open a public URL with: eight-tool catalog + schemas, Cursor setup snippet, simulated Try-tool playground, and sample observability events. The FastMCP stdio server remains the real product; the UI never holds secrets and never replaces MCP. Vercel/Netlify are deferred hosting ports of the same static assets.

## Technical Context

**Language/Version**: HTML5 + CSS + vanilla JavaScript (ES modules); optional tiny build step only if needed for Pages path prefix — prefer zero-build

**Primary Dependencies**: None required for runtime (no React/Next mandatory). Data: checked-in `tools.json` + `sample-events.json` derived from OpsMCP contracts

**Storage**: N/A (static files only)

**Testing**: Playwright or pytest+httpx against local static server optional; smoke checklist in quickstart; keep existing Python pytest suite green/unrelated

**Target Platform**: GitHub Pages (`https://tanmays0.github.io/ops-mcp/` project site)

**Project Type**: Static web companion co-located in monorepo (`site/`)

**Performance Goals**: First contentful paint usable on mobile within a few seconds on typical network; all demos work offline after first load

**Constraints**: No server secrets; no visitor auth; simulated playground only; base path must work under `/ops-mcp/` on Pages; accessible without local MCP

**Scale/Scope**: One public marketing/demo site; 4 sections (hero/catalog, setup, playground, observability); 8 tools

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status |
|-----------|--------|
| I Security-first tools | PASS — UI does not change MCP guards; demos mirror fail-closed semantics |
| II Test-first guardrails | PASS — core guards unchanged; UI adds presentation/smoke only |
| III Typed schemas | PASS — catalog surfaces the eight tool contracts |
| IV No secrets leave process | PASS — static site; no token/DSN fields; redaction messaging |
| V Structured observability | PASS — sample events illustrate `log_tool_call` shape |
| VI Minimal core + companion | PASS — constitution 1.1.0 allows static companion; not multi-tenant OAuth |

**Post-design**: Still PASS — static `site/` + Pages workflow; MCP package untouched except README Website pointer.

## Project Structure

### Documentation (this feature)

```text
specs/002-control-plane-ui/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── tool-catalog.md
│   └── playground-sim.md
├── checklists/requirements.md
└── tasks.md                 # created by /speckit-tasks
```

### Source Code (repository root)

```text
site/                       # GitHub Pages content root (or published from here)
├── index.html
├── styles.css
├── app.js
├── data/
│   ├── tools.json          # eight tools + schemas/safety notes
│   ├── setup.mcp.json.example
│   └── sample-events.json
└── assets/                 # optional logo/diagram

.github/workflows/
└── pages.yml               # build/deploy Pages from site/ on main (or this branch merge)

README.md                   # add Website / Pages link when live
```

**Structure Decision**: Co-locate a zero-build (or minimal) `site/` directory at repo root. Publish via GitHub Actions → GitHub Pages. Do **not** put UI under `src/ops_mcp/` (Python package stays MCP-only).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | — |
