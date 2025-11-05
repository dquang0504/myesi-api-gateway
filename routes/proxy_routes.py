# routes/proxy_routes.py
from fastapi import APIRouter, Request, Response, status
import httpx
import os

router = APIRouter()

RISK_SERVICE_URL = os.getenv("RISK_SERVICE_URL", "http://risk:8000")
REPORT_SERVICE_URL = os.getenv("REPORT_SERVICE_URL", "http://report:8000")

async def forward_request(base_url: str, request: Request, path: str):
    url = f"{base_url}{path}"
    headers = dict(request.headers)
    # remove host header so upstream receives correct host
    headers.pop("host", None)

    body = await request.body()
    params = dict(request.query_params)

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.request(
            request.method,
            url,
            headers=headers,
            params=params,
            content=body,
        )
    return Response(content=resp.content, status_code=resp.status_code, headers=resp.headers)

# Example: forward all /api/risk/*  to Risk service
@router.api_route("/api/risk/{rest_of_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def risk_proxy(request: Request, rest_of_path: str):
    return await forward_request(f"{RISK_SERVICE_URL}/api/risk/", request, rest_of_path)

# Example: forward all /api/report/* to Report service
@router.api_route("/api/report/{rest_of_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def report_proxy(request: Request, rest_of_path: str):
    return await forward_request(f"{REPORT_SERVICE_URL}/api/report/", request, rest_of_path)
