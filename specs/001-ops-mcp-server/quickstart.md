# Quickstart: OpsMCP (Week 1)

## Install

```bash
cd /Users/shind/ops-mcp
uv sync
```

## Run stdio server

```bash
export OPS_MCP_FS_ROOTS=/Users/shind/ops-mcp/fixtures/fs_sandbox
uv run python -m ops_mcp
```

## Cursor

Use `.cursor/mcp.json` (committed example). Reload MCP servers in Cursor,
confirm `fs_search` and `fs_read_file` appear, then ask the agent to search
for `hello sandbox` and read `safe/readme.txt`.

## Tests

```bash
uv run pytest
```
