# app/middleware/audit_middleware.py
import time
import uuid
import json
import asyncio
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import httpx
from datetime import datetime

AUDIT_SERVICE_URL = "http://audit-service:8005/audit"  # Docker container URL

def now_iso():
    return datetime.utcnow().isoformat() + "Z"

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()

        trace_id = request.headers.get("X-Request-ID") or request.headers.get("X-Trace-ID") or str(uuid.uuid4())
        try:
            req_body = await request.json()
        except Exception:
            req_body = None

        client_ip = request.client.host if request.client else None
        service_name = request.app.title or "unknown-service"

        # Pre-request audit
        pre_event = {
            "trace_id": trace_id,
            "timestamp": now_iso(),
            "service": service_name,
            "event_type": "request",
            "operation": request.url.path.strip("/").replace("/", "."),
            "user_id": request.headers.get("X-User-Id"),
            "client_ip": client_ip,
            "method": request.method,
            "path": str(request.url.path),
            "request_body": req_body,
            "metadata": {}
        }

        asyncio.create_task(_send_audit(pre_event))

        # Call handler
        try:
            response = await call_next(request)
            status_code = response.status_code
            try:
                body = b""
                async for chunk in response.__dict__["body_iterator"]:
                    body += chunk
                response.__dict__["body_iterator"] = iter([body])
                try:
                    resp_body = json.loads(body.decode())
                except:
                    resp_body = body.decode(errors="ignore")
            except:
                resp_body = None
        except Exception as exc:
            duration_ms = int((time.time() - start) * 1000)
            err_event = {
                "trace_id": trace_id,
                "timestamp": now_iso(),
                "service": service_name,
                "event_type": "error",
                "operation": request.url.path.strip("/").replace("/","."),
                "user_id": request.headers.get("X-User-Id"),
                "client_ip": client_ip,
                "method": request.method,
                "path": str(request.url.path),
                "status_code": 500,
                "duration_ms": duration_ms,
                "request_body": req_body,
                "response_body": str(exc),
                "metadata": {}
            }
            asyncio.create_task(_send_audit(err_event))
            raise

        duration_ms = int((time.time() - start) * 1000)
        post_event = {
            "trace_id": trace_id,
            "timestamp": now_iso(),
            "service": service_name,
            "event_type": "response",
            "operation": request.url.path.strip("/").replace("/","."),
            "user_id": request.headers.get("X-User-Id"),
            "client_ip": client_ip,
            "method": request.method,
            "path": str(request.url.path),
            "status_code": status_code,
            "duration_ms": duration_ms,
            "request_body": req_body,
            "response_body": resp_body,
            "metadata": {}
        }
        asyncio.create_task(_send_audit(post_event))

        response.headers["X-Request-ID"] = trace_id
        return response

async def _send_audit(event: dict):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(AUDIT_SERVICE_URL, json=event)
    except:
        pass
