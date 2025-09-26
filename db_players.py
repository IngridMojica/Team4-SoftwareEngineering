import psycopg2
from typing import Optional

connection_params = {
    "dbname": "photon",
    "user": "student",
    # "password": "student",
    # "host": "127.0.0.1",
    # "port": "5432",
}

def get_codename(player_id: int) -> Optional[str]:
    conn = cur = None
    try:
        conn = psycopg2.connect(**connection_params)
        cur = conn.cursor()
        cur.execute("SELECT codename FROM players WHERE id = %s;", (player_id,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        if cur: cur.close()
        if conn: conn.close()

def add_player(player_id: int, codename: str) -> bool:
    conn = cur = None
    try:
        conn = psycopg2.connect(**connection_params)
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM players WHERE id = %s;", (player_id,))
        if cur.fetchone():
            return False
        cur.execute("INSERT INTO players (id, codename) VALUES (%s, %s);", (player_id, codename))
        conn.commit()
        return True
    finally:
        if cur: cur.close()
        if conn: conn.close()
