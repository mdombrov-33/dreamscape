# Development Commands Cheatsheet

## Daily Workflow

```bash
# Start project
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop project
docker-compose down
```

## When You Change Database Models

```bash
# 1. Edit your model file (e.g., app/db/models/dream.py)

# 2. Generate migration (Alembic auto-detects changes)
docker-compose exec app alembic revision --autogenerate -m "describe change"

# 3. Restart to apply migration (auto-runs on boot)
docker-compose restart app
```

## Database Access

```bash
# Access PostgreSQL shell
docker exec -it dreamscape-postgres psql -U dreamscape -d dreamscape

# Inside psql:
SELECT * FROM dreams;           # View dreams table
\dt                             # List all tables
\d dreams                       # Describe dreams table
\q                              # Quit
```

## Testing API

```bash
# Open interactive docs (recommended)
http://localhost:8000/docs

# Or use curl
curl -X POST http://localhost:8000/api/v1/dreams \
  -H "Content-Type: application/json" \
  -d '{"content": "My dream text"}'

curl http://localhost:8000/api/v1/dreams
```

## Migration Commands

```bash
# View migration history
docker-compose exec app alembic history

# Check current version
docker-compose exec app alembic current

# Rollback one migration
docker-compose exec app alembic downgrade -1

# Apply migrations manually
docker-compose exec app alembic upgrade head
```

## Docker Commands

```bash
# Restart just the app
docker-compose restart app

# Rebuild after changing dependencies
docker-compose up -d --build

# View all container status
docker-compose ps

# Stop and DELETE database (⚠️ destroys data)
docker-compose down -v
```

## Troubleshooting

```bash
# Container won't start
docker-compose logs postgres    # Check database logs
docker-compose ps               # Check health status

# Port already in use
lsof -ti:8000                   # Find what's using port
kill -9 $(lsof -ti:8000)        # Kill the process

# Module not found
docker-compose up -d --build    # Rebuild containers
```

## What Files Do What

| File | Purpose |
|------|---------|
| `app/db/models/*.py` | Database table definitions |
| `alembic/versions/*.py` | Migration files (auto-generated) |
| `app/schemas/*.py` | API request/response validation |
| `app/services/*.py` | Business logic |
| `app/api/v1/*.py` | API endpoints |
| `docker-compose.yml` | Full stack setup |

## Setup Explanation

**What `docker-compose up -d` starts:**
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- FastAPI app (port 8000)
- Auto-runs migrations on boot

**Where your code runs:**
- Everything in Docker containers
- Code changes auto-reload (hot reload enabled)
- Migrations apply automatically when you restart
