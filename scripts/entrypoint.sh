#!/bin/sh
set -e

python - <<'PY'
import os
import time

import psycopg

dsn = {
    "dbname": os.environ.get("POSTGRES_DB", "secundaria_db"),
    "user": os.environ.get("POSTGRES_USER", "secundaria_user"),
    "password": os.environ.get("POSTGRES_PASSWORD", "secundaria_password"),
    "host": os.environ.get("POSTGRES_HOST", "db"),
    "port": os.environ.get("POSTGRES_PORT", "5432"),
}

for attempt in range(30):
    try:
        with psycopg.connect(**dsn):
            break
    except psycopg.OperationalError:
        if attempt == 29:
            raise
        time.sleep(1)
PY

python manage.py migrate --noinput
python manage.py createsuperuser --noinput || true
python manage.py seed_demo || true

exec "$@"
