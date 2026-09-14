# Contract: Filesystem Tools (Week 1)

## fs_search

**Input**
- `query: str` (required) — literal substring
- `root: str | null` — optional path that must resolve under allowlisted roots;
  if omitted, search all configured roots
- `max_results: int` — default 50

**Output**
- `hits: list[{path: str, line: int, text: str}]`

**Errors**
- Path outside allowlist → fail closed
- Empty query → empty hits or validation error

## fs_read_file

**Input**
- `path: str` (required)
- `max_bytes: int | null` — capped by server `fs_max_read_bytes`

**Output**
- `{path, size, truncated, content, encoding}`

**Errors**
- Escape / symlink outside roots → fail closed
- Directory path → error
- Missing file → error
