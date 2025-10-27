"""
SBOM module routes.
Forwards requests from API Gateway to SBOM Service.
"""

from fastapi import APIRouter, HTTPException, Request, UploadFile, File
import httpx

router = APIRouter()

# URL of sbom-service
SBOM_SERVICE_URL = "http://sbom-service:8002"


# ----- UPLOAD SBOM -----
@router.post("/upload")
async def upload_sbom(request: Request, file: UploadFile = File(...)):
    """Forward SBOM upload to SBOM Service."""
    try:
        form = await request.form()
        project_name = form.get("project_name")

        if not project_name:
            raise HTTPException(status_code=400, detail="Missing project_name")

        # Prepare multipart/form-data to send
        form_data = {
            "project_name": (None, project_name),
            "file": (file.filename, await file.read(), file.content_type),
        }

        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{SBOM_SERVICE_URL}/api/sbom/upload", files=form_data, timeout=60.0
            )
        return res.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gateway -> SBOM Service upload error: {str(e)}"
        )


# ----- GET SBOM BY ID -----
@router.get("/{sbom_id}")
async def get_sbom(sbom_id: str):
    """Forward get SBOM by ID."""
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{SBOM_SERVICE_URL}/api/sbom/{sbom_id}")
        return res.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gateway -> SBOM Service upload error: {str(e)}"
        )


# ----- LIST SBOMs -----
@router.get("/list")
async def list_sboms(request: Request):
    """Forward SBOM list request."""
    try:
        params = dict(request.query_params)
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{SBOM_SERVICE_URL}/api/sbom/list", params=params)
        return res.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gateway -> SBOM Service upload error: {str(e)}"
        )
