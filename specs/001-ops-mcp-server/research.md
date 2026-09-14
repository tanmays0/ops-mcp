# Research: OpsMCP Server

## Decision: Standalone FastMCP package

- **Choice**: `from fastmcp import FastMCP` (PyPI `fastmcp`), stdio default
- **Rationale**: Matches portfolio brief; ergonomic tool decorators; Cursor
  launches stdio subprocesses cleanly
- **Alternatives**: Official `mcp` SDK 2.x `MCPServer` — more canonical but
  more boilerplate; deferred unless FastMCP blocks a requirement

## Decision: Resolve-then-compare path sandbox

- **Choice**: `Path.resolve()` then membership check against allowlisted roots
- **Rationale**: String-prefix checks on unresolved paths are bypassable via
  `..` and symlinks
- **Alternatives**: chroot / OS sandbox — overkill for local MCP Week 1

## Decision: Pure-Python literal substring search

- **Choice**: Walk allowlisted trees; case-sensitive substring match
- **Rationale**: No hard dependency on system `rg`; predictable agent behavior
- **Alternatives**: Shell out to ripgrep — faster, less portable

## Decision: uv + src layout

- **Choice**: `uv` project with `src/ops_mcp`, Python 3.12 pin
- **Rationale**: Fast lockfiles, reproducible Cursor `uv run` launches
