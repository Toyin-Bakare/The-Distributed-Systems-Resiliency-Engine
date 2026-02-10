# The-Distributed-Systems-Resiliency-Engine
---
Enterprise Resilience &amp; Middleware Patterns : A reference architecture for building multi-tenant, idempotent services that maintain high availability under extreme load. Includes custom middleware for observability and distributed traffic control.

### 1. GraphQL Wrapper for Legacy APIs 
**Tech:** Java/Spring Boot  

GraphQL gateway that aggregates data from three different "messy" REST APIs (e.g., Weather, Finnhub, and Twitter) into a clean, unified schema.

**Focus:** Implement dataloaders to solve the $N+1$ query problem and add a caching layer with Redis.

**Use Case:** "Abstract the nuances of raw data access" for other developers.

📁[`GraphQL Wrapper for Legacy APIs`](https://github.com/Toyin-Bakare/The-Distributed-Systems-Resiliency-Engine/tree/main/graphql_wrapper_legacy_apis)
***


### 2. Distributed Rate Limiter 
**Tech:** Java & Redis  

Standalone library or sidecar service that provides distributed rate limiting (Token Bucket or Leaky Bucket algorithms) for microservices.

**Focus:** ultra-low latency and handling "thundering herd" problems.

**Use Case:** For distributed systems and service-oriented architecture (SOA).

📁 [`Distributed Rate Limiter`](https://github.com/Toyin-Bakare/The-Distributed-Systems-Resiliency-Engine/tree/main/distributed_rate_limiter)
***

### 3. Observability & Tracing Middleware 
**Tech:** Kotlin & OpenTelemetry  
Middleware for an HTTP framework (like Ktor or Micronaut) that automatically injects trace IDs and exports metrics to a Prometheus/Grafana stack.

**Focus:** Developer experience (DX)—how easy is it for another engineer to drop this into their project

**Use Case:** "Technical Excellence" and "Operations."

📁 [`Observability & Tracing Middleware`](https://github.com/Toyin-Bakare/The-Distributed-Systems-Resiliency-Engine/tree/main/observability_tracing_middleware)
***

