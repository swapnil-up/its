#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_DIR="$SCRIPT_DIR/.dev"
LOGS_DIR="$DEV_DIR/logs"
PIDS_DIR="$DEV_DIR/pids"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

UV_Path() {
	if [ -f "$HOME/.local/bin/uv" ]; then
		echo "$HOME/.local/bin/uv"
	else
		echo "uv"
	fi
}

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERR]${NC} $1" >&2; }

need_setup() {
	if [ ! -f "$DEV_DIR/.setup_complete" ]; then
		log_error "Setup not complete. Run: $0 setup"
		exit 1
	fi
}

ensure_dev_dir() {
	mkdir -p "$LOGS_DIR" "$PIDS_DIR"
}

wait_for_postgres() {
	local max_attempts=30
	local attempt=1

	log_info "Waiting for PostgreSQL to be ready..."
	while [ $attempt -le $max_attempts ]; do
		if docker compose exec -T db pg_isready -U postgres -p 5432 >/dev/null 2>&1; then
			log_success "PostgreSQL is ready"
			return 0
		fi
		echo -n "."
		sleep 1
		attempt=$((attempt + 1))
	done

	log_error "PostgreSQL failed to start after ${max_attempts}s"
	return 1
}

cmd_setup() {
	log_info "Starting setup..."

	ensure_dev_dir

	if [ -f "$DEV_DIR/.setup_complete" ]; then
		log_warn "Setup already complete. Run '$0 clean' first to reset."
		log_info "To re-run setup anyway, delete .dev/.setup_complete"
		return 0
	fi

	log_info "Copying environment files..."
	[ ! -f "$SCRIPT_DIR/.env" ] && cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env" && log_success "Created .env" || log_warn ".env already exists, skipping"
	[ ! -f "$BACKEND_DIR/.env" ] && cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env" && log_success "Created backend/.env" || log_warn "backend/.env already exists, skipping"
	[ ! -f "$FRONTEND_DIR/.env" ] && cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env" && log_success "Created frontend/.env" || log_warn "frontend/.env already exists, skipping"

	log_info "Starting Docker services (postgres, minio)..."
	docker compose up -d db minio
	wait_for_postgres

	log_info "Setting up Python environment with uv..."
	cd "$BACKEND_DIR"
	$(UV_Path) sync

	log_info "Running Alembic migrations..."
	$(UV_Path) run alembic upgrade head

	cd "$SCRIPT_DIR"
	log_info "Installing frontend dependencies..."
	cd "$FRONTEND_DIR"
	npm install

	cd "$SCRIPT_DIR"
	touch "$DEV_DIR/.setup_complete"
	log_success "Setup complete!"
	log_info "Run '$0 up' to start all services"
}

cmd_up() {
	need_setup

	log_info "Starting services..."

	log_info "Ensuring Docker services are running..."
	docker compose up -d db minio

	ensure_dev_dir

	log_info "Starting backend server..."
	cd "$BACKEND_DIR"
	nohup $(UV_Path) run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 >"$LOGS_DIR/backend.log" 2>&1 &
	echo $! >"$PIDS_DIR/backend.pid"
	sleep 2
	if ps -p $(cat "$PIDS_DIR/backend.pid") >/dev/null 2>&1; then
		log_success "Backend started (PID: $(cat $PIDS_DIR/backend.pid))"
	else
		log_error "Backend failed to start. Check $LOGS_DIR/backend.log"
	fi

	log_info "Starting frontend server..."
	cd "$FRONTEND_DIR"
	nohup npm run dev >"$LOGS_DIR/frontend.log" 2>&1 &
	echo $! >"$PIDS_DIR/frontend.pid"
	sleep 3
	if ps -p $(cat "$PIDS_DIR/frontend.pid") >/dev/null 2>&1; then
		log_success "Frontend started (PID: $(cat $PIDS_DIR/frontend.pid))"
	else
		log_error "Frontend failed to start. Check $LOGS_DIR/frontend.log"
	fi

	cd "$SCRIPT_DIR"

	echo ""
	log_success "All services started!"
	echo ""
	echo -e "  ${BLUE}Frontend:${NC}  http://localhost:5173"
	echo -e "  ${BLUE}Backend:${NC}   http://localhost:8000"
	echo -e "  ${BLUE}API Docs:${NC}  http://localhost:8000/docs"
	echo -e "  ${BLUE}MinIO:${NC}     http://localhost:9003"
	echo ""
	log_info "Run '$0 logs' to view combined logs"
}

cmd_down() {
	log_info "Stopping services..."

	if [ -f "$PIDS_DIR/backend.pid" ]; then
		local backend_pid=$(cat "$PIDS_DIR/backend.pid")
		if kill -0 "$backend_pid" 2>/dev/null; then
			kill "$backend_pid" 2>/dev/null || true
			log_success "Backend stopped"
		fi
		rm -f "$PIDS_DIR/backend.pid"
	fi

	if [ -f "$PIDS_DIR/frontend.pid" ]; then
		local frontend_pid=$(cat "$PIDS_DIR/frontend.pid")
		if kill -0 "$frontend_pid" 2>/dev/null; then
			kill "$frontend_pid" 2>/dev/null || true
			log_success "Frontend stopped"
		fi
		rm -f "$PIDS_DIR/frontend.pid"
	fi

	log_info "Stopping Docker services..."
	docker compose stop db minio 2>/dev/null || true

	log_success "All services stopped"
}

cmd_logs() {
	if command -v multitail >/dev/null 2>&1; then
		multitail -cS bash "$LOGS_DIR/backend.log" "$LOGS_DIR/frontend.log"
	else
		log_warn "multitail not found. Using combined tail -f"
		tail -f "$LOGS_DIR/backend.log" "$LOGS_DIR/frontend.log"
	fi
}

cmd_status() {
	echo -e "${BLUE}Docker Services:${NC}"
	docker compose ps 2>/dev/null || echo "  Docker compose not available"

	echo ""
	echo -e "${BLUE}Process Status:${NC}"

	if [ -f "$PIDS_DIR/backend.pid" ]; then
		if kill -0 "$(cat $PIDS_DIR/backend.pid)" 2>/dev/null; then
			echo -e "  Backend:   ${GREEN}running${NC} (PID: $(cat $PIDS_DIR/backend.pid))"
		else
			echo -e "  Backend:   ${RED}stopped${NC} (stale PID file)"
		fi
	else
		echo -e "  Backend:   ${YELLOW}not running${NC}"
	fi

	if [ -f "$PIDS_DIR/frontend.pid" ]; then
		if kill -0 "$(cat $PIDS_DIR/frontend.pid)" 2>/dev/null; then
			echo -e "  Frontend:  ${GREEN}running${NC} (PID: $(cat $PIDS_DIR/frontend.pid))"
		else
			echo -e "  Frontend:  ${RED}stopped${NC} (stale PID file)"
		fi
	else
		echo -e "  Frontend:  ${YELLOW}not running${NC}"
	fi
}

cmd_lint() {
	log_info "Running linters and formatters..."

	echo -e "${BLUE}Backend (ruff):${NC}"
	cd "$BACKEND_DIR"
	$(UV_Path) run ruff check .
	$(UV_Path) run ruff format --check .

	echo ""
	echo -e "${BLUE}Frontend (prettier):${NC}"
	cd "$FRONTEND_DIR"
	npm run lint

	log_success "Lint complete"
}

cmd_format() {
	log_info "Running formatters..."

	echo -e "${BLUE}Backend (ruff):${NC}"
	cd "$BACKEND_DIR"
	$(UV_Path) run ruff format .

	echo ""
	echo -e "${BLUE}Frontend (prettier):${NC}"
	cd "$FRONTEND_DIR"
	npm run format

	log_success "Format complete"
}

cmd_check() {
	log_info "Running type checks..."

	echo -e "${BLUE}Frontend (svelte-check):${NC}"
	cd "$FRONTEND_DIR"
	npm run check

	log_success "Check complete"
}

cmd_test() {
	log_info "Running tests..."

	echo -e "${BLUE}Backend (pytest):${NC}"
	cd "$BACKEND_DIR"
	$(UV_Path) run pytest -v

	echo ""
	echo -e "${BLUE}Frontend:${NC}"
	cd "$FRONTEND_DIR"
	if grep -q '"test"' package.json 2>/dev/null; then
		npm run test
	else
		log_warn "No test script found in frontend/package.json"
	fi

	log_success "Tests complete"
}

cmd_precommit() {
	log_info "Installing pre-commit hooks..."

	if ! command -v pre-commit &>/dev/null; then
		log_info "Installing pre-commit..."
		if command -v pip &>/dev/null; then
			pip install pre-commit
		elif [ -f "$BACKEND_DIR/.venv/bin/pip" ]; then
			"$BACKEND_DIR/.venv/bin/pip" install pre-commit
		else
			log_error "pip not found. Please install pre-commit manually: pip install pre-commit"
			return 1
		fi
	fi

	pre-commit install
	log_success "Pre-commit hooks installed!"
	log_info "Hooks will run automatically before each commit"
}

cmd_db_reset() {
	need_setup

	log_warn "This will drop and recreate the database!"
	read -p "Continue? [y/N] " -n 1 -r
	echo ""

	if [[ ! $REPLY =~ ^[Yy]$ ]]; then
		log_info "Cancelled"
		return 0
	fi

	cd "$BACKEND_DIR"
	$(UV_Path) run alembic downgrade -1
	$(UV_Path) run alembic upgrade head
	log_success "Database reset complete"
}

cmd_clean() {
	log_warn "This will stop all services and remove:"
	echo "  - backend/.venv"
	echo "  - frontend/node_modules"
	echo "  - .dev/ directory"
	echo ""
	read -p "Continue? [y/N] " -n 1 -r
	echo ""

	if [[ ! $REPLY =~ ^[Yy]$ ]]; then
		log_info "Cancelled"
		return 0
	fi

	cmd_down

	log_info "Removing Python virtual environment..."
	rm -rf "$BACKEND_DIR/.venv"

	log_info "Removing frontend node_modules..."
	rm -rf "$FRONTEND_DIR/node_modules"

	log_info "Removing .dev directory..."
	rm -rf "$DEV_DIR"

	log_success "Clean complete"
}

cmd_help() {
	echo "Usage: $0 <command>"
	echo ""
	echo "Commands:"
	echo "  setup      One-time setup (copy envs, docker, deps, migrations)"
	echo "  up         Start all services in background"
	echo "  down       Stop all running services"
	echo "  logs       Tail combined logs from both services"
	echo "  status     Show which services are currently running"
	echo "  lint       Run linters (ruff, prettier)"
	echo "  format     Run formatters (ruff, prettier)"
	echo "  check      Run type checks (svelte-check)"
	echo "  test       Run all tests (pytest, vitest)"
	echo "  precommit  Install pre-commit hooks"
	echo "  db:reset   Drop and recreate database"
	echo "  clean      Stop services + remove venv, node_modules, and .dev"
	echo "  help       Show this help message"
}

case "${1:-help}" in
setup) cmd_setup ;;
up) cmd_up ;;
down) cmd_down ;;
logs) cmd_logs ;;
status) cmd_status ;;
lint) cmd_lint ;;
format) cmd_format ;;
check) cmd_check ;;
test) cmd_test ;;
precommit) cmd_precommit ;;
db:reset) cmd_db_reset ;;
clean) cmd_clean ;;
help) cmd_help ;;
*)
	log_error "Unknown command: $1"
	echo ""
	cmd_help
	exit 1
	;;
esac
