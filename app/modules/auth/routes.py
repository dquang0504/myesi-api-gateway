"""
Authentication module routes.
Handles registration, login, and token refresh endpoints.
"""

from fastapi import APIRouter, HTTPException, Request
import httpx
from app.core.limiter import limiter

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
            print(payload)
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


# ----- HEALTHCHECK -----
@router.get("/test")
@limiter.limit("5/minute")
async def test_auth(request: Request):  # ✅ added request argument
    return {"msg": "Auth route works!"}
