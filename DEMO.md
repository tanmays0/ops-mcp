# OpsMCP demo script (2–3 minutes)

Record this in Cursor with the `ops-mcp` MCP server connected and
`docker compose up -d` running. Use a public demo repo you own (example:
`tanmays0/admax-india`).

## Setup (before recording)

1. `.env` has `OPS_MCP_GITHUB_TOKEN` and `OPS_MCP_DATABASE_URL`
2. Cursor shows all 8 tools under **ops-mcp**
3. Postgres healthy: `docker compose ps`

## Script (say / type these)

1. **GitHub read**  
   “Using ops-mcp, list open issues/PRs in `OWNER/REPO`.”

2. **Filesystem**  
   “Search the sandbox for `hello sandbox` and read the matching file.”

3. **Postgres**  
   “How many paid orders are in the demo DB? Use `postgres_query_readonly`.”  
   Optional: “`EXPLAIN` that query without executing it.”

4. **Deploy status**  
   “Is `main`’s latest GitHub Actions run green for `OWNER/REPO`?”

5. **Safe write**  
   “Draft a GitHub issue summarizing what you found — dry-run only.”  
   (Confirm the tool returns `dry_run: true` and does **not** create anything.)

## What interviewers should notice

- Credentials never appear in tool output
- Path/SQL attacks fail closed (optional live: ask to `DROP TABLE` or read `/etc/passwd`)
- Writes default to dry-run
- One agent session chains four real systems through typed tools

## Resume one-liner

Built a production-style MCP server (Python/FastMCP) exposing 8 typed tools for
GitHub, Postgres read models, deploy status, and secure file search — with auth,
structured errors, Docker, and Cursor agent demos.
