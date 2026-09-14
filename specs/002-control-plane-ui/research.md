# Research: OpsMCP Control Plane UI

## Decision: GitHub Pages as primary host (v1.1)

- **Choice**: GitHub Pages project site for `tanmays0/ops-mcp`
- **Rationale**: Free on public repos; URL sits next to the code; no credit card; fits static companion scope
- **Alternatives**: Vercel/Netlify (easy later port of same `site/`); Fly.io (needs a process — unnecessary for static)
- **Defer**: Live backends, serverless tool proxies

## Decision: Fully static + simulated playground

- **Choice**: Browser-side canned responses + client-side “policy demos” (e.g. reject strings matching DROP / path escape demos)
- **Rationale**: No secrets on a public host; zero abuse surface; works offline
- **Alternatives**: Live demo env (cost/complexity); passphrase-gated API (still needs a backend)
- **Honesty rule**: UI must label simulations clearly so interviews don’t overclaim

## Decision: Sample observability events (not live MCP logs)

- **Choice**: Checked-in `sample-events.json` shaped like `log_tool_call` fields
- **Rationale**: Pages cannot see the builder’s laptop stdio process
- **Alternatives**: Ship logs to a SaaS (out of scope / cost)

## Decision: Zero-build vanilla site

- **Choice**: HTML/CSS/JS in `site/` with JSON data files
- **Rationale**: Fast to ship, no Node toolchain required for contributors, trivial Pages deploy
- **Alternatives**: Next/Vite React — nicer DX but heavier for a catalog+demo page; revisit if UI grows

## Decision: Publish path `/ops-mcp/`

- **Choice**: Project Pages with `base` awareness for asset paths
- **Rationale**: Default for project sites under `username.github.io/repo`
- **Note**: Relative URLs or `<base href>` / path prefix in JS fetch for `data/*.json`

## Decision: Keep MCP package independent

- **Choice**: Do not couple FastMCP runtime to the static site
- **Rationale**: Constitution + architecture: UI is companion only

## Open items resolved by product owner (2026-09-15)

| Topic | Resolution |
|-------|------------|
| Playground mode | Simulated only |
| Access model | Fully public static |
| Host | GitHub Pages first; Vercel/Netlify later optional |
