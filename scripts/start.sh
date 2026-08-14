#!/usr/bin/env sh
set -eux

echo "=== DATABASE CHECK ==="
echo "DATABASE_URL is set: ${DATABASE_URL:+YES}"
echo "=== RUNNING MIGRATIONS ==="

alembic current
alembic upgrade head
alembic current

echo "=== STARTING FASTAPI ==="

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
