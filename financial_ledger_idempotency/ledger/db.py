from __future__ import annotations
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from ledger.config import settings

def get_conn(db_url: str | None = None):
    return psycopg2.connect(db_url or settings.db_url)

def migrate(sql_dir: str = "sql"):
    sql_files = sorted([f for f in os.listdir(sql_dir) if f.endswith(".sql")])
    with get_conn() as conn:
        with conn.cursor() as cur:
            for f in sql_files:
                with open(os.path.join(sql_dir, f), "r", encoding="utf-8") as fh:
                    cur.execute(fh.read())
        conn.commit()

def fetch_one(sql: str, params=None):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params or ())
            return cur.fetchone()
