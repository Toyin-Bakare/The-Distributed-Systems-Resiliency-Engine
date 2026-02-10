import asyncio
import pytest
import redis
from rate_limiter.config import RateLimitPolicy
from rate_limiter.token_bucket import TokenBucketLimiter

@pytest.mark.asyncio
async def test_token_bucket_burst_and_refill():
    r = redis.Redis.from_url("redis://localhost:6379/0", decode_responses=False)
    policy = RateLimitPolicy(rate_per_sec=5.0, burst=5, ttl_seconds=60, cost=1, prefix="test:tb")
    limiter = TokenBucketLimiter(r, policy)

    key = "test:tb:apikey:demo"
    r.delete(key)

    allowed = 0
    blocked = 0
    for _ in range(7):
        d = limiter.check(key)
        allowed += 1 if d.allowed else 0
        blocked += 0 if d.allowed else 1

    assert allowed == 5
    assert blocked == 2

    await asyncio.sleep(0.25)
    d2 = limiter.check(key)
    assert d2.allowed is True
