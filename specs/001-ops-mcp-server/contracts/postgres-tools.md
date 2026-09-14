# Contract: Postgres Tools

## postgres_query_readonly

**Input**: `sql` (SELECT), `params` (optional sequence), `max_rows` (optional)
**Output**: `{columns, rows, row_count, truncated}`
**Safety**: `assert_select_only` before connect; parameterized only; DSN is SecretStr

## postgres_explain

**Input**: `sql` (SELECT), `params` (optional)
**Output**: `{plan: str}` from `EXPLAIN (FORMAT TEXT)` — never `ANALYZE`
**Safety**: same SELECT-only gate; row counts of target tables must not change
