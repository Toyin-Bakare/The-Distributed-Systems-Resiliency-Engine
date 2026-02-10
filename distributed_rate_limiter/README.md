# Distributed Rate Limiter 
(Redis + Lua) — Token Bucket + API Middleware

A **distributed rate limiting** reference implementation designed for real-world API gateways and microservices.
It provides **consistent enforcement across multiple instances** (pods/VMs) by storing counters/state in **Redis** and using
**Lua scripts** for atomic, low-latency decisions.

This repo includes:
- A production-style **rate limiter library** with Redis + Lua token bucket logic
- A **FastAPI demo service** showing how to enforce limits per user / API key / IP
- A **load generator** to validate throttling behavior under concurrency
- Docker Compose for a clean local demo

---

## Problem Statement

Rate limiting protects services from abuse and keeps multi-tenant platforms stable. It’s used for:

- preventing API abuse / credential stuffing
- isolating noisy neighbors in multi-tenant systems
- protecting downstream dependencies (databases, 3rd-party APIs)
- enforcing pricing tiers (Free vs Pro vs Enterprise)
- reducing blast radius during incidents (brownout protection)

### Why "distributed" is hard

A naive in-memory limiter works only for a single process. In real deployments you have many instances behind a load balancer.
You need:

- **global consistency** across instances
- **atomicity** (no race conditions under high concurrency)
- **low latency** (rate limiting sits on the hot path)
- predictable bursting behavior
- **observability** (allowed/blocked counts, latency)

This repo solves those requirements by using **Redis** as shared state and **Lua** for atomic token bucket operations.

---

## Solution Overview

### Algorithm: Token Bucket

Token bucket allows controlled bursts while maintaining an average rate:

- Bucket has capacity `burst`
- Tokens refill at `rate_per_sec` tokens/sec
- Each request consumes `cost` tokens (usually 1)
- Request is allowed if enough tokens exist; otherwise blocked

The limiter returns:
- allowed/blocked
- remaining tokens
- retry-after (ms / s)

### Key implementation choices

- **Lua script for atomicity**: read + compute + write in one Redis round-trip
- **Per-key state**: `apikey:{key}`, `user:{id}`, `ip:{addr}` (configurable)
- **TTL eviction**: inactive keys expire to avoid Redis memory blow-up
- **FastAPI middleware**: drop-in for services

---

## Repository Structure (How each file solves the problem)

### Infrastructure
- `docker-compose.yml` — runs Redis + demo API
- `Dockerfile` — containerizes the demo API
- `requirements.txt` — deps

### Library (`rate_limiter/`)
- `config.py` — policy object (rate/burst/ttl/cost/prefix)
- `keys.py` — consistent identity key building (api key > user id > ip)
- `redis_client.py` — Redis client factory
- `scripts/token_bucket.lua` — atomic token bucket logic
- `token_bucket.py` — Python wrapper around Lua (handles NOSCRIPT reload)
- `middleware.py` — ASGI middleware that enforces the limiter and sets headers
- `metrics.py` — Prometheus counters/histograms

### Demo API (`demo_api/`)
- `app.py` — FastAPI service with `/v1/hello`, `/health`, `/metrics`

### Tools
- `tools/load_test.py` — async load generator to validate throttling

### Tests
- `tests/test_lua_token_bucket.py` — burst + refill behavior (requires local Redis)
- `tests/test_key_builders.py` — key formatting

---

## Quickstart

### 1) Start Redis + API
```bash
docker compose up --build
```

API: http://localhost:8080  
Metrics: http://localhost:8080/metrics

### 2) Try requests
```bash
curl -H "x-api-key: demo" http://localhost:8080/v1/hello
```

### 3) Run load test
```bash
python tools/load_test.py --url http://localhost:8080/v1/hello --api-key demo --concurrency 20 --seconds 10
```

---

## Rate-limit headers

- `X-RateLimit-Limit`: bucket capacity (burst)
- `X-RateLimit-Remaining`: tokens remaining (rounded)
- `Retry-After`: seconds until a token is available (when blocked)

---

## Project highlights

- Implemented a distributed token bucket rate limiter using Redis-backed shared state and atomic Lua scripts
- Built ASGI middleware enforcing per-API-key/user/IP quotas with standard 429 + retry-after semantics
- Added TTL-based key eviction and Prometheus metrics for decision latency and deny rates
- Shipped Docker Compose + async load generator + tests for reproducible validation
