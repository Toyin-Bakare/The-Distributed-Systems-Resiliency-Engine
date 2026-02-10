import os, uuid
import pytest
from ledger.db import get_conn, migrate
from ledger.ledger_core import create_account, transfer
from ledger.outbox import poll_unsent, mark_sent

@pytest.fixture(scope="module")
def conn():
    db_url = os.getenv("LEDGER_TEST_DB_URL", "postgresql://ledger:ledger@localhost:5433/ledger")
    c = get_conn(db_url)
    migrate(sql_dir="sql")
    yield c
    c.close()

def test_outbox_event_created_and_marked_sent(conn):
    a1 = create_account(conn, "A1", "ASSET", "USD")
    a2 = create_account(conn, "A2", "ASSET", "USD")
    conn.commit()

    transfer(conn, idempotency_key=str(uuid.uuid4()), from_account_id=a1["account_id"], to_account_id=a2["account_id"],
             amount_cents=10, currency="USD", external_ref="o")
    conn.commit()

    events = poll_unsent(conn, limit=10)
    assert len(events) >= 1
    eid = str(events[0]["event_id"])
    mark_sent(conn, eid)
    conn.commit()

    events2 = poll_unsent(conn, limit=10)
    assert all(str(e["event_id"]) != eid for e in events2)
