from __future__ import annotations
import os
from typing import Optional
from opentelemetry import trace, propagate
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

SERVICE_NAME_ENV = "SERVICE_NAME"
OTLP_ENDPOINT_ENV = "OTEL_EXPORTER_OTLP_ENDPOINT"

def init_tracing(service_name: str | None = None, otlp_endpoint: str | None = None) -> None:
    service_name = service_name or os.getenv(SERVICE_NAME_ENV, "demo-api")
    otlp_endpoint = otlp_endpoint or os.getenv(OTLP_ENDPOINT_ENV, "http://otel-collector:4318")

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint}/v1/traces")
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

def get_tracer(name: str = "obs-mw"):
    return trace.get_tracer(name)

def extract_context_from_headers(headers: dict) -> None:
    # uses global propagator (W3C TraceContext by default)
    return propagate.extract(headers)

def inject_context_to_headers(headers: dict) -> None:
    propagate.inject(headers)
