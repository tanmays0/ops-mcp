# Tasks: OpsMCP Control Plane UI (GitHub Pages)

**Input**: Design documents from `/specs/002-control-plane-ui/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Optional smoke checklist (quickstart); no separate E2E suite required for v1.1 unless added later

**Organization**: By user story (US1–US4)

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

**Purpose**: Static site skeleton and Pages wiring

- [x] T001 Create `site/` directory with `index.html`, `styles.css`, `app.js`, and `site/data/`
- [x] T002 [P] Add `.github/workflows/pages.yml` to publish `site/` to GitHub Pages (Actions source)
- [x] T003 [P] Document local preview (`python -m http.server`) in `site/README.md` (short)
- [x] T004 Implement base layout in `site/index.html` (nav: Catalog, Setup, Playground, Observability) + architecture one-liner (UI ≠ MCP stdio)
- [x] T005 Implement `site/app.js` helpers: resolve `BASE` for project Pages path, `fetch` JSON under `site/data/`, truncate/redact token-like strings
- [x] T006 [P] Author `site/data/tools.json` with all **eight** tools (names match `src/ops_mcp/server.py`) per `contracts/tool-catalog.md`
- [x] T007 [P] Author `site/data/setup.mcp.json.example` aligned with `.cursor/mcp.json.example` (placeholders only)
- [x] T008 [US1] Render tool catalog from `tools.json` in `site/index.html` / `site/app.js`
- [x] T009 [US1] Style catalog for mobile + desktop in `site/styles.css` (readable, not dashboard-cluttered)
- [x] T010 [US1] Verify safety notes cover dry-run, SELECT-only, path sandbox, no patches on PR tool
- [x] T011 [US2] Setup section loads `setup.mcp.json.example` and shows copy button in `site/app.js`
- [x] T012 [US2] Add explicit warnings: secrets in `.env` only; never paste tokens into the public UI
- [x] T013 [US2] High-level steps: clone → env → `uv run python -m ops_mcp` → point Cursor at it
- [x] T014 [P] [US3] Author `site/data/playground.json` with scenarios from `contracts/playground-sim.md`
- [x] T015 [US3] Playground UI: select scenario → show inputs → Run → result panel with **Simulated** badge
- [x] T016 [US3] Block/redact `ghp_`, `github_pat_`, `postgresql://` style input before display
- [x] T017 [US3] Ensure create-issue demo is dry-run shaped; DROP and path escape are refusals
- [x] T018 [P] [US4] Author `site/data/sample-events.json` (safe fields only)
- [x] T019 [US4] Render health (“static companion available”) + sample events table/list
- [x] T020 [US4] Caption: not live laptop MCP logs; shape matches structured tool logs
- [x] T021 [P] README.md: add Pages URL placeholder + one line that `site/` is the companion UI
- [ ] T022 Run quickstart.md smoke checklist locally
- [ ] T023 Merge to `main`, enable Pages (Settings → Actions), verify `https://tanmays0.github.io/ops-mcp/`
- [ ] T024 Set GitHub About **Website** to the Pages URL
- [ ] T025 Confirm `uv run pytest` still green (MCP core untouched)

---

## Dependencies & Execution Order

- Phase 1 → Phase 2 → US1 (MVP) → US2 → US3 → US4 → Polish
- US1+US2 are both P1; US1 first for MVP linkability
- T006/T007/T014/T018 are parallelizable data authoring

## Implementation Strategy

1. Ship **US1 catalog** as soon as Pages deploys — enough for Website field
2. Add setup, then playground, then sample logs
3. Do **not** add live backends on this branch

## Notes

- Do not commit `OpsMCP-Interview-Master-Guide.md` as part of this feature
- Do not put secrets in `site/data/`
- Future Vercel/Netlify = same `site/` assets, different host
