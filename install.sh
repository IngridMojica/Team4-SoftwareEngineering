#!/usr/bin/env bash
set -euo pipefail

# -------------------------------
# Ensure Python 3 and venv exist
# -------------------------------
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 not found. Install it with: sudo apt update && sudo apt install -y python3 python3-venv python3-pip" >&2
  exit 1
fi

# -------------------------------
# Create and activate venv
# -------------------------------
python3 -m venv .venv
. .venv/bin/activate

# -------------------------------
# Upgrade pip and install deps
# -------------------------------
python -m pip install --upgrade pip

# Explicit deps
python -m pip install psycopg2-binary
python -m pip install pygame

# Optional: testing tools
python -m pip install pytest

# -------------------------------
# Set sane Postgres defaults
# (for VM test environment only)
# -------------------------------
export PGDATABASE=${PGDATABASE:-photon}
export PGUSER=${PGUSER:-student}
export PGHOST=${PGHOST:-127.0.0.1}
export PGPORT=${PGPORT:-5432}

# -------------------------------
# Verify database connection
# -------------------------------
python - << 'PY'
import psycopg2, os
try:
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
except Exception as e:
    print("Database test skipped or failed:", e)
PY

# -------------------------------
# Final message
# -------------------------------
echo "------------------------------------------------------"
echo "Environment ready."
echo "Activate later with: . .venv/bin/activate"
echo "Run project: python main.py"
echo "Run tests: pytest"