# Feature Specification: OpsMCP Server

**Feature Branch**: `001-ops-mcp-server`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Build OpsMCP: an MCP server that lets an AI coding agent safely operate GitHub, Postgres, deploys, and the local filesystem without holding raw credentials or unrestricted access."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sandboxed filesystem search and read (Priority: P1)

As a developer in Cursor, I ask the agent to search and read files in my
repo. The server confines every path to allowlisted roots and rejects
escapes (including symlinks and `..` traversal).

**Why this priority**: Establishes the fail-closed safety model and a
working Cursor stdio demo without external credentials.

**Independent Test**: Point Cursor at the stdio server with
`OPS_MCP_FS_ROOTS` set; call `fs_search` and `fs_read_file` on allowlisted
paths and verify escape attempts fail closed.

**Acceptance Scenarios**:

1. **Given** a search term, **When** the agent calls `fs_search`, **Then**
   it returns matches only from files under allowlisted roots; a search
   rooted outside the allowlist is rejected.
2. **Given** a file path, **When** the agent calls `fs_read_file`, **Then**
   it returns file contents up to a size limit if the path resolves inside
   the sandbox, and is rejected if the resolved path escapes it (including
   via symlinks or `..` traversal).

---

### User Story 2 - GitHub issue and PR inspection (Priority: P2)

As a developer, I ask the agent to list issues/PRs and summarize a PR
diff without dumping full file contents.

**Why this priority**: High-value read operations; requires GitHub token
but no write side effects.

**Independent Test**: With a GitHub token and a known repo, call
`github_list_issues` and `github_pr_diff_summary` and verify filtered
results and diff metadata.

**Acceptance Scenarios**:

1. **Given** a repo with open issues labeled "backend", **When** the agent
   calls `github_list_issues` with that filter, **Then** it returns exactly
   those issues with title, number, and state.
2. **Given** a PR number, **When** the agent calls `github_pr_diff_summary`,
   **Then** it returns the changed files and diff stats without dumping
   full file contents.

---

### User Story 3 - Safe GitHub issue creation (Priority: P3)

As a developer, I ask the agent to file an issue; writes default to dry-run
unless explicitly confirmed.

**Why this priority**: Demonstrates write safety without accidental creates.

**Independent Test**: Call `github_create_issue` without confirm /
`dry_run=false` and verify a dry-run payload; with confirm, verify create.

**Acceptance Scenarios**:

1. **Given** a natural-language request to create an issue, **When** the
   agent calls `github_create_issue` without an explicit confirm flag,
   **Then** the tool runs in dry-run mode and returns what it would have
   created instead of creating it.

---

### User Story 4 - Read-only Postgres query and explain (Priority: P4)

As a developer, I ask the agent to run SELECT queries and EXPLAIN plans
against Postgres; DDL/DML is rejected before execution.

**Why this priority**: High risk surface; depends on SQL allowlist.

**Independent Test**: Execute SELECT successfully; assert DROP/DELETE fail
before touching the DB; EXPLAIN returns a plan without executing the query.

**Acceptance Scenarios**:

1. **Given** a SELECT query, **When** the agent calls
   `postgres_query_readonly`, **Then** it executes as a parameterized query
   and returns rows; given any non-SELECT statement, the tool rejects it
   before touching the database.
2. **Given** a SELECT query, **When** the agent calls `postgres_explain`,
   **Then** it returns the query plan without executing the query.

---

### User Story 5 - Deploy / CI status (Priority: P5)

As a developer, I ask the agent for the latest GitHub Actions workflow run
or deployment state on the default branch.

**Why this priority**: Completes the four-domain story; reuses GitHub auth.

**Independent Test**: Call `deploy_status` for a repo with recent CI and
verify latest run/state fields.

**Acceptance Scenarios**:

1. **Given** a repo with a recent CI run, **When** the agent calls
   `deploy_status`, **Then** it returns the latest workflow run or
   deployment state for the default branch.

---

### Edge Cases

- Path contains `..` segments or a symlink that resolves outside allowlisted roots → reject (fail closed).
- Empty `OPS_MCP_FS_ROOTS` or missing root directory → reject at startup or call time (fail closed).
- File larger than max read bytes → return truncated content with `truncated=true`.
- Binary files during search → skipped (null-byte heuristic).
- GitHub/Postgres credentials missing when those tools are invoked → clear configuration error without leaking secrets.
- Non-SELECT SQL (DROP, DELETE, UPDATE, INSERT, WITH…mutating, multiple statements) → rejected before DB touch.
- GitHub create without confirm → dry-run only.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-1**: The server exposes exactly 8 tools, each with a typed schema:
  `github_list_issues`, `github_create_issue`, `github_pr_diff_summary`,
  `postgres_query_readonly`, `postgres_explain`, `deploy_status`,
  `fs_search`, `fs_read_file`.
- **FR-2**: All filesystem access is confined to explicitly allowlisted root
  directories, resolved and checked after symlink resolution.
- **FR-3**: All Postgres access is read-only; DDL/DML is rejected before
  execution, not merely discouraged.
- **FR-4**: GitHub write operations default to a dry-run response unless the
  caller explicitly sets confirm / `dry_run=false`.
- **FR-5**: Every tool call is logged as structured JSON with latency and
  outcome; no credential values appear in any log line or tool response.
- **FR-6**: The server runs over stdio for local Cursor use and is packaged
  as a Docker image for remote/demo use.

### Key Entities

- **Allowlisted Root**: Absolute directory the FS tools may access.
- **Tool Call Log**: Structured record with tool name, latency, ok/err.
- **GitHub Issue / PR Summary**: Title, number, state, labels; PR file
  stats without full contents.
- **Query Plan / Row Set**: Explain output or SELECT result rows.
- **Deploy State**: Latest workflow run or deployment status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Path-escape and symlink-escape attempts against FS tools fail
  closed in automated tests (100% of documented attack cases).
- **SC-002**: Non-SELECT SQL statements are rejected before DB execution in
  automated tests.
- **SC-003**: `github_create_issue` without confirm never creates a remote
  issue (dry-run by default).
- **SC-004**: A developer can wire the stdio server into Cursor via
  `.cursor/mcp.json` and successfully call `fs_search` / `fs_read_file`.
- **SC-005**: No raw token values appear in tool responses or captured logs
  in secret-redaction tests.

## Assumptions

- Week 1 delivery focuses on P1 (FS tools + stdio server + Cursor wiring);
  P2–P5 land in later weeks with domain stubs reserved in the package layout.
- Credentials (GitHub token, Postgres DSN) are supplied via environment
  variables on the developer's machine or container.
- Out of scope for this feature: OAuth UI, multi-tenant SaaS dashboard,
  write-heavy database tools, Kubernetes controllers, marketplace publishing.
