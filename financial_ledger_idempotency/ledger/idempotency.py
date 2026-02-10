from __future__ import annotations
import hashlib, json
from typing import Any, Dict, Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor

def request_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def begin_idempotent(conn, key: str, req_hash: str) -> Tuple[str, Optional[dict]]:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            cur.execute(
                "INSERT INTO idempotency_key(idempotency_key, request_hash, status) VALUES (%s, %s, 'IN_PROGRESS')",
                (key, req_hash),
            )
            return "NEW", None
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            cur.execute("SELECT * FROM idempotency_key WHERE idempotency_key=%s", (key,))
            row = cur.fetchone()
            if not row:
                return "NEW", None
            if row["request_hash"] != req_hash:
                raise ValueError("IDEMPOTENCY_KEY_CONFLICT")
            if row["status"] == "COMPLETED":
                return "COMPLETED", row["response_json"]
            return "IN_PROGRESS", None

def complete_idempotency(conn, key: str, response_json: dict) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE idempotency_key SET status='COMPLETED', response_json=%s, updated_at=now() WHERE idempotency_key=%s",
            (json.dumps(response_json), key),
        )
