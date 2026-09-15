# OpsMCP

MCP (Model Context Protocol) server that exposes eight typed tools so an AI
agent can operate GitHub, Postgres, deploy status, and a sandboxed local
filesystem. Credentials stay in the server process; tool inputs are treated as
untrusted.

**Live:** https://tanmays0.github.io/ops-mcp/  
**GitHub:** https://github.com/tanmays0/ops-mcp


| Artifact | Location |
|----------|----------|
| MCP server (stdio) | `uv run python -m ops_mcp` |
| Eight tools | registered in `src/ops_mcp/server.py` |
| Companion UI | `site/` → GitHub Pages (catalog, setup, simulated playground) |
| Seeded demo database | `docker compose up -d` → Postgres `users` / `orders` / `products` |
| Automated tests | `uv run pytest` (path sandbox, SQL guard, GitHub mocks, Postgres) |
| CI | GitHub Actions workflow `.github/workflows/ci.yml` |
| Pages deploy | `.github/workflows/pages.yml` |
| Container image | `Dockerfile` |
| Agent wiring example | `.cursor/mcp.json.example` |

## Architecture

```text
Agent (stdio) → FastMCP server
                  ├── tools/       domain tools
                  ├── security/    path sandbox, SQL allowlist, redaction, rate limit
                  ├── adapters/    GitHub HTTP, Postgres
                  └── config.py    Pydantic Settings (env / .env)
```

## Tools

| Tool | System | Behavior |
|------|--------|----------|
| `github_list_issues` | GitHub API | List issues/PRs by repo, state, labels |
| `github_create_issue` | GitHub API | Create issue; default `dry_run=true` |
| `github_pr_diff_summary` | GitHub API | PR file list and diff stats (no patches) |
| `postgres_query_readonly` | Postgres | Parameterized SELECT only |
| `postgres_explain` | Postgres | `EXPLAIN (FORMAT TEXT)` only (no `ANALYZE`) |
| `deploy_status` | GitHub Actions | Latest workflow run for a branch |
| `fs_search` | Local FS | Literal search under allowlisted roots |
| `fs_read_file` | Local FS | Read file with sandbox and size limit |

## Safety

| Control | Implementation |
|---------|----------------|
| Filesystem | Resolve-then-compare allowlist after symlink resolution |
| SQL | sqlglot AST: single SELECT / WITH…SELECT; DDL/DML/multi-statement rejected before connect |
| GitHub writes | `dry_run=true` unless explicitly disabled |
| Secrets | `SecretStr` for token and DSN; log redaction; never returned in tool payloads |
| Outbound HTTP | Token-bucket rate limit |

## Stack

Python 3.12 · FastMCP · httpx · psycopg · sqlglot · Pydantic Settings · pytest · Docker

## Run

```bash
git clone https://github.com/tanmays0/ops-mcp.git
cd ops-mcp
uv sync
docker compose up -d
cp .env.example .env
uv run pytest
uv run python -m ops_mcp
```

Populate `.env` from `.env.example` (`OPS_MCP_FS_ROOTS`, `OPS_MCP_DATABASE_URL`, `OPS_MCP_GITHUB_TOKEN`). MCP client config: copy `.cursor/mcp.json.example` to `.cursor/mcp.json` with absolute paths. Secrets load from `.env` only (`.env` and `.cursor/mcp.json` are gitignored).

## Configuration

| Variable | Purpose |
|----------|---------|
| `OPS_MCP_FS_ROOTS` | Colon-separated allowlisted directories |
| `OPS_MCP_FS_MAX_READ_BYTES` | Max bytes for `fs_read_file` |
| `OPS_MCP_DATABASE_URL` | Postgres DSN |
| `OPS_MCP_GITHUB_TOKEN` | GitHub fine-grained or classic PAT |
| `OPS_MCP_HTTP_RATE_PER_SECOND` | Outbound API rate |
| `OPS_MCP_LOG_LEVEL` | Log level |

## Verification flows

Documented end-to-end flows: [DEMO.md](DEMO.md).

## Spec

Project principles: [`.specify/memory/constitution.md`](.specify/memory/constitution.md)  
Requirements: [`specs/001-ops-mcp-server/spec.md`](specs/001-ops-mcp-server/spec.md)
