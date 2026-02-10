from __future__ import annotations
import os
from pydantic import BaseModel, Field

class Settings(BaseModel):
    db_url: str = Field(default_factory=lambda: os.getenv("LEDGER_DB_URL", "postgresql://ledger:ledger@localhost:5433/ledger"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8080")))
    worker_poll_seconds: float = Field(default_factory=lambda: float(os.getenv("WORKER_POLL_SECONDS", "2")))

settings = Settings()
