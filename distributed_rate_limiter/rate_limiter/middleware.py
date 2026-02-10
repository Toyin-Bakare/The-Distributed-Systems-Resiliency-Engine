from __future__ import annotations
from typing import Callable, Optional
from time import perf_counter

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from rate_limiter.config import RateLimitPolicy
from rate_limiter.keys import pick_identity_key
from rate_limiter.token_bucket import TokenBucketLimiter
from rate_limiter.metrics import rl_allowed, rl_blocked, rl_latency

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        limiter: TokenBucketLimiter,
        policy: RateLimitPolicy,
        *,
        api_key_header: str = "x-api-key",
        user_id_header: str = "x-user-id",
        exempt_paths: Optional[set[str]] = None,
        dimension_label: str = "default",
    ):
        super().__init__(app)
        self.limiter = limiter
        self.policy = policy
        self.api_key_header = api_key_header.lower()
        self.user_id_header = user_id_header.lower()
        self.exempt_paths = exempt_paths or {"/health", "/metrics"}
        self.dimension_label = dimension_label

    async def dispatch(self, request: Request, call_next: Callable):
        if request.url.path in self.exempt_paths:
            return await call_next(request)

        api_key = request.headers.get(self.api_key_header)
        user_id = request.headers.get(self.user_id_header)
        forwarded = request.headers.get("x-forwarded-for")
        ip = (forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown"))

        redis_key = pick_identity_key(self.policy.prefix, api_key=api_key, user_id=user_id, ip=ip)

        t0 = perf_counter()
        decision = self.limiter.check(redis_key)
        rl_latency.labels(self.dimension_label).observe(perf_counter() - t0)

        headers = {
            "X-RateLimit-Limit": str(self.policy.burst),
            "X-RateLimit-Remaining": str(max(0, int(decision.remaining))),
        }

        if decision.allowed:
            rl_allowed.labels(self.dimension_label).inc()
            resp: Response = await call_next(request)
            for k, v in headers.items():
                resp.headers[k] = v
            return resp

        rl_blocked.labels(self.dimension_label).inc()
        retry_after_s = max(1, int((decision.retry_after_ms + 999) / 1000))
        headers["Retry-After"] = str(retry_after_s)
        return JSONResponse(
            status_code=429,
            content={"error": "rate_limited", "retry_after_seconds": retry_after_s},
            headers=headers,
        )
