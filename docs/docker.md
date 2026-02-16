# Docker Setup

## What We Have

- `docker-compose.yml` = Full stack (Postgres + Redis + FastAPI in Docker)
- `docker-compose.dev.yml` = Just databases (FastAPI runs on your machine)
- `Dockerfile` = How to build the FastAPI container

## Daily Commands (Full Docker - Recommended)

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f app

# Restart app after changes
docker-compose restart app

# Stop everything
docker-compose down

# Fresh start (⚠️ deletes database)
docker-compose down -v
```

## Alternative: Hybrid Dev Mode (Faster reload)

```bash
# Start just databases
docker-compose -f docker-compose.dev.yml up -d

# Run app on your machine (in another terminal)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Stop databases
docker-compose -f docker-compose.dev.yml down
```

**Why use this:**
- Faster code reload
- Easier debugging
- But more setup (two terminals)

## Database Access

```bash
# PostgreSQL shell
docker exec -it dreamscape-postgres psql -U dreamscape -d dreamscape

# Redis CLI
docker exec -it dreamscape-redis redis-cli
```

## Common Issues

**Port already in use:**
```bash
lsof -ti:8000              # Find what's using port
kill -9 $(lsof -ti:8000)   # Kill it
```

**Database connection failed:**
```bash
docker ps                  # Check containers are healthy
docker-compose logs postgres
```

**Added new packages:**
```bash
docker-compose up -d --build
```

## What Runs Where

### Full Docker Mode (docker-compose.yml)
- PostgreSQL → Docker (port 5432)
- Redis → Docker (port 6379)
- FastAPI → Docker (port 8000)
- App connects to `postgres:5432` (Docker network)

### Hybrid Dev Mode (docker-compose.dev.yml)
- PostgreSQL → Docker (port 5432)
- Redis → Docker (port 6379)
- FastAPI → Your machine (port 8000)
- App connects to `localhost:5432`

## Health Checks

Both compose files have health checks:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U dreamscape"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**Why:**
- App waits for DB to be ready before starting
- `depends_on: service_healthy` prevents startup errors

**Check status:**
```bash
docker ps  # Look for "(healthy)" in STATUS column
```

## Which Mode to Use

**Full Docker** = Simple, consistent, good for this project
**Hybrid Dev** = Faster iteration if you need it later

Start with Full Docker (`docker-compose up -d`). Switch to Hybrid later if you want faster reload.
