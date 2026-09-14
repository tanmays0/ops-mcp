# Data Model: Control Plane UI (static)

No database. Entities are JSON documents shipped with the site.

## ToolCatalogEntry

| Field | Type | Notes |
|-------|------|-------|
| `name` | string | Exact MCP tool name |
| `system` | string | github / postgres / deploy / filesystem |
| `summary` | string | One-line purpose |
| `inputs` | object[] | name, type, required, default, description |
| `outputs` | string | Human description of return shape |
| `safety` | string[] | Dry-run, SELECT-only, sandbox, etc. |

Source of truth: OpsMCP `server.py` docstrings + tool contracts under `specs/001-ops-mcp-server/contracts/`.

## SetupSnippet

| Field | Type | Notes |
|-------|------|-------|
| `label` | string | e.g. Cursor mcp.json |
| `body` | string | Example JSON with `/ABS/PATH/TO/ops-mcp` placeholders |
| `warnings` | string[] | Secrets in `.env` only |

## PlaygroundScenario

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | Stable id |
| `tool` | string | Tool name |
| `title` | string | Demo title |
| `inputs` | object | Pre-filled sanitized inputs |
| `kind` | enum | `success_sim` \| `dry_run` \| `refusal` |
| `result` | object | Simulated payload shown to visitor |

## SafeEvent (sample)

| Field | Type | Notes |
|-------|------|-------|
| `ts` | string | ISO timestamp (sample) |
| `tool` | string | Tool name |
| `ok` | boolean | |
| `latency_ms` | number | |
| `error` | string \| null | Redacted class only |

## Relationships

- Catalog entries (8) are independent of playground scenarios (N≥3).
- Sample events reference tool names that exist in the catalog.
