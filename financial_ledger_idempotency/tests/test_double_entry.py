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

def test_transfer_balances_to_zero(conn):
    a1 = create_account(conn, "A1", "ASSET", "USD")
    a2 = create_account(conn, "A2", "ASSET", "USD")
    conn.commit()

    resp = transfer(conn, idempotency_key=str(uuid.uuid4()), from_account_id=a1["account_id"], to_account_id=a2["account_id"],
                    amount_cents=1234, currency="USD", external_ref="t1")
    conn.commit()

    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(amount_cents),0) FROM ledger_entry WHERE txn_id=%s", (resp["txn_id"],))
        s = cur.fetchone()[0]
    assert int(s) == 0
