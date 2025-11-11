202511101942 — DropSpot build kickoff

# DropSpot — Waitlist & Limited Claim Platform

DropSpot is a full-stack case implementation for the Alpaco Full Stack Developer challenge. It provides a FastAPI backend with a SQLite store and a Next.js frontend that lets users join waitlists, claim limited drops, and administer inventory.

## Table of Contents

- [Worklog & Roadmap](#worklog--roadmap)
- [Feature Summary](#feature-summary)
- [Architecture](#architecture)
- [Environment Variables](#environment-variables)
- [Getting Started](#getting-started)
  - [Backend (FastAPI)](#backend-fastapi)
  - [Frontend (Next.js)](#frontend-nextjs)
- [Seed Generator Utility](#seed-generator-utility)
- [Testing](#testing)
- [Continuous Integration](#continuous-integration)
- [Screenshots](#screenshots)

## Worklog & Roadmap

| Branch | Focus | Status |
| --- | --- | --- |
| feature/project-scaffold | Repo scaffolding, env setup | ✅ completed |
| feature/backend-auth | Auth + user management | ✅ completed |
| feature/backend-drops | Drop lifecycle, waitlist, claim | ✅ completed |
| feature/frontend-base | Public-facing flow | ✅ completed |
| feature/frontend-admin | Admin CRUD, AI helper | ✅ completed |
| feature/tests-ci | Automated tests + CI | ✅ completed |

Each branch lands with a PR summarising the problem statement, solution outline, and automated test results.

## Feature Summary

- Authenticated signup & login with JWT tokens and role-aware (admin vs member) capabilities.
- Drop management lifecycle: create, list, update, delete drops and expose waitlist/claim windows.
- Waitlist service calculates priority scores via deterministic seed-based weighting and enforces claim quotas.
- Responsive Next.js frontend featuring landing, drop browsing, admin dashboard, and auth flows.
- Automated pytest integration tests for the backend and React Testing Library coverage for core components.

## Architecture

- **Backend:** FastAPI, SQLAlchemy ORM, SQLite (development) with modular routers/services. Configurable for Postgres via `DATABASE_URL`.
- **Frontend:** Next.js 14 App Router, Zustand for session persistence, SWR-style API helpers.
- **Shared utilities:** Seed-based priority scoring logic (`backend/app/services/seed.py`) with deterministic coefficients.
- **CI:** GitHub Actions pipeline runs backend pytest, frontend unit tests, and a Next.js production build.

## Environment Variables

Copy `.env.example` into `.env` for local development:

```bash
cp backend/.env.example backend/.env
```

Key variables:

- `DATABASE_URL`: set to a Postgres connection string in production (defaults to SQLite file).
- `JWT_SECRET_KEY`: secret used to sign access tokens.
- `DROPSPOT_SEED`: optional override for priority score determinism.

Frontend expects `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000`).

## Getting Started

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[test]"
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. A `/health` endpoint is provided for smoke testing. SQLite migrations run automatically on startup.

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` for the marketing landing page and `http://localhost:3000/drops` to browse active drops.

## Seed Generator Utility

- Deterministic priority scoring lives in `backend/app/services/seed.py`.
- Use `compute_priority_score` to evaluate queue position; coefficients derive from `DROPSPOT_SEED`.
- `derive_seed(remote_url, first_commit_epoch, start_time)` can bootstrap a repeatable seed value tied to repository metadata.

## Testing

- **Backend:** `cd backend && pytest` executes unit and integration suites (waitlist flow, seed logic, auth).
- **Frontend:** `cd frontend && npm test -- --runInBand` runs component tests for AuthPanel and DropList via Jest + RTL.
- Both suites are wired into the GitHub Actions pipeline for regression protection.

## Continuous Integration

GitHub Actions configuration lives in `.github/workflows/ci.yml`.

- Runs on pushes and PRs targeting `master`.
- Job 1 (backend) installs Python 3.11 dependencies and executes pytest.
- Job 2 (frontend) runs `npm ci`, executes unit tests, and builds the Next.js app.

## Screenshots

Screenshots live in `docs/screenshots/` (add new captures as PNG files):

- Landing page — `![Landing](docs/screenshots/landing.png)`
- Drops listing — `![Drops](docs/screenshots/drops.png)`
- Admin dashboard — `![Admin](docs/screenshots/admin.png)`

## TODO Snapshot

- [x] Backend FastAPI skeleton with database wiring
- [x] Frontend Next.js app shell
- [x] Shared seed generator utility
- [x] README finalization with required sections and screenshots
- [x] Automated tests (backend unit/integration, frontend components)
- [x] GitHub Actions workflow (bonus)

Progress updates continue in commit messages and PR descriptions.
