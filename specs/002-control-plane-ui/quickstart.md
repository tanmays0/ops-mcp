# Quickstart: Control Plane UI (GitHub Pages)

## Local preview

```bash
cd site
python -m http.server 8080
# open http://127.0.0.1:8080/
```

If using project Pages path locally, open with a note that production is `/ops-mcp/`.

## Deploy (after merge to main)

1. Ensure `.github/workflows/pages.yml` publishes `site/` to GitHub Pages.
2. Repo **Settings → Pages**: Source = GitHub Actions.
3. Confirm URL: `https://tanmays0.github.io/ops-mcp/`
4. Set GitHub About **Website** to that URL.

## Smoke checklist

- [ ] Eight tools visible with safety notes
- [ ] Setup snippet copy works; secrets warning visible
- [ ] Three playground scenarios: dry-run, success sim, refusal
- [ ] Sample events show no secrets
- [ ] Architecture line: UI ≠ MCP stdio server
