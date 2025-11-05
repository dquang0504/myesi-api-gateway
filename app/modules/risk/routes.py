"""
Risk module routes.
Forwards requests from API Gateway to Risk Service.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, logger
import httpx
from app.utils.security import require_role


router = APIRouter()

# URL of Risk Service
RISK_SERVICE_URL = "http://risk-service:8004"


# ----- GET RISK SCORE -----
@router.get("/score", dependencies=[Depends(require_role(["developer"]))])
async def risk_score(request: Request):
    """
    Forward risk score request to Risk Service.
    Query param: sbom_id
    """
    try:
        params = dict(request.query_params)
        if "sbom_id" not in params:
            raise HTTPException(
                status_code=400, detail="Missing sbom_id query parameter"
            )

        logger.info(
            f"Forwarding /score request to Risk Service: {RISK_SERVICE_URL}/api/risk/score with params {params}"
        )
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{RISK_SERVICE_URL}/api/risk/score", params=params, timeout=30.0
            )
        return res.json()
    except Exception as e:
        logger.error(f"Error forwarding /score request: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Gateway -> Risk Service score error: {str(e)}"
        )


# ----- GET RISK TRENDS -----
@router.get("/trends", dependencies=[Depends(require_role(["developer"]))])
async def risk_trends(request: Request):
    """
    Forward risk trends request to Risk Service.
    """
    try:
        params = dict(request.query_params)
        logger.info(
            f"Forwarding /trends request to Risk Service: {RISK_SERVICE_URL}/api/risk/trends with params {params}"
        )
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{RISK_SERVICE_URL}/api/risk/trends", timeout=30.0)
        logger.info(f"Risk Service responded: status={res.status_code}")
        return res.json()
    except Exception as e:
        logger.error(f"Error forwarding /trends request: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Gateway -> Risk Service trends error: {str(e)}"
        )
