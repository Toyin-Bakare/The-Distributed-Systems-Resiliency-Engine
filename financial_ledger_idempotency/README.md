# Financial Ledger with Idempotency (Double-Entry + Outbox + Safe Retries)

A portfolio-ready **financial ledger service** that implements:
- **Double-entry accounting** (every transaction balances to zero)
- **Idempotency keys** to safely retry requests without double-charging
- **Outbox pattern** for reliable event publication after commit
- **Postgres** as the source of truth with constraints to prevent corruption
- **FastAPI** REST API + a lightweight worker to publish outbox events
- Tests that validate balance invariants and idempotency

---

## Quickstart

```bash
docker compose up --build
```

API: http://localhost:8080

---

## Key Endpoints

- `POST /v1/accounts`
- `GET /v1/accounts/{account_id}/balance`
- `POST /v1/transactions/transfer` (requires `Idempotency-Key` header)

---

## Repo Map (How files solve the problem)

- `sql/001_init.sql` — schema + constraints (deferred trigger enforces balanced transactions)
- `ledger/idempotency.py` — idempotency key storage + request hash validation
- `ledger/ledger_core.py` — double-entry transfer logic + balance cache update + outbox insert
- `ledger/outbox.py` + `ledger/worker.py` — poll + publish + mark-sent pattern
- `ledger/api.py` — FastAPI interface
- `tests/*` — invariants and retry safety

---

## Resume-ready highlights

- Implemented a **double-entry ledger** with strict balancing invariants enforced by DB constraints and service logic
- Added **idempotency-key handling** to support safe retries and prevent duplicate transfers
- Implemented an **outbox pattern** for reliable event publication after commits
