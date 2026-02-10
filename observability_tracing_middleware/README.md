# Observability & Tracing Middleware 
(FastAPI + OpenTelemetry + Prometheus + Structured Logs)

A project that implements **drop-in observability middleware** for Python APIs:
- **Distributed tracing** with **OpenTelemetry** (W3C Trace Context propagation)
- **Metrics** with **Prometheus** (HTTP latency, request counts, error counts)
- **Structured logging** (JSON logs with trace/span IDs, request IDs, latency, status)
- **Redaction** of sensitive headers and PII-safe logging defaults
- A **demo FastAPI service** instrumented with the middleware
- Docker Compose that runs:
  - demo API
  - OpenTelemetry Collector
  - Jaeger (trace UI)
  - Prometheus + Grafana (metrics dashboards)

This mirrors what you’d build for a production platform team: consistent instrumentation across services.

---

## Problem Statement

In microservices and API platforms, incidents often look like:
- “Latency is up, but which service is the cause?”
- “Errors are spiking—what endpoints, what tenants, what upstream dependency?”
- “This request failed, but where in the distributed call graph did it happen?”
- “We have logs, but no correlation between logs and traces.”

When each team instruments differently, you get:
- inconsistent tags/labels
- missing trace context
- brittle dashboards
- inability to correlate logs ⇄ traces ⇄ metrics

**Goal:** Provide a reusable middleware that standardizes:
- request/response metrics
- trace propagation and span creation
- log correlation fields
- safe redaction rules

---

## High-Level Architecture

```
Client
  -> FastAPI (ObservabilityMiddleware)
      - create/continue trace span
      - inject trace_id/span_id into logs
      - record Prometheus metrics
      - export spans via OTLP
  -> OpenTelemetry Collector
  -> Jaeger (traces UI)

Prometheus scrapes /metrics
Grafana visualizes Prometheus metrics
```

---

## Repository Structure (How each file solves the problem)

### Middleware library (`obs_mw/`)
- `context.py`
  - request-scoped context and log correlation helpers
- `logging.py`
  - JSON logger + redaction filters + trace/span enrichment
- `tracing.py`
  - OpenTelemetry setup + span creation + context propagation
- `metrics.py`
  - Prometheus metrics definitions (counters, histograms)
- `middleware.py`
  - FastAPI/ASGI middleware:
    - starts spans
    - measures latency
    - records metrics
    - logs request summary
    - returns request id and trace context headers

### Demo API (`demo_api/`)
- `app.py`
  - endpoints that simulate:
    - normal traffic
    - errors
    - downstream calls (HTTP client) to show trace propagation

### Observability stack (`infra/`)
- `docker-compose.yml`
  - API + otel-collector + jaeger + prometheus + grafana
- `otel-collector-config.yml`
  - receives OTLP spans and exports to Jaeger
  - exposes Prometheus scrape endpoint if desired
- `prometheus.yml`
  - scrapes the API’s `/metrics`
- `grafana/`
  - provisioning for a basic Prometheus datasource + dashboard

### Tools
- `tools/loadgen.py`
  - simple load generator to create traces and metrics quickly

---

## Quickstart

### 1) Run the full stack
```bash
docker compose -f infra/docker-compose.yml up --build
```

### 2) Try it
- API: http://localhost:8080
- Metrics: http://localhost:8080/metrics
- Jaeger: http://localhost:16686
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000  (default login: admin / admin)

### 3) Generate traffic
```bash
python tools/loadgen.py --base-url http://localhost:8080 --seconds 15 --concurrency 10
```

---

## What to look for

- In Jaeger, search for service `demo-api` and open traces.
- In Prometheus/Grafana, observe:
  - request rate
  - p50/p95 latency
  - error counts per route

---

## Project highlights

- Built reusable observability middleware: OpenTelemetry tracing + Prometheus metrics + JSON structured logging
- Implemented W3C trace context propagation and log correlation (trace_id/span_id/request_id)
- Added safe redaction for sensitive headers and default PII-safe logging practices
- Shipped dockerized observability stack (OTel Collector, Jaeger, Prometheus, Grafana) + load generator for demos
