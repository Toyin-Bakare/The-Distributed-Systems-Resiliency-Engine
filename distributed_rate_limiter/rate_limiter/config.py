from __future__ import annotations
from pydantic import BaseModel, Field

class RateLimitPolicy(BaseModel):
    """Token bucket policy."""
    rate_per_sec: float = Field(..., gt=0)
    burst: int = Field(..., ge=1)
    ttl_seconds: int = Field(default=3600, ge=10)
    cost: int = Field(default=1, ge=1)
    prefix: str = Field(default="rl:tb")
