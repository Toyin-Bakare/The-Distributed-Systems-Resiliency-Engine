from __future__ import annotations
from prometheus_client import Counter, Histogram

rl_allowed = Counter("rate_limiter_allowed_total", "Allowed requests", ["dimension"])
rl_blocked = Counter("rate_limiter_blocked_total", "Blocked requests", ["dimension"])
rl_latency = Histogram("rate_limiter_decision_seconds", "Limiter decision latency (seconds)", ["dimension"])
