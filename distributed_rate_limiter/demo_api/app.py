from __future__ import annotations
import os
from fastapi import FastAPI, Request, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from rate_limiter.config import RateLimitPolicy
from rate_limiter.redis_client import get_redis
from rate_limiter.token_bucket import TokenBucketLimiter
from rate_limiter.middleware import RateLimitMiddleware

PORT = int(os.getenv("PORT", "8080"))

rate = float(os.getenv("RL_RATE_PER_SEC", "5"))
burst = int(os.getenv("RL_BURST", "10"))

policy = RateLimitPolicy(rate_per_sec=rate, burst=burst, ttl_seconds=1800, cost=1, prefix="rl:tb")

app = FastAPI(title="Distributed Rate Limiter Demo", version="1.0.0")

r = get_redis(os.getenv("REDIS_URL"))
limiter = TokenBucketLimiter(r, policy)

app.add_middleware(RateLimitMiddleware, limiter=limiter, policy=policy, dimension_label="demo")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/v1/hello")
def hello(request: Request):
    return {"message": "hello", "client": request.client.host if request.client else "unknown"}

@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("demo_api.app:app", host="0.0.0.0", port=PORT, reload=False)
