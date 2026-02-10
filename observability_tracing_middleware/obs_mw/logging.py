from __future__ import annotations
import logging
import os
from typing import Dict, Any, Iterable
from pythonjsonlogger import jsonlogger
from obs_mw.context import get_request_context

SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key"}

def redact_headers(headers: Dict[str, str]) -> Dict[str, str]:
    out = {}
    for k, v in headers.items():
        lk = k.lower()
        if lk in SENSITIVE_HEADERS:
            out[k] = "[REDACTED]"
        else:
            out[k] = v
    return out

class ContextEnricherFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        ctx = get_request_context()
        if ctx:
            record.request_id = ctx.request_id
            record.trace_id = ctx.trace_id
            record.span_id = ctx.span_id
        else:
            record.request_id = None
            record.trace_id = None
            record.span_id = None
        return True

def init_logging(level: str | None = None) -> None:
    level = level or os.getenv("LOG_LEVEL", "INFO")
    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler()
    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(trace_id)s %(span_id)s"
    formatter = jsonlogger.JsonFormatter(fmt)
    handler.setFormatter(formatter)
    handler.addFilter(ContextEnricherFilter())

    # replace existing handlers
    root.handlers = [handler]

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
