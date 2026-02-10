from __future__ import annotations
from typing import Any, Dict, List, Tuple
from psycopg2.extras import RealDictCursor

from ledger.idempotency import request_hash, begin_idempotent, complete_idempotency
from ledger.outbox import insert_event

def create_account(conn, name: str, type_: str, currency: str) -> dict:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO account(name, type, currency) VALUES (%s, %s, %s) RETURNING account_id, name, type, currency",
            (name, type_, currency),
        )
        acct = cur.fetchone()
        cur.execute(
            "INSERT INTO account_balance(account_id, balance_cents) VALUES (%s, 0) ON CONFLICT (account_id) DO NOTHING",
            (acct["account_id"],),
        )
        return {k: str(v) for k, v in acct.items()}

def get_balance(conn, account_id: str) -> dict:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """SELECT a.account_id, a.currency, b.balance_cents
               FROM account a JOIN account_balance b ON b.account_id=a.account_id
               WHERE a.account_id=%s""",
            (account_id,),
        )
        row = cur.fetchone()
        if not row:
            raise KeyError("ACCOUNT_NOT_FOUND")
        row["account_id"] = str(row["account_id"])
        return row

def _apply_balance_updates(cur, updates: List[Tuple[str, int]]):
    for account_id, delta in updates:
        cur.execute(
            """INSERT INTO account_balance(account_id, balance_cents)
               VALUES (%s, %s)
               ON CONFLICT (account_id) DO UPDATE
                 SET balance_cents = account_balance.balance_cents + EXCLUDED.balance_cents,
                     updated_at = now()""",
            (account_id, delta),
        )

def transfer(conn, *, idempotency_key: str, from_account_id: str, to_account_id: str,
             amount_cents: int, currency: str, external_ref: str | None) -> dict:
    payload = {
        "from_account_id": from_account_id,
        "to_account_id": to_account_id,
        "amount_cents": amount_cents,
        "currency": currency,
        "external_ref": external_ref,
    }
    rh = request_hash(payload)

    status, cached = begin_idempotent(conn, idempotency_key, rh)
    if status == "COMPLETED":
        return cached
    if status == "IN_PROGRESS":
        raise RuntimeError("IDEMPOTENCY_IN_PROGRESS")

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT account_id, currency FROM account WHERE account_id=%s", (from_account_id,))
        fa = cur.fetchone()
        cur.execute("SELECT account_id, currency FROM account WHERE account_id=%s", (to_account_id,))
        ta = cur.fetchone()
        if not fa or not ta:
            raise KeyError("ACCOUNT_NOT_FOUND")
        if fa["currency"] != currency or ta["currency"] != currency:
            raise ValueError("CURRENCY_MISMATCH")

        cur.execute(
            "INSERT INTO ledger_transaction(txn_type, currency, external_ref) VALUES ('TRANSFER', %s, %s) "
            "RETURNING txn_id, txn_type, currency, external_ref",
            (currency, external_ref),
        )
        txn = cur.fetchone()

        cur.execute("INSERT INTO ledger_entry(txn_id, account_id, amount_cents) VALUES (%s, %s, %s)",
                    (txn["txn_id"], from_account_id, -amount_cents))
        cur.execute("INSERT INTO ledger_entry(txn_id, account_id, amount_cents) VALUES (%s, %s, %s)",
                    (txn["txn_id"], to_account_id, amount_cents))

        _apply_balance_updates(cur, [(from_account_id, -amount_cents), (to_account_id, amount_cents)])

        cur.execute("SELECT entry_id, account_id, amount_cents FROM ledger_entry WHERE txn_id=%s ORDER BY created_at",
                    (txn["txn_id"],))
        entries = cur.fetchall()

        resp = {
            "txn_id": str(txn["txn_id"]),
            "txn_type": txn["txn_type"],
            "currency": txn["currency"],
            "external_ref": txn["external_ref"],
            "entries": [{"entry_id": str(e["entry_id"]), "account_id": str(e["account_id"]), "amount_cents": int(e["amount_cents"])} for e in entries],
        }

        insert_event(conn, "ledger.transaction_posted", {"txn_id": resp["txn_id"], "type": resp["txn_type"], "currency": resp["currency"]})
        complete_idempotency(conn, idempotency_key, resp)

        return resp
