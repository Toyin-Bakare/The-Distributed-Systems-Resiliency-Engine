from __future__ import annotations
from fastapi import FastAPI, Header, HTTPException
import psycopg2

from ledger.config import settings
from ledger.db import get_conn, migrate
from ledger.models import CreateAccountRequest, AccountResponse, BalanceResponse, TransferRequest, TransactionResponse
from ledger.ledger_core import create_account, get_balance, transfer

app = FastAPI(title="Financial Ledger with Idempotency", version="1.0.0")

@app.on_event("startup")
def _startup():
    migrate(sql_dir="sql")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/v1/accounts", response_model=AccountResponse)
def create_account_route(req: CreateAccountRequest):
    with get_conn() as conn:
        try:
            acct = create_account(conn, req.name, req.type, req.currency)
            conn.commit()
            return acct
        except Exception:
            conn.rollback()
            raise

@app.get("/v1/accounts/{account_id}/balance", response_model=BalanceResponse)
def balance_route(account_id: str):
    with get_conn() as conn:
        try:
            row = get_balance(conn, account_id)
            return {"account_id": row["account_id"], "currency": row["currency"], "balance_cents": int(row["balance_cents"])}
        except KeyError:
            raise HTTPException(status_code=404, detail="account_not_found")

@app.post("/v1/transactions/transfer", response_model=TransactionResponse)
def transfer_route(req: TransferRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="missing_idempotency_key")
    with get_conn() as conn:
        try:
            resp = transfer(
                conn,
                idempotency_key=idempotency_key,
                from_account_id=req.from_account_id,
                to_account_id=req.to_account_id,
                amount_cents=req.amount_cents,
                currency=req.currency,
                external_ref=req.external_ref,
            )
            conn.commit()
            return resp
        except ValueError as e:
            conn.rollback()
            if str(e) == "IDEMPOTENCY_KEY_CONFLICT":
                raise HTTPException(status_code=409, detail="idempotency_key_conflict")
            if str(e) == "CURRENCY_MISMATCH":
                raise HTTPException(status_code=400, detail="currency_mismatch")
            raise HTTPException(status_code=400, detail="bad_request")
        except KeyError:
            conn.rollback()
            raise HTTPException(status_code=404, detail="account_not_found")
        except RuntimeError as e:
            conn.rollback()
            if str(e) == "IDEMPOTENCY_IN_PROGRESS":
                raise HTTPException(status_code=409, detail="idempotency_in_progress")
            raise HTTPException(status_code=500, detail="internal_error")
        except psycopg2.Error:
            conn.rollback()
            raise HTTPException(status_code=400, detail="db_constraint_violation")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ledger.api:app", host="0.0.0.0", port=settings.port, reload=False)
