-- Financial Ledger schema (Postgres)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS account (
  account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('ASSET','LIABILITY','REVENUE','EXPENSE')),
  currency TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ledger_transaction (
  txn_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  txn_type TEXT NOT NULL,
  currency TEXT NOT NULL,
  external_ref TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ledger_entry (
  entry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  txn_id UUID NOT NULL REFERENCES ledger_transaction(txn_id) ON DELETE CASCADE,
  account_id UUID NOT NULL REFERENCES account(account_id),
  amount_cents BIGINT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_entry_account ON ledger_entry(account_id);
CREATE INDEX IF NOT EXISTS idx_entry_txn ON ledger_entry(txn_id);

-- Deferred trigger enforces: SUM(entries.amount_cents) == 0 per txn at commit time.
CREATE OR REPLACE FUNCTION enforce_txn_balanced() RETURNS trigger AS $$
DECLARE
  s BIGINT;
BEGIN
  SELECT COALESCE(SUM(amount_cents),0) INTO s FROM ledger_entry WHERE txn_id = NEW.txn_id;
  IF s <> 0 THEN
    RAISE EXCEPTION 'Transaction % is not balanced (sum=%)', NEW.txn_id, s;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_enforce_txn_balanced ON ledger_entry;
CREATE CONSTRAINT TRIGGER trg_enforce_txn_balanced
AFTER INSERT OR UPDATE OR DELETE ON ledger_entry
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION enforce_txn_balanced();

CREATE TABLE IF NOT EXISTS account_balance (
  account_id UUID PRIMARY KEY REFERENCES account(account_id) ON DELETE CASCADE,
  balance_cents BIGINT NOT NULL DEFAULT 0,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS idempotency_key (
  idempotency_key TEXT PRIMARY KEY,
  request_hash TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('IN_PROGRESS','COMPLETED')),
  response_json JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS outbox_event (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  sent_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_outbox_unsent ON outbox_event(sent_at) WHERE sent_at IS NULL;
