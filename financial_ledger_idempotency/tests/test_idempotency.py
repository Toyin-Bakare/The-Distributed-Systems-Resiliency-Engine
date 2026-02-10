import os, uuid
import pytest
from ledger.db import get_conn, migrate
from ledger.ledger_core import create_account, transfer

@pytest.fixture(scope="module")
def conn():
    db_url = os.getenv("LEDGER_TEST_DB_URL", "postgresql://ledger:ledger@localhost:5433/ledger")
    c = get_conn(db_url)
    migrate(sql_dir="sql")
    yield c
    c.close()

def test_idempotent_retry_returns_same_response(conn):
    a1 = create_account(conn, "Cash", "ASSET", "USD")
    a2 = create_account(conn, "Wallet", "LIABILITY", "USD")
    conn.commit()

    idem = str(uuid.uuid4())
    r1 = transfer(conn, idempotency_key=idem, from_account_id=a1["account_id"], to_account_id=a2["account_id"],
                 amount_cents=500, currency="USD", external_ref="order-1")
    conn.commit()

    r2 = transfer(conn, idempotency_key=idem, from_account_id=a1["account_id"], to_account_id=a2["account_id"],
                 amount_cents=500, currency="USD", external_ref="order-1")
    conn.commit()

    assert r1["txn_id"] == r2["txn_id"]
    assert r1["entries"] == r2["entries"]

def test_idempotency_key_conflict(conn):
    a1 = create_account(conn, "Src", "ASSET", "USD")
    a2 = create_account(conn, "Dst", "ASSET", "USD")
    conn.commit()

    idem = str(uuid.uuid4())
    transfer(conn, idempotency_key=idem, from_account_id=a1["account_id"], to_account_id=a2["account_id"],
             amount_cents=100, currency="USD", external_ref="x")
    conn.commit()

    with pytest.raises(ValueError):
        transfer(conn, idempotency_key=idem, from_account_id=a1["account_id"], to_account_id=a2["account_id"],
                 amount_cents=999, currency="USD", external_ref="x")
