from __future__ import annotations
import json
from typing import Any, Dict, List
from psycopg2.extras import RealDictCursor

def insert_event(conn, event_type: str, payload: Dict[str, Any]) -> str:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO outbox_event(event_type, payload) VALUES (%s, %s) RETURNING event_id",
            (event_type, json.dumps(payload)),
        )
        return str(cur.fetchone()["event_id"])

def poll_unsent(conn, limit: int = 50) -> List[dict]:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """SELECT event_id, event_type, payload, created_at
               FROM outbox_event
               WHERE sent_at IS NULL
               ORDER BY created_at
               LIMIT %s
               FOR UPDATE SKIP LOCKED""",
            (limit,),
        )
        return cur.fetchall()

def mark_sent(conn, event_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute("UPDATE outbox_event SET sent_at=now() WHERE event_id=%s", (event_id,))
