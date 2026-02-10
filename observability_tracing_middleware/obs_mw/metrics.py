from __future__ import annotations
from prometheus_client import Counter, Histogram

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "route", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "route"],
)

http_exceptions_total = Counter(
    "http_exceptions_total",
    "Unhandled exceptions",
    ["route"],
)
