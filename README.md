# OpsMCP

**Production-style MCP (Model Context Protocol) server** that lets Cursor and
other AI agents safely operate real systems: GitHub, Postgres, deploys, and a
sandboxed filesystem.



## Why this project

Most student “AI” demos call an LLM API. OpsMCP is **agent infrastructure**:
tools are discovered via schemas, credentials stay in the server process, and
safety gates (path sandbox, SELECT-only SQL, dry-run writes) fail closed under
test.

## Architecture

```text
Cursor / Agent ──stdio──▶ FastMCP (ops-mcp)
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         tools/*         security/*      adapters/*
      (8 typed tools)  (sandbox, SQL,   (GitHub HTTP,
                        redaction,       Postgres)
                        rate limit)
```

## The 8 tools

| Tool | Domain | Safety |
|------|--------|--------|
| `github_list_issues` | GitHub | Read |
| `github_create_issue` | GitHub | **`dry_run=true` by default** |
| `github_pr_diff_summary` | GitHub | Stats only (no patches) |
| `postgres_query_readonly` | Postgres | SELECT-only AST gate before connect |
| `postgres_explain` | Postgres | `EXPLAIN` only (no `ANALYZE`) |
| `deploy_status` | GitHub Actions | Read-only latest workflow run |
| `fs_search` | Filesystem | Allowlisted roots |
| `fs_read_file` | Filesystem | Sandbox + size cap |

## Quick start

```bash
git clone https://github.com/tanmays0/ops-mcp.git
cd ops-mcp
uv sync
docker compose up -d
cp .env.example .env   # set OPS_MCP_GITHUB_TOKEN locally — never commit
uv run pytest
uv run python -m ops_mcp
```

### Cursor

1. Copy [`.cursor/mcp.json.example`](.cursor/mcp.json.example) → `.cursor/mcp.json` and fix paths.
2. Keep secrets in `.env` only (gitignored).
3. Reload MCP in Cursor Settings → confirm all 8 tools.

## Demo script (for Loom / interviews)

See **[DEMO.md](DEMO.md)** — 2–3 minutes, multi-tool agent flow.

## Threat model

| Trust boundary | Control |
|----------------|---------|
| Agent args | Untrusted; sandboxes and parsers fail closed |
| Secrets | `SecretStr` + redaction; never logged or returned |
| FS | Resolve-then-compare after symlink resolution |
| Postgres | sqlglot SELECT-only allowlist before any DB I/O |
| GitHub writes | Dry-run default; outbound token-bucket rate limit |

## Tests / CI

```bash
docker compose up -d
uv run pytest   # 47 tests: sandbox, SQL guard, GitHub mocks, live Postgres
```

GitHub Actions: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

## Docker

```bash
docker compose up -d          # seeded Postgres (users, orders, products)
docker build -t ops-mcp:local .
docker run --rm -i --env-file .env ops-mcp:local
```

## Stack

Python 3.12 · FastMCP · httpx · psycopg · sqlglot · Pydantic Settings · pytest · Docker

## Spec-driven development

[Constitution](.specify/memory/constitution.md) · [Feature spec](specs/001-ops-mcp-server/spec.md)
