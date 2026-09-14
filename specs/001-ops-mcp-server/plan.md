# Implementation Plan: OpsMCP Server

**Branch**: `001-ops-mcp-server` | **Date**: 2026-09-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-ops-mcp-server/spec.md`

## Summary

Build a typed FastMCP stdio server (`ops-mcp`) that exposes eight tools across
GitHub, Postgres, deploys, and sandboxed filesystem access. Week 1 delivers
the package scaffold, path sandbox, `fs_search` / `fs_read_file`, Cursor
wiring, and fail-closed tests. Later weeks fill GitHub, Postgres, deploy,
Docker, and rate limiting behind the same architecture.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: `fastmcp` (standalone), `pydantic-settings`, `httpx`
(declared early); later: `asyncpg`/`psycopg` for Postgres

**Storage**: Local filesystem (allowlisted); Postgres (later); no app DB

**Testing**: pytest (+ pytest-asyncio when async tools arrive)

**Target Platform**: Local developer machine (Cursor stdio); Docker later

**Project Type**: MCP tool server (CLI/package)

**Performance Goals**: Interactive agent latency; FS search bounded by
`max_results` and size limits

**Constraints**: Fail-closed path sandbox; no secrets in logs/responses;
GitHub writes dry-run by default; SELECT-only Postgres (later)

**Scale/Scope**: Exactly 8 tools in v1; Week 1 = FS + scaffold only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status |
|------|--------|
| I. Security-first / fail closed | PASS — path sandbox designed resolve-then-compare |
| II. Test-first guardrails | PASS — escape/symlink tests before/with implementation |
| III. Typed tool schemas | PASS — FastMCP typed tools + docstrings |
| IV. No secrets leave process | PASS — Settings + redaction logger |
| V. Structured observability | PASS — JSON tool-call logs |
| VI. Minimal v1 scope | PASS — 8 tools; Week 1 implements FS only |

Post-design: unchanged PASS.

## Project Structure

### Documentation (this feature)

```text
specs/001-ops-mcp-server/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
src/ops_mcp/
├── __init__.py
├── __main__.py
├── server.py
├── config.py
├── logging_setup.py
├── security/
│   ├── path_sandbox.py
│   └── secrets.py
├── tools/
│   ├── fs.py
│   ├── github.py      # stub Week 1
│   ├── postgres.py    # stub Week 1
│   └── deploy.py      # stub Week 1
└── adapters/          # clients Week 2+

tests/
├── conftest.py
├── security/
└── tools/

fixtures/fs_sandbox/
.cursor/mcp.json
.env.example
```

## Phase 0 / Phase 1

See [research.md](./research.md), [data-model.md](./data-model.md),
[contracts/](./contracts/), [quickstart.md](./quickstart.md).

## Complexity Tracking

No unjustified complexity. Pure-Python FS search (no `rg` dependency) chosen
for portable Week 1 demos.
