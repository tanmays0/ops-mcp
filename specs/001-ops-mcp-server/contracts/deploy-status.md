# Contract: deploy_status

**Input**: `owner`, `repo`, `branch` (default `main`)
**Output**: `{branch, run: null | {id, name, status, conclusion, html_url, ...}}`
**Transport**: existing GitHub adapter + rate limiter — `GET /repos/{o}/{r}/actions/runs`
**Safety**: read-only; no write surface; token never returned
