# Project: ITS (Issue Tracking System)

## Overview

Full-stack issue tracking system with real-time updates.

## Structure

```
its/
├── backend/           # FastAPI + SQLAlchemy + Alembic
│   ├── app/           # Application code
│   │   ├── main.py   # Entry point
│   │   ├── models.py # SQLAlchemy models
│   │   ├── schemas.py # Pydantic schemas
│   │   └── routers/  # API endpoints
│   ├── alembic/       # Database migrations
│   ├── pyproject.toml # Python deps (uv)
│   └── .env.example   # Env template
├── frontend/          # SvelteKit + Tailwind
│   ├── src/
│   │   ├── lib/      # Components, stores, utils
│   │   └── routes/   # Pages
│   ├── package.json  # Node deps
│   └── .env.example  # Env template
├── docker-compose.yml # Postgres + MinIO
└── dev.sh           # Development commands
```

## Quick Start

```bash
# First time
./dev.sh setup

# Start developing
./dev.sh up

# View logs
./dev.sh logs

# Stop
./dev.sh down
```

## Development Commands

| Command | Description |
|---------|-------------|
| `./dev.sh setup` | One-time setup |
| `./dev.sh up` | Start all services |
| `./dev.sh down` | Stop all services |
| `./dev.sh logs` | Tail combined logs |
| `./dev.sh status` | Show running services |
| `./dev.sh clean` | Full reset |
| `./dev.sh lint` | Run linters |
| `./dev.sh test` | Run tests |

## Backend

- **Framework:** FastAPI
- **Python:** 3.12 (managed by pyenv)
- **Package Manager:** uv
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Linter:** ruff

### Commands

```bash
cd backend
uv sync              # Install deps
uv run uvicorn app.main:app --reload  # Dev server
uv run alembic upgrade head  # Migrations
uv run ruff check .  # Lint
uv run ruff format . # Format
uv run pytest        # Tests
```

## Frontend

- **Framework:** SvelteKit 5 (Svelte with Runes)
- **Build:** Vite
- **CSS:** Tailwind CSS 4
- **UI:** shadcn-svelte (bits-ui)
- **Formatters:** Prettier

### Commands

```bash
cd frontend
npm install         # Install deps
npm run dev         # Dev server
npm run check       # Type check
npm run lint        # Format check
npm run format      # Format
npm run test        # Tests (Vitest)
```

## Database

- **PostgreSQL** in Docker (port 5433)
- **MinIO** for file storage (ports 9002/9003)

### Port Mappings (local)

| Service | Local Port | Docker Internal |
|---------|------------|-----------------|
| Postgres | 5433 | 5432 |
| MinIO API | 9002 | 9000 |
| MinIO Console | 9003 | 9001 |

## Code Style

### Python
- Use `uv` for all Python package management
- Run `ruff check .` and `ruff format .` before committing
- Type hints required

### JavaScript/Svelte
- Use Prettier for formatting (configured in `.prettierrc`)
- TypeScript strict mode
- Run `npm run check` before committing

## Pre-commit Hooks

Pre-commit hooks run automatically before each commit to catch issues early.

## Testing

- **Backend:** pytest
- **Frontend:** Vitest

Run all tests with: `./dev.sh test`

## Environment Variables

Copy `.env.example` files to `.env` in:
- Root directory
- `backend/`
- `frontend/`

Update values as needed for local development.

## Common Tasks

### Reset Database
```bash
./dev.sh db:reset
```

### Create Migration
```bash
cd backend
uv run alembic revision --autogenerate -m "description"
```

### Add Frontend Component (shadcn-svelte)
```bash
npx shadcn-svelte@latest add component-name
```

## Architecture Notes

- JWT authentication with access/refresh tokens
- WebSocket support for real-time updates
- MinIO (S3-compatible) for file attachments
- SQLAlchemy models in `backend/app/models.py`
- Pydantic schemas in `backend/app/schemas.py`
- API routes in `backend/app/routers/`
