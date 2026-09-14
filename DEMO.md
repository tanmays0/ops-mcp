# Verification flows

Prerequisite: `docker compose up -d`, `.env` configured, MCP server process running
(`uv run python -m ops_mcp` or client-launched stdio).

## Flow A — Filesystem

| Step | Tool | Input | Expected output |
|------|------|-------|-----------------|
| 1 | `fs_search` | `query=hello sandbox` | Hits under allowlisted roots only |
| 2 | `fs_read_file` | path from a hit | File content, `encoding=utf-8` |
| 3 | `fs_read_file` | path outside allowlist | Error: outside allowlist |

## Flow B — Postgres

| Step | Tool | Input | Expected output |
|------|------|-------|-----------------|
| 1 | `postgres_query_readonly` | `SELECT email FROM users ORDER BY id` | Seeded emails |
| 2 | `postgres_query_readonly` | `SELECT COUNT(*) AS n FROM orders WHERE status = %s` params `["paid"]` | Count row |
| 3 | `postgres_explain` | same SELECT as step 2 | Plan text; table row counts unchanged |
| 4 | `postgres_query_readonly` | `DROP TABLE users` | Rejected before DB connect |

## Flow C — GitHub and deploy

| Step | Tool | Input | Expected output |
|------|------|-------|-----------------|
| 1 | `github_list_issues` | `owner`, `repo`, `state=open` | Issue/PR summaries |
| 2 | `github_pr_diff_summary` | `owner`, `repo`, `pull_number` | File stats; no `patch` fields |
| 3 | `deploy_status` | `owner`, `repo`, `branch=main` | Latest run `status` / `conclusion` or `run=null` |
| 4 | `github_create_issue` | title/body with default dry-run | `{dry_run: true, would_create: ...}` ; no remote create |

## Automated proof

```bash
uv run pytest
```

CI on `main`: GitHub Actions workflow `ci` (Postgres service + pytest).
