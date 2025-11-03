"""
Report module routes.
Forwards requests from API Gateway to Report Service.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, logger
import httpx
from app.utils.security import require_role


router = APIRouter()

# URL of Report Service
REPORT_SERVICE_URL = "http://report-service:8005"


# ----- GET ALL REPORTS -----
@router.get("/list", dependencies=[Depends(require_role(["developer", "admin"]))])
async def get_all_reports(request: Request):
    """
    Forward request to get all reports from Report Service.
    """
    try:
        params = dict(request.query_params)
        logger.info(
            f"Forwarding /list request to Report Service: {REPORT_SERVICE_URL}/api/report/list with params {params}"
        )
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{REPORT_SERVICE_URL}/api/report/list", params=params, timeout=30.0
            )
        logger.info(f"Report Service responded: status={res.status_code}")
        return res.json()
    except Exception as e:
        logger.error(f"Error forwarding /list request: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Gateway -> Report Service list error: {str(e)}"
        )


# ----- GET REPORT BY ID -----
@router.get("/{report_id}", dependencies=[Depends(require_role(["developer", "admin"]))])
async def get_report(report_id: str):
    """
    Forward request to get a specific report by ID.
    """
    try:
        logger.info(
            f"Forwarding /{{report_id}} request to Report Service: {REPORT_SERVICE_URL}/api/report/{report_id}"
        )
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{REPORT_SERVICE_URL}/api/report/{report_id}", timeout=30.0)
        logger.info(f"Report Service responded: status={res.status_code}")
        return res.json()
    except Exception as e:
        logger.error(f"Error forwarding /{{report_id}} request: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Gateway -> Report Service error: {str(e)}"
        )


# ----- CREATE NEW REPORT -----
@router.post("/create", dependencies=[Depends(require_role(["developer", "admin"]))])
async def create_report(request: Request):
    """
    Forward request to create a new report.
    """
    try:
        payload = await request.json()
        logger.info(
            f"Forwarding /create request to Report Service: {REPORT_SERVICE_URL}/api/report/create"
        )
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{REPORT_SERVICE_URL}/api/report/create", json=payload, timeout=30.0
            )
        logger.info(f"Report Service responded: status={res.status_code}")
        return res.json()
    except Exception as e:
        logger.error(f"Error forwarding /create request: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Gateway -> Report Service create error: {str(e)}"
        )


# ----- UPDATE REPORT -----
@router.put("/{report_id}", dependencies=[Depends(require_role(["developer", "admin"]))])
async def update_report(request: Request, report_id: str):
    """
    Forward request to update an existing report.
    """
    try:
        payload = await request.json()
        logger.info(
            f"Forwarding PUT /{{report_id}} request to Report Service: {REPORT_SERVICE_URL}/api/report/{report_id}"
        )
        async with httpx.AsyncClient() as client:
            res = await client.put(
                f"{REPORT_SERVICE_URL}/api/report/{report_id}",
                json=payload,
                timeout=30.0,
            )
        logger.info(f"Report Service responded: status={res.status_code}")
        return res.json()
    except Exception as e:
        logger.error(f"Error forwarding PUT /{{report_id}} request: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Gateway -> Report Service update error: {str(e)}"
        )


# ----- DELETE REPORT -----
@router.delete("/{report_id}", dependencies=[Depends(require_role(["admin"]))])
async def delete_report(report_id: str):
    """
    Forward request to delete a report. Only admins can delete.
    """
    try:
        logger.info(
            f"Forwarding DELETE /{{report_id}} request to Report Service: {REPORT_SERVICE_URL}/api/report/{report_id}"
        )
        async with httpx.AsyncClient() as client:
            res = await client.delete(f"{REPORT_SERVICE_URL}/api/report/{report_id}", timeout=30.0)
        logger.info(f"Report Service responded: status={res.status_code}")
        return res.json()
    except Exception as e:
        logger.error(f"Error forwarding DELETE /{{report_id}} request: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Gateway -> Report Service delete error: {str(e)}"
        )


# ----- HEALTH CHECK -----
@router.get("/health")
async def health_check():
    """Check report service health."""
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{REPORT_SERVICE_URL}/api/report/health")
        return res.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gateway -> Report Service health error: {str(e)}"
        )

