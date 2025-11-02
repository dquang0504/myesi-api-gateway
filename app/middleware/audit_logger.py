# app/middleware/audit_logger.py
import time
import json
import logging
from fastapi import Request
from fastapi.background import BackgroundTasks
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.es_client import index_audit
from app.core.config import settings
from typing import Callable

logger = logging.getLogger("audit_middleware")
logger.setLevel(logging.INFO)

def _truncate_text(text: str | bytes | None, max_chars: int):
    if text is None:
        return None
    if isinstance(text, bytes):
        try:
            text = text.decode("utf-8", errors="replace")
        except Exception:
            return "<non-decodable>"
    if len(text) > max_chars:
        return text[:max_chars] + "...(truncated)"
    return text

class AuditLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware that captures request metadata and sends an audit document to Elasticsearch.
    - Reads request body safely and restores it for downstream handlers.
    - Uses BackgroundTasks to index docs so response is not blocked.
    """
    async def dispatch(self, request: Request, call_next: Callable):
        start = time.time()

        # Safe read of request body and preserve for downstream:
        try:
            body_bytes = await request.body()
        except Exception:
            body_bytes = b""

        # Starlette/fastapi uses receive callable; replace so downstream can still read the body
        async def receive() -> dict:
            return {"type": "http.request", "body": body_bytes}

        # attach a new receive() function so downstream handlers can read request.body() normally
        request._receive = receive  # monkeypatching common pattern for BaseHTTPMiddleware

        # capture basic context
        user_id = request.headers.get("x-user-id") or request.headers.get("authorization")
        tenant = request.headers.get("x-tenant-id")

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.time() - start) * 1000
            doc_error = {
                "service": "api-gateway",
                "path": str(request.url.path),
                "method": request.method,
                "status": 500,
                "user_id": user_id,
                "tenant": tenant,
                "request_body": _truncate_text(body_bytes, settings.MAX_BODY_CHARS),
                "error": str(exc),
                "duration_ms": duration_ms,
                "timestamp": time.time()
            }
            # try best-effort indexing (synchronous here) — do not fail the original exception
            try:
                index_audit(doc_error)
            except Exception:
                logger.exception("Failed to index error audit")
            raise

        duration_ms = (time.time() - start) * 1000

        # prepare doc (we do not attempt to read response body to avoid complications)
        doc = {
            "service": "api-gateway",
            "path": str(request.url.path),
            "method": request.method,
            "status": response.status_code,
            "user_id": user_id,
            "tenant": tenant,
            "request_body": _truncate_text(body_bytes, settings.MAX_BODY_CHARS),
            "duration_ms": duration_ms,
            "timestamp": time.time()
        }

        # enqueue indexing as background task (fast and non-blocking)
        bg = BackgroundTasks()
        bg.add_task(_index_background_safe, doc)
        # attach background to response so FastAPI runs it
        try:
            # If response already has background tasks, append; otherwise set it
            if hasattr(response, "background") and response.background:
                # response.background is a BackgroundTasks instance; add new task
                response.background.add_task(_index_background_safe, doc)
            else:
                response.background = bg
        except Exception:
            # best-effort only
            logger.exception("Failed to attach background task for audit indexing")

        return response

async def _index_background_safe(doc: dict):
    """
    Background task wrapper — index doc and ignore exceptions (already logged).
    """
    try:
        index_audit(doc)
    except Exception:
        logger.exception("Background audit indexing failed")
