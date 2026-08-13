#!/usr/bin/env sh
set -e

echo "===== DATABASE CHECK ====="
python -c "from app.database import DATABASE_URL; print('DATABASE:', DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL)"
echo "===== RUNNING MIGRATIONS ====="

alembic upgrade head

echo "===== MIGRATIONS COMPLETE ====="
echo "===== STARTING SERVER ====="

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
