from __future__ import annotations
import json, time
from ledger.config import settings
from ledger.db import get_conn, migrate
from ledger.outbox import poll_unsent, mark_sent

def publish(event: dict) -> None:
    print(json.dumps({"published_event": event}, default=str))

def main():
    migrate(sql_dir="sql")
    while True:
        with get_conn() as conn:
            events = poll_unsent(conn, limit=25)
            for e in events:
                publish(e)
                mark_sent(conn, str(e["event_id"]))
            conn.commit()
        time.sleep(settings.worker_poll_seconds)

if __name__ == "__main__":
    main()
