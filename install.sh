#!/usr/bin/env bash
set -euo pipefail

# Ensure Python 3 and venv exist
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 not found. Install it with: sudo apt update && sudo apt install -y python3 python3-venv python3-pip" >&2
  exit 1
fi

# Create and activate venv
python3 -m venv .venv
. .venv/bin/activate

# Upgrade pip and install deps
python -m pip install --upgrade pip
python -m pip install psycopg2-binary

# Set sane Postgres defaults for the VM (not permanent; for this shell only)
export PGDATABASE=${PGDATABASE:-photon}
export PGUSER=${PGUSER:-student}
export PGHOST=${PGHOST:-127.0.0.1}
export PGPORT=${PGPORT:-5432}

# Quick verification for database portion of install
python - << 'PY'
import psycopg2, os
print("psycopg2 OK; connecting...")
conn = psycopg2.connect(
    dbname=os.getenv("PGDATABASE","photon"),
    user=os.getenv("PGUSER","student"),
    host=os.getenv("PGHOST","127.0.0.1"),
    port=int(os.getenv("PGPORT","5432")),
)
cur = conn.cursor()
cur.execute("SELECT 1;")
print("DB test OK:", cur.fetchone())
cur.close(); conn.close()
PY

echo "Environment ready. To use it later: . .venv/bin/activate"
echo "Run tests: python test_players.py"
