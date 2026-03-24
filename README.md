# Issue Tracking System

## Requirements
- Docker
- Docker Compose

## Setup

1. Clone the repo then cd into project root.
```bash
git clone https://github.com/swapnil-up/its.git
cd its
```

2. Copy the environment file and fill in your values:
```bash
   cp .env.example .env
```

3. Build and start all services:
```bash
   docker compose up --build
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

Database migrations run automatically on startup.
