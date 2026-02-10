from __future__ import annotations
from dataclasses import dataclass
from time import time
import redis
from rate_limiter.config import RateLimitPolicy

@dataclass
class Decision:
    allowed: bool
    remaining: float
    retry_after_ms: int

class TokenBucketLimiter:
    """Redis-backed token bucket limiter using Lua for atomic decisions."""

    def __init__(self, r: redis.Redis, policy: RateLimitPolicy):
        self.r = r
        self.policy = policy
        self._script, self._sha = self._load_script()

    def _load_script(self):
        import pkgutil
        lua = pkgutil.get_data("rate_limiter", "scripts/token_bucket.lua")
        if lua is None:
            raise RuntimeError("Lua script not found")
        script = lua.decode("utf-8")
        sha = self.r.script_load(script)
        return script, sha

    def _now_ms(self) -> int:
        return int(time() * 1000)

    def check(self, key: str) -> Decision:
        args = [
            str(self._now_ms()),
            str(self.policy.rate_per_sec),
            str(self.policy.burst),
            str(self.policy.cost),
            str(self.policy.ttl_seconds),
        ]
        try:
            res = self.r.evalsha(self._sha, 1, key, *args)
        except redis.exceptions.NoScriptError:
            self._sha = self.r.script_load(self._script)
            res = self.r.evalsha(self._sha, 1, key, *args)

        return Decision(
            allowed=bool(int(res[0])),
            remaining=float(res[1]),
            retry_after_ms=int(res[2]),
        )
