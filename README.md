# Issue Tracking System

A full-stack issue tracking system with real-time updates, built with FastAPI, SvelteKit, PostgreSQL, and MinIO.

## Quick Start

```bash
# One-time setup (copies env files, installs deps, runs migrations)
./dev.sh setup

# Start all services
./dev.sh up

# View logs
./dev.sh logs
```

## Requirements

- Docker & Docker Compose
- Python 3.12+ (managed by pyenv)
- Node.js 22+

## Development Commands

```bash
./dev.sh setup      # One-time setup
./dev.sh up         # Start all services in background
./dev.sh down       # Stop all services
./dev.sh logs       # Tail combined logs
./dev.sh status     # Show running services
./dev.sh lint       # Run linters (ruff, prettier)
./dev.sh format     # Format code
./dev.sh check      # Type check (svelte-check)
./dev.sh test       # Run tests (pytest, vitest)
./dev.sh precommit  # Install pre-commit hooks
./dev.sh db:reset   # Reset database
./dev.sh clean      # Full reset (removes venv, node_modules)
```

## URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| MinIO Console | http://localhost:9003 |

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, Alembic, PostgreSQL
- **Frontend:** SvelteKit 5, Tailwind CSS 4, shadcn-svelte
- **Storage:** MinIO (S3-compatible)
- **Package Managers:** uv (Python), npm (Node)

## Project Structure

```
its/
├── backend/           # FastAPI + SQLAlchemy
│   ├── app/          # Application code
│   ├── alembic/       # Database migrations
│   └── pyproject.toml # Dependencies
├── frontend/          # SvelteKit + Tailwind
│   ├── src/
│   │   ├── lib/      # Components, stores, utils
│   │   └── routes/   # Pages
│   └── package.json
├── docker-compose.yml # Postgres + MinIO
└── dev.sh            # Development commands
```

## Docker Setup (Alternative)

For containerized development:

```bash
docker compose up --build
```

Database migrations run automatically on startup.
