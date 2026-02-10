from __future__ import annotations
from typing import Callable, Optional
from time import perf_counter
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from opentelemetry import trace
from opentelemetry.propagate import extract, inject

from obs_mw.context import set_request_context
from obs_mw.metrics import http_requests_total, http_request_duration_seconds, http_exceptions_total
from obs_mw.logging import get_logger, redact_headers

log = get_logger("obs_mw.middleware")

def _hex_trace_id(span_ctx) -> str:
    return format(span_ctx.trace_id, "032x")

def _hex_span_id(span_ctx) -> str:
    return format(span_ctx.span_id, "016x")

class ObservabilityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, service_name: str = "demo-api", expose_request_headers: bool = False):
        super().__init__(app)
        self.service_name = service_name
        self.expose_request_headers = expose_request_headers
        self.tracer = trace.get_tracer("obs_mw")

    async def dispatch(self, request: Request, call_next: Callable):
        start = perf_counter()
        request_id = request.headers.get("x-request-id") or str(uuid4())

        # Extract incoming trace context
        carrier = dict(request.headers)
        ctx = extract(carrier)

        route = request.url.path  # fallback; for templated routes, use request.scope["route"].path if available
        method = request.method

        with self.tracer.start_as_current_span(f"{method} {route}", context=ctx) as span:
            span_ctx = span.get_span_context()
            trace_id = _hex_trace_id(span_ctx)
            span_id = _hex_span_id(span_ctx)
            set_request_context(request_id=request_id, trace_id=trace_id, span_id=span_id)

            # Add useful attributes
            span.set_attribute("http.method", method)
            span.set_attribute("http.route", route)
            span.set_attribute("http.target", str(request.url))
            span.set_attribute("request.id", request_id)

            try:
                response: Response = await call_next(request)
                status = response.status_code
            except Exception as e:
                http_exceptions_total.labels(route=route).inc()
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR))  # type: ignore[attr-defined]
                status = 500
                response = JSONResponse(status_code=500, content={"error": "internal_error", "request_id": request_id})

            duration = perf_counter() - start

            http_requests_total.labels(method=method, route=route, status=str(status)).inc()
            http_request_duration_seconds.labels(method=method, route=route).observe(duration)

            span.set_attribute("http.status_code", status)
            span.set_attribute("http.server_duration_ms", int(duration * 1000))

            # Log one line per request (JSON)
            payload = {
                "event": "request_complete",
                "request_id": request_id,
                "method": method,
                "route": route,
                "status": status,
                "duration_ms": int(duration * 1000),
            }
            if self.expose_request_headers:
                payload["headers"] = redact_headers(dict(request.headers))
            log.info("request", extra=payload)

            # propagate context on response
            response.headers["x-request-id"] = request_id
            response.headers["x-trace-id"] = trace_id
            response.headers["x-span-id"] = span_id

            # also inject W3C trace context for clients that forward it
            inject_carrier = {}
            inject(inject_carrier)
            # these standard headers are lower-case in python dict, but Starlette normalizes anyway
            for k, v in inject_carrier.items():
                response.headers[k] = v

            return response
