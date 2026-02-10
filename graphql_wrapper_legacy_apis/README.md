# GraphQL Wrapper for Legacy APIs 
(Apollo Server + DataLoader + Caching + Auth)

A project that modernizes a legacy REST ecosystem by placing a **GraphQL façade** in front of existing services.

This repo includes:
- **Mock legacy REST API** (`legacy-api/`) simulating common pain points (N+1 calls, inconsistent payloads, latency).
- **GraphQL wrapper** (`graphql-wrapper/`) that:
  - exposes a clean GraphQL schema
  - batches/caches downstream calls via **DataLoader**
  - propagates auth headers
  - adds response caching + a Redis adapter stub
  - adds timeouts/retries for resiliency
  - emits request IDs for traceability

---

## Problem Statement

Legacy APIs often have:
- inconsistent naming/versions/payloads
- chatty clients (N+1 requests)
- clients doing business joins (customer + orders + order details)
- inconsistent security patterns and error handling

**Goal:** Provide a single interface for clients (web/mobile/agents) without rewriting legacy services.

GraphQL is useful because it:
- composes multiple backend calls into one query
- lets clients fetch exactly what they need
- centralizes auth, caching, error handling, and evolution

---

## Architecture

Clients → GraphQL Wrapper (Apollo) → Legacy REST APIs

---

## Repo Structure (How each file solves the problem)

### Legacy mock service (`legacy-api/`)
- `src/server.ts` — Express server with endpoints and artificial latency/inconsistency
- `src/data.ts` — in-memory dataset used by endpoints

### GraphQL wrapper (`graphql-wrapper/`)
- `src/schema.ts` — GraphQL schema (Customer, Order, Query)
- `src/context.ts` — per-request context (requestId, auth, loaders, API client, cache)
- `src/datasources/legacyClient.ts` — HTTP client with timeouts + retries + auth propagation
- `src/loaders/customerLoader.ts` — batches customer fetches via `/customers?ids=...`
- `src/loaders/orderLoader.ts` — request-scope caching for order detail calls
- `src/resolvers.ts` — composes legacy endpoints into GraphQL fields
- `src/cache.ts` — caching interface + in-memory cache + Redis stub
- `src/server.ts` — Apollo + Express wiring + requestId middleware
- `src/index.ts` — entrypoint

### DevOps
- `docker-compose.yml` — runs both services together
- `Makefile` — convenience commands

### Tests
- `graphql-wrapper/tests/graphql.test.ts` — integration test hitting GraphQL (expects legacy API running)

---

## Quickstart

### Run with Docker
```bash
docker compose up --build
```

- Legacy API: http://localhost:4001/health
- GraphQL: http://localhost:4000/graphql

---

## Example GraphQL Query

```graphql
query Demo {
  customer(id: "c-001") {
    id
    name
    email
    orders {
      id
      status
      total
      customer { id name }
    }
  }
}
```

What this demonstrates:
- The client makes **one** request.
- The wrapper fans out to legacy endpoints and reduces N+1 calls via DataLoader batching/caching.

---

## Project highlights
- Built a GraphQL façade over legacy REST services using Apollo Server + TypeScript
- Implemented DataLoader batching/caching to eliminate N+1 patterns
- Added auth propagation, timeouts/retries, and response caching to stabilize dependencies
- Shipped Docker Compose + integration tests for repeatable demos
