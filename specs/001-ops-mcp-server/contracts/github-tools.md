# Contract: GitHub Tools

## github_list_issues

**Input**: `owner`, `repo`, `state` (default open), `labels` (optional), `per_page`
**Output**: `{issues: [{number, title, state, labels, is_pull_request, html_url}]}`
**Errors**: missing token → config error; API errors surfaced without secrets

## github_create_issue

**Input**: `owner`, `repo`, `title`, `body?`, `labels?`, `dry_run` (default **true**)
**Output (dry_run)**: `{dry_run: true, would_create: {...}}`
**Output (write)**: `{dry_run: false, issue: {number, title, state, html_url}}`
**Safety**: default dry-run; no remote POST unless `dry_run=false`

## github_pr_diff_summary

**Input**: `owner`, `repo`, `pull_number`
**Output**: PR stats + per-file `{filename, status, additions, deletions, changes}`
**Safety**: never include `patch` / full file contents
