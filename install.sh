#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------
# Laser Tag – Sprint 3 installer (Debian-ready)
# - Creates .venv
# - Installs pygame + psycopg2-binary
# - Optional PostgreSQL connectivity test (prompts password)
# ---------------------------------------------

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$project_root"

echo "==> Checking Python 3 ..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 not found."
  echo "On Debian/Ubuntu: sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
  exit 1
fi

# Helpful system packages for psycopg2 on Debian/Ubuntu
if command -v apt-get >/dev/null 2>&1; then
  echo "==> Installing system packages needed for psycopg2 (safe to re-run)"
  sudo apt-get update -y
  sudo apt-get install -y --no-install-recommends \
    python3-venv python3-pip libpq-dev libssl-dev build-essential
fi

# Create & activate venv
if [[ ! -d .venv ]]; then
  echo "==> Creating virtual environment: .venv"
  python3 -m venv .venv
fi

echo "==> Activating .venv"
# shellcheck disable=SC1091
source .venv/bin/activate

# Upgrade pip and install deps
echo "==> Upgrading pip"
python -m pip install --upgrade pip

echo "==> Installing Python dependencies"
if [[ -f requirements.txt ]]; then
  python -m pip install -r requirements.txt
else
  python -m pip install pygame psycopg2-binary
fi

# Default Postgres env (no password here)
export PGHOST="${PGHOST:-127.0.0.1}"
export PGPORT="${PGPORT:-5432}"
export PGUSER="${PGUSER:-student}"
export PGDATABASE="${PGDATABASE:-photon}"

# Optional: DB connectivity test (prompts for password, does not store it)
read -p "Would you like to test the PostgreSQL connection now? (y/n): " TEST_DB
if [[ "$TEST_DB" =~ ^[Yy]$ ]]; then
  read -s -p "Enter PostgreSQL password for user '${PGUSER}': " PGPASSWORD_INPUT
  echo ""
  export PGPASSWORD="$PGPASSWORD_INPUT"

  echo "==> Testing database connection..."
  python - <<'PY'
import os
try:
    import psycopg2
    print("psycopg2 OK; attempting connection…")
    conn = psycopg2.connect(
        dbname=os.getenv("PGDATABASE","photon"),
        user=os.getenv("PGUSER","student"),
        password=os.getenv("PGPASSWORD"),
        host=os.getenv("PGHOST","127.0.0.1"),
        port=int(os.getenv("PGPORT","5432")),
        connect_timeout=3,
    )
    with conn.cursor() as cur:
        cur.execute("SELECT 1;")
        print("DB test OK:", cur.fetchone())
    conn.close()
except Exception as e:
    print("Database test failed:", e)
PY
else
  echo "Skipping database connectivity test."
fi

cat <<'TXT'

------------------------------------------------------------
✅ Environment ready.

To activate later:
  source .venv/bin/activate

Run the game:
  python main.py
  # (or: python src/main.py if your entry lives under src/)

Notes:
- We do NOT store any DB password; if you test the DB, you'll be prompted.
- If psycopg2 gives build errors on Windows, use the VM (this script works there).
------------------------------------------------------------
TXT