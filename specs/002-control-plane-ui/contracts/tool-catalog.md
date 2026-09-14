# Contract: Tool Catalog (static)

## Endpoint / surface

Static page section + `GET` relative `data/tools.json` (same origin on Pages).

## `tools.json` shape

```json
{
  "version": 1,
  "tools": [
    {
      "name": "github_create_issue",
      "system": "github",
      "summary": "Create a GitHub issue; default dry_run=true",
      "inputs": [
        {"name": "owner", "type": "string", "required": true},
        {"name": "repo", "type": "string", "required": true},
        {"name": "title", "type": "string", "required": true},
        {"name": "dry_run", "type": "boolean", "required": false, "default": true}
      ],
      "outputs": "{ dry_run, would_create } | { dry_run, issue }",
      "safety": ["dry_run defaults true", "token never returned"]
    }
  ]
}
```

## Invariants

- Exactly **eight** tools matching MCP server registration names.
- No live credentials in file.
- Safety notes must not contradict core server behavior.
