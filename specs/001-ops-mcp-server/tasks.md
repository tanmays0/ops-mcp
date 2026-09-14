# Tasks: OpsMCP Server (Week 1 MVP = US1)

**Input**: Design documents from `/specs/001-ops-mcp-server/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required for guardrails (constitution II).

## Phase 1: Setup

- [x] T001 Create `src/ops_mcp/` package layout with security/, tools/, adapters/
- [x] T002 Initialize uv project (Python 3.12), deps: fastmcp, pydantic-settings, httpx, pytest
- [x] T003 [P] Add `.python-version`, `.env.example`, domain tool stubs, fixtures/fs_sandbox

## Phase 2: Foundational

- [x] T004 Implement `src/ops_mcp/config.py` (OPS_MCP_FS_ROOTS, max read, log level)
- [x] T005 [P] Implement `src/ops_mcp/security/secrets.py` redaction
- [x] T006 [P] Implement `src/ops_mcp/logging_setup.py` structured JSON logging with redaction
- [x] T007 Write failing path-sandbox tests in `tests/security/test_path_sandbox.py`
- [x] T008 Implement `src/ops_mcp/security/path_sandbox.py` until tests pass
- [x] T009 FastMCP stdio app in `src/ops_mcp/server.py` + `__main__.py` with lifespan

**Checkpoint**: Foundation ready for US1

## Phase 3: User Story 1 — Sandboxed FS (P1) 🎯 MVP

**Goal**: `fs_search` + `fs_read_file` fail-closed under allowlisted roots

**Independent Test**: pytest + Cursor mcp.json calling both tools

### Tests first

- [x] T010 [P] [US1] Failing/asserting FS tool tests in `tests/tools/test_fs_tools.py`
- [x] T011 [P] [US1] Redaction assertion for fake `ghp_` token

### Implementation

- [x] T012 [US1] Implement `fs_search` / `fs_read_file` in `src/ops_mcp/tools/fs.py`
- [x] T013 [US1] Register FS tools on FastMCP server; structured tool-call logs
- [x] T014 [US1] Wire `.cursor/mcp.json` + README threat-model stub + quickstart validation

**Checkpoint**: Week 1 done when pytest green and Cursor lists FS tools

## Phase 4+: Deferred (not Week 1)

- [x] US2/US3 GitHub tools + outbound rate limit (Week 2)
- [x] US4/US5 Postgres SELECT-only + EXPLAIN + deploy_status + Compose seed (Week 3)
- [x] Week 4: Dockerfile, CI workflow, secret hygiene (.env / mcp.json.example)
- Strix skipped (paid credits required) — not part of this ship

## Dependencies

Setup → Foundational → US1. Later stories blocked on US1 demo quality only by schedule, not code.

## Implementation Strategy

Complete T001–T014 as Week 1 MVP. Stop and validate before GitHub/Postgres work.
