# CHANGELOG

All notable changes to POLYPRO are recorded here.
Detailed release notes, iteration summaries, and test results are in [`docs/`](docs/).

---

## [Unreleased]

---

## [0.1.5] — 2026-04-02
### Changed
- `launcher/src/launcher.py` — added `check_preflight()`, `_check_early_exit()`, stdout/stderr capture, hardened `run()` flow
- `launcher/tests/test_launcher.py` — expanded from 14 to 17 tests; added process cleanup, terminate coverage, and frontend early-exit documentation

### Notes
- Launcher tests: 17 / 17 PASSED

---

## [0.1.4] — 2026-04-02
### Added
- Foundation verification: live uvicorn subprocess + HTTP health integration test
- All three layers (backend, frontend, launcher) verified together

### Notes
- Backend: 3 / 3, Frontend: 3 / 3, Launcher: 5 / 5, Live: 1 / 1

---

## [0.1.3] — 2026-04-02
### Added
- `launcher/src/launcher.py` — subprocess orchestration: start_backend, start_frontend, wait_for_health, open_browser, terminate, run()
- `launcher/tests/test_launcher.py` — 5 tests

---

## [0.1.2] — 2026-04-02
### Added
- React + Vite + TypeScript + Tailwind v4 frontend shell
- BrowserRouter with `/`, `/user`, `/admin` routes
- Layout, HealthBadge, route components
- Vitest test suite: 3 tests

---

## [0.1.1] — 2026-04-02
### Added
- FastAPI backend shell with lifespan handler
- `GET /health` endpoint
- env-based config, stdlib logger
- pytest test suite: 3 tests
