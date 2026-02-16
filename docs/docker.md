# Docker Setup Guide

This project supports two development workflows: **Full Docker** (production-like) and **Dev Mode** (fast iteration).

---

## Quick Start

### Fast Development (Recommended for Daily Coding)

```bash
# 1. Start database and Redis only
docker-compose -f docker-compose.dev.yml up -d

# 2. Run the API on your machine
uv run uvicorn app.main:app --reload

# 3. Visit http://localhost:8000/docs
```

**Why this way?**

- ✅ Instant code changes (no rebuild)
- ✅ Easy debugging in IDE
- ✅ Faster iteration
- ✅ Hot reload works perfectly

**Stop services:**

```bash
docker-compose -f docker-compose.dev.yml down
```

---

### Full Docker (Production-like)

```bash
# Start everything (DB + Redis + API) in Docker
docker-compose up --build

# Or run in background
docker-compose up --build -d

# View logs
docker-compose logs -f app

# Stop everything
docker-compose down
```

**Why this way?**

- ✅ Most production-like
- ✅ Consistent environment across team
- ✅ Tests deployment setup
- ❌ Slower iteration (needs rebuild on dependency changes)

---

## File Overview

### `docker-compose.yml` (Full Stack)

Runs **all services** in Docker:

- PostgreSQL (with pgvector extension)
- Redis
- FastAPI app

```yaml
services:
  app:
    build: .
    depends_on:
      postgres:
        condition: service_healthy # Waits for DB to be ready
      redis:
        condition: service_healthy
    volumes:
      - .:/app # Code mounted for hot reload
    command: uvicorn app.main:app --reload # Auto-restart on changes
```

**Key features:**

- App waits for DB to be healthy before starting
- Code changes trigger automatic reload (even in Docker!)
- Environment variables configured for container networking

**Usage:**

```bash
docker-compose up          # Start all services (foreground)
docker-compose up -d       # Start all services (background)
docker-compose logs -f app # Follow app logs
docker-compose down        # Stop all services
docker-compose down -v     # Stop and remove volumes (fresh start)
```

---

### `docker-compose.dev.yml` (DB + Redis Only)

Runs **only infrastructure** services:

- PostgreSQL
- Redis

FastAPI app runs on **host machine** for fast development.

**Usage:**

```bash
# Start infrastructure
docker-compose -f docker-compose.dev.yml up -d

# Run app on host
uv run uvicorn app.main:app --reload

# Stop infrastructure
docker-compose -f docker-compose.dev.yml down
```

---

### `Dockerfile`

Defines how to build the FastAPI app container.

```dockerfile
FROM python:3.14-slim
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy app code
COPY . .

# Run server
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**When is it used?**

- Only when running `docker-compose up --build` (full Docker mode)
- NOT used in dev mode (app runs on host)

---

### `.dockerignore`

Tells Docker which files to **exclude** from the build context (faster builds).

Excludes:

- `.git/`, `.venv/`, `__pycache__/`
- IDE files (`.vscode/`, `.idea/`)
- Environment files (`.env`)

---

## Understanding the Two Modes

### Mode 1: Dev Mode (Fast Development)

```
┌─────────────────────────────────┐
│  Your Machine                   │
│                                 │
│  ┌─────────────────────┐       │
│  │  FastAPI App        │       │
│  │  (host machine)     │       │
│  │  localhost:8000     │       │
│  └──────────┬──────────┘       │
│             │                   │
│     connects to ↓               │
│                                 │
│  ┌─────────────────────┐       │
│  │  Docker Containers  │       │
│  │  ├─ PostgreSQL      │       │
│  │  └─ Redis           │       │
│  └─────────────────────┘       │
└─────────────────────────────────┘
```

**How it works:**

1. Docker runs PostgreSQL and Redis
2. Your app runs on your machine
3. App connects to `localhost:5432` (Postgres) and `localhost:6379` (Redis)
4. Code changes = instant reload (no Docker rebuild!)

**Configuration:**

```python
# .env file
POSTGRES_HOST=localhost  # ← Host machine
REDIS_HOST=localhost
```

---

### Mode 2: Full Docker (Production-like)

```
┌─────────────────────────────────┐
│  Docker Containers              │
│                                 │
│  ┌─────────────────────┐       │
│  │  FastAPI App        │       │
│  │  (container)        │       │
│  └──────────┬──────────┘       │
│             │                   │
│     connects to ↓               │
│             │                   │
│  ┌──────────┴──────────┐       │
│  │  PostgreSQL         │       │
│  └─────────────────────┘       │
│  ┌─────────────────────┐       │
│  │  Redis              │       │
│  └─────────────────────┘       │
└─────────────────────────────────┘
```

**How it works:**

1. Everything runs in Docker containers
2. Containers talk to each other via Docker network
3. App connects to `postgres:5432` and `redis:6379` (service names!)
4. Code changes trigger reload, but slower than host

**Configuration:**

```yaml
# docker-compose.yml sets these
POSTGRES_HOST=postgres  # ← Service name in Docker network
REDIS_HOST=redis
```

---

## Common Commands

### Check Container Status

```bash
docker ps

# Expected output:
# dreamscape-postgres  (healthy)
# dreamscape-redis     (healthy)
# dreamscape-api       (if running full Docker)
```

### View Logs

```bash
# All services
docker-compose logs -f

# Just the app
docker-compose logs -f app

# Just PostgreSQL
docker-compose logs -f postgres
```

### Fresh Start (Delete All Data)

```bash
# Stop and remove volumes (deletes database data!)
docker-compose down -v

# Start fresh
docker-compose up -d
```

### Rebuild After Dependency Changes

```bash
# If you added new packages to pyproject.toml
docker-compose up --build
```

### Access PostgreSQL Directly

```bash
docker exec -it dreamscape-postgres psql -U dreamscape -d dreamscape

# Then run SQL:
# \dt  -- list tables
# \q   -- quit
```

### Access Redis Directly

```bash
docker exec -it dreamscape-redis redis-cli

# Then run commands:
# PING  -- should return PONG
# KEYS *  -- list all keys
# exit
```

---

## Health Checks Explained

Both PostgreSQL and Redis have **health checks** configured:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U dreamscape"]
  interval: 10s # Check every 10 seconds
  timeout: 5s # Max 5 seconds per check
  retries: 5 # Must pass 5 times to be "healthy"
```

**Why?**

- Prevents app from starting before DB is ready
- Docker knows when services are actually functional (not just running)
- `depends_on: { condition: service_healthy }` waits for healthy status

**Check health:**

```bash
docker ps

# STATUS column shows:
# "Up 2 minutes (healthy)"      ← Good!
# "Up 30 seconds (starting)"    ← Still initializing
# "Up 5 minutes (unhealthy)"    ← Problem!
```

---

## Troubleshooting

### "Database connection failed"

**If using dev mode:**

```bash
# Make sure containers are running
docker ps

# Should see:
# dreamscape-postgres  (healthy)
# dreamscape-redis     (healthy)

# Check .env file
cat .env
# Should have:
# POSTGRES_HOST=localhost
# REDIS_HOST=localhost
```

**If using full Docker:**

```bash
# Check logs
docker-compose logs app

# Environment should show:
# POSTGRES_HOST=postgres  (not localhost!)
```

---

### "Port 5432 already in use"

Another PostgreSQL instance is running on your machine.

```bash
# Stop it
brew services stop postgresql

# Or use different port in docker-compose.yml:
ports:
  - "5433:5432"  # Maps to localhost:5433
```

---

### "pg18-trixie volume error"

Old PostgreSQL data exists. Delete volumes and start fresh:

```bash
docker-compose down -v  # -v removes volumes!
docker-compose up -d
```

---

### App can't reach DB in full Docker mode

Check that `POSTGRES_HOST` is set correctly:

```yaml
# In docker-compose.yml
environment:
  - POSTGRES_HOST=postgres # ← Must be service name, not localhost!
```

---

## When to Use Which Mode?

### Use Dev Mode (`docker-compose.dev.yml`) when:

- ✅ Actively coding and testing
- ✅ Want instant feedback on changes
- ✅ Debugging with IDE breakpoints
- ✅ Experimenting with new features

### Use Full Docker (`docker-compose.yml`) when:

- ✅ Testing the full deployment
- ✅ Sharing with team members
- ✅ Ensuring production parity
- ✅ Before creating a PR
- ✅ CI/CD pipelines

---

## Best Practice Workflow

**Daily development:**

```bash
# Morning: Start infrastructure
docker-compose -f docker-compose.dev.yml up -d

# Code all day with hot reload
uv run uvicorn app.main:app --reload

# Evening: Stop infrastructure
docker-compose -f docker-compose.dev.yml down
```

**Before committing:**

```bash
# Test full Docker setup
docker-compose up --build

# If everything works, commit!
git add .
git commit -m "Add feature X"
```

---

## Summary

| Aspect              | Dev Mode                                         | Full Docker                 |
| ------------------- | ------------------------------------------------ | --------------------------- |
| **Command**         | `docker-compose -f docker-compose.dev.yml up -d` | `docker-compose up --build` |
| **App runs**        | On host machine                                  | In Docker container         |
| **Speed**           | ⚡ Fast (instant reload)                         | 🐢 Slower (rebuild needed)  |
| **Debugging**       | ✅ Easy (IDE breakpoints)                        | ❌ Harder                   |
| **Production-like** | ❌ No                                            | ✅ Yes                      |
| **Best for**        | Daily coding                                     | Testing deployment          |

**Recommendation: Use Dev Mode for development, Full Docker for testing before deployment.**
