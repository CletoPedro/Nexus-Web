# NEXUS WEB

NEXUS is a personal life operating system. This is the web implementation
(`nexus-web`) — the primary implementation as of the W-phase pivot.

**Current milestone: W4.5 — First Usable NEXUS.** You can create, edit,
delete, list, and search personal memories in a browser, backed by a real
PostgreSQL database, with no AI involved.

---

## Option A — Run locally (no Docker)

Prerequisites: Node.js 22+, `pnpm`, Python 3.12+, `uv`, PostgreSQL 16 running
locally.

### 1. Database

```bash
# Create a database and user (adjust to your local Postgres setup)
psql -c "CREATE USER nexus WITH PASSWORD 'nexus';"
psql -c "CREATE DATABASE nexus OWNER nexus;"
```

### 2. Backend

```bash
cd backend
cp .env.example .env        # adjust DATABASE_URL if needed
uv sync                     # installs dependencies
uv run alembic upgrade head # creates the memories table
uv run uvicorn app.main:app --reload --port 8000
```

Backend is now running at http://localhost:8000. Check it:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/db   # should report {"status":"ok"}
```

Interactive API docs: http://localhost:8000/docs

### 3. Frontend

In a separate terminal:

```bash
cd frontend
cp .env.local.example .env.local   # NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
pnpm install
pnpm dev
```

Open http://localhost:3000/memory in your browser.

---

## Option B — Docker Compose

Prerequisites: Docker + Docker Compose.

```bash
cd infrastructure/docker
docker compose up --build
```

This starts three containers:
- `nexus-postgres` — PostgreSQL 16, persisted in a named volume
- `nexus-backend` — FastAPI, runs `alembic upgrade head` automatically on
  startup before serving, on port 8000
- `nexus-frontend` — Next.js production build, on port 3000

Open http://localhost:3000/memory once all three are healthy.

To stop: `docker compose down` (add `-v` to also delete the database volume).

**Note:** the Docker Compose setup has been written and reviewed but **not
executed** in the sandbox this project was developed in — Docker isn't
installed there and Docker Hub / GHCR aren't reachable from its network
egress rules. Everything it orchestrates (Postgres, the backend, the
migration, the frontend) has been verified working when run directly on
the host (Option A); the Compose file itself should be treated as
reviewed-but-unverified until you run it in your own environment. Please
report back if `docker compose up` surfaces anything unexpected.

---

## What you can do right now

- Go to `/memory`
- Click **New memory**, type something like *"My passport is inside the
  safe."*, optionally add comma-separated tags, save
- Create a few more
- Search for a word from one of them — full-text search (Postgres
  `tsvector`, no AI) finds it
- Hover a memory card to edit or delete it
- Toggle dark/light mode from the top-right of the shell

See `docs/architecture/PHASE_W1_ARCHITECTURE.md` for the full architecture
and `docs/phases/` for phase-by-phase implementation reports, including
`PHASE_W4_5_REPORT.md` for this milestone's test results and known issues.
