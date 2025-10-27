"""
Authentication module routes.
Handles registration, login, and token refresh endpoints.
"""

from fastapi import APIRouter, HTTPException, Request, Depends
import httpx
from app.core.limiter import limiter
from app.utils.security import require_role

router = APIRouter()

# URL of user-service
USER_SERVICE_URL = "http://user-service:8001"


# ----- REGISTER -----
@router.post("/register")
@limiter.limit("5/minute")
async def register_user(request: Request):
    """Forward register request to User Service."""
    try:
        payload = await request.json()
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{USER_SERVICE_URL}/api/users/register", json=payload
            )
        return res.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gateway → User Service error: {str(e)}"
        )


# ----- LOGIN -----
@router.post("/login")
async def login_user(request: Request):
    """Forward login request to User Service."""
    try:
        payload = await request.json()
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{USER_SERVICE_URL}/api/users/login", json=payload)
        return res.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gateway → User Service error: {str(e)}"
        )


# ----- REFRESH TOKEN -----
@router.post("/refresh-token")
async def refresh_token(request: Request):
    """Forward refresh-token request to User Service."""
    try:
        payload = await request.json()
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{USER_SERVICE_URL}/api/users/refresh-token", json=payload
            )
        return res.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gateway → User Service error: {str(e)}"
        )


# ----- ADMIN DASHBOARD ACCESS -----
@router.get("/admin/dashboard", dependencies=[Depends(require_role(["admin"]))])
async def admin_dashboard(request: Request):
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{USER_SERVICE_URL}/api/admin/dashboard")
        return res.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gateway → User Service error: {str(e)}"
        )


# ----- ADMIN GET ALL USERS -----
@router.get("/admin/users/", dependencies=[Depends(require_role(["admin"]))])
async def get_all_users(request: Request):
    """Forward request to User Service to retrieve all users."""
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{USER_SERVICE_URL}/api/admin/users")
        return res.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gateway → User Service error: {str(e)}"
        )


# ----- LOGOUT -----
@router.post("/logout")
async def logout_user(request: Request):
    """Forward logout request to User Service."""
    try:
        # Forward along with Authorization header to let user-service know who log outs
        headers = {"Authorization": request.headers.get("Authorization")}
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{USER_SERVICE_URL}/api/users/logout", headers=headers
            )
        return res.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gateway → User Service error: {str(e)}"
        )


# ----- HEALTHCHECK -----
@router.get("/test")
@limiter.limit("5/minute")
async def test_auth(request: Request):  # added request argument
    return {"msg": "Auth route works!"}
