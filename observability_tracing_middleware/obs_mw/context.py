from __future__ import annotations
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional

request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)
span_id_var: ContextVar[Optional[str]] = ContextVar("span_id", default=None)

@dataclass
class RequestContext:
    request_id: str
    trace_id: str
    span_id: str

def set_request_context(request_id: str, trace_id: str, span_id: str) -> None:
    request_id_var.set(request_id)
    trace_id_var.set(trace_id)
    span_id_var.set(span_id)

def get_request_context() -> Optional[RequestContext]:
    rid = request_id_var.get()
    tid = trace_id_var.get()
    sid = span_id_var.get()
    if rid and tid and sid:
        return RequestContext(request_id=rid, trace_id=tid, span_id=sid)
    return None
