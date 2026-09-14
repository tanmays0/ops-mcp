# Contract: Playground Simulation (client-side)

## Surface

UI “Try tool” panel; no HTTP backend. Scenarios loaded from `data/playground.json` (or embedded in `app.js`).

## Required scenarios (minimum)

| id | tool | kind | Visitor sees |
|----|------|------|----------------|
| `create-issue-dry` | `github_create_issue` | `dry_run` | `dry_run: true`, `would_create`, banner “simulated” |
| `select-ok` | `postgres_query_readonly` | `success_sim` | Fake columns/rows for a SELECT |
| `drop-refuse` | `postgres_query_readonly` | `refusal` | Error explaining DDL rejected before connect |
| `path-refuse` | `fs_read_file` | `refusal` | Error explaining path outside allowlist |

## Invariants

- Every result panel MUST include a visible **Simulated** label.
- Inputs that look like `ghp_` / `github_pat_` / `postgresql://` MUST be blocked or redacted before display.
- No network calls to GitHub or Postgres from the playground.
