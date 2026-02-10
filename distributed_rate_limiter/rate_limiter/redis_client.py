from __future__ import annotations
import os
import redis

def get_redis(url: str | None = None) -> redis.Redis:
    url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.Redis.from_url(
        url,
        decode_responses=False,
        socket_timeout=2.0,
        socket_connect_timeout=2.0,
        health_check_interval=10,
    )
