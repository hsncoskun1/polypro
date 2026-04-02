# Iteration Summary — Foundation (v0.1.1 – v0.1.4)

## Scope
Build the POLYPRO foundation from scratch: backend, frontend, launcher, and end-to-end verification.

## Versions in This Iteration
| Version | Focus | Status |
|---------|-------|--------|
| v0.1.1 | Backend shell (FastAPI) | Merged to main |
| v0.1.2 | Frontend shell (React + Vite) | Merged to main |
| v0.1.3 | Launcher shell (subprocess orchestration) | Merged to main |
| v0.1.4 | Foundation verification (integration tests) | Merged to main |

## Delivery Method
All four versions were developed on separate branches and merged to main together via PR #2.

## Total Tests at End of Iteration
- Backend: 3
- Frontend: 3
- Launcher: 5
- Live integration: 1
- **Total: 12 tests, all passing**

## Architecture Decisions
- Backend: FastAPI with lifespan handler (not deprecated `on_event`)
- Frontend: React Router v7, Tailwind v4 via `@tailwindcss/vite`, Vitest + jsdom
- Launcher: pure stdlib Python, no third-party dependencies
- Config: env-based (`os.getenv`), no secrets in repo

## Notes
- Foundation reset was performed before v0.1.1 (PR #1) to establish clean slate
- No legacy code or prior architecture referenced
