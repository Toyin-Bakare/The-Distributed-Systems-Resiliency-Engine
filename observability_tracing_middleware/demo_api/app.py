from __future__ import annotations
import os
import random
import asyncio
from fastapi import FastAPI, Request, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import httpx

from obs_mw.tracing import init_tracing
from obs_mw.logging import init_logging, get_logger
from obs_mw.middleware import ObservabilityMiddleware

PORT = int(os.getenv("PORT", "8080"))
SERVICE_NAME = os.getenv("SERVICE_NAME", "demo-api")
OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318")

init_logging()
init_tracing(service_name=SERVICE_NAME, otlp_endpoint=OTLP_ENDPOINT)

log = get_logger("demo_api")

app = FastAPI(title="Observability Middleware Demo", version="1.0.0")
app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/v1/hello")
async def hello(request: Request):
    await asyncio.sleep(random.random() * 0.05)
    return {"message": "hello", "request_id": request.headers.get("x-request-id")}

@app.get("/v1/error")
async def error():
    # simulate a crash
    raise RuntimeError("simulated failure")

@app.get("/v1/downstream")
async def downstream():
    # demonstrate trace propagation to downstream calls (even if downstream is external)
    async with httpx.AsyncClient(timeout=2.5) as client:
        r = await client.get("https://httpbin.org/status/200")
        return {"status_code": r.status_code}

@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("demo_api.app:app", host="0.0.0.0", port=PORT, reload=False)
