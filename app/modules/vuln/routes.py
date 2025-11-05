"""
Vulnerability module routes.
Forwards requests from API Gateway to Vulnerability Service.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
import httpx
from app.utils.security import require_role

router = APIRouter()

# URL of vuln-service (chạy trong Docker)
VULN_SERVICE_URL = "http://vulnerability-service:8003"


# ----- HEALTH CHECK -----
@router.get("/health")
async def health_check():
    """Check vuln service health."""
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{VULN_SERVICE_URL}/api/vuln/health")
        return res.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gateway -> Vuln Service health error: {str(e)}"
        )

# ----- REFRESH -----
@router.get("/stream")
async def stream_vulnerabilities(request: Request):
    project_name = request.query_params.get("project_name")
    if not project_name:
        raise HTTPException(status_code=400, detail="project_name required")

    async def event_stream():
        async with httpx.AsyncClient(timeout=None) as client:
            # giữ kết nối tới vuln-service SSE
            async with client.stream(
                "GET",
                f"{VULN_SERVICE_URL}/api/vuln/stream",
                params={"project_name": project_name},
                headers={"X-From-Gateway": "true"},  # đánh dấu request
            ) as res:
                async for line in res.aiter_lines():
                    if await request.is_disconnected():
                        print("❌ Client disconnected")
                        break
                    if line.strip():
                        yield f"{line}\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

# ----- GET VULNS BY SBOM -----
@router.get("/{sbom_id}", dependencies=[Depends(require_role(["developer"]))])
async def get_vulns_by_sbom(sbom_id: str):
    """Forward request to get vulnerabilities for a given SBOM ID."""
    print("HERE")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{VULN_SERVICE_URL}/api/vuln/{sbom_id}")
        return res.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gateway -> Vuln Service error: {str(e)}"
        )


# ----- REFRESH -----
@router.post("/refresh", dependencies=[Depends(require_role(["developer"]))])
async def refresh_vuln(request: Request):
    """Forward vulnerability refresh request."""
    try:
        body = await request.json()
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{VULN_SERVICE_URL}/api/vuln/refresh", json=body)
        return res.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gateway -> Vuln Service refresh error: {str(e)}"
        )


# ----- STREAM (SSE) -----
@router.get("/stream")
async def stream_vulnerabilities(request: Request):
    """
    Forward SSE stream to frontend.
    Giữ kết nối giữa client và vuln-service.
    """

    project_name = request.query_params.get("project_name")
    if not project_name:
        raise HTTPException(status_code=400, detail="project_name required")

    async def event_stream():
        # Giữ kết nối HTTP streaming tới vuln-service
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "GET",
                f"{VULN_SERVICE_URL}/api/vuln/stream",
                params={"project_name": project_name},
            ) as res:
                async for line in res.aiter_lines():
                    if await request.is_disconnected():
                        break
                    if line.strip():
                        yield f"{line}\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
