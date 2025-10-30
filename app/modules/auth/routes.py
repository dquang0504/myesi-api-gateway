"""
Authentication module routes.
Handles registration, login, and token refresh endpoints.
"""

from fastapi import APIRouter, HTTPException, Request, Depends, Response
from fastapi.responses import JSONResponse
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
async def login_user(request: Request, response: Response):
    """Forward login request to User Service."""
    try:
        payload = await request.json()
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{USER_SERVICE_URL}/api/users/login", json=payload)

        if "set-cookie" in res.headers:
            cookies = res.headers.get_list("set-cookie")
            for cookie in cookies:
                response.headers.append("set-cookie", cookie)

        return JSONResponse(content=res.json(), status_code=res.status_code)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gateway → User Service error: {str(e)}"
        )


# ----- REFRESH TOKEN -----
@router.post("/refresh-token")
async def refresh_token(request: Request, response: Response):
    """Forward refresh-token request with cookies to User Service."""
    try:
        # Forward cookies from client to User Service
        cookies = request.cookies

        async with httpx.AsyncClient(follow_redirects=True) as client:
            res = await client.post(
                f"{USER_SERVICE_URL}/api/users/refresh-token", cookies=cookies
            )

        # Copy refreshed cookie (if any)
        if "set-cookie" in res.headers:
            response.headers["set-cookie"] = res.headers["set-cookie"]

        return JSONResponse(content=res.json(), status_code=res.status_code)
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


# ----- ADMIN UPDATE USER -----
@router.put("/admin/users/{user_id}", dependencies=[Depends(require_role(["admin"]))])
async def update_user(request: Request, user_id: int):
    """Forward update user request to User Service."""
    try:
        payload = await request.json()
        async with httpx.AsyncClient() as client:
            res = await client.put(
                f"{USER_SERVICE_URL}/api/admin/users/{user_id}",
                json=payload,
            )
        return JSONResponse(content=res.json(), status_code=res.status_code)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gateway → User Service error: {str(e)}",
        )


# ----- LOGOUT -----
@router.post("/logout")
async def logout_user(request: Request):
    """Forward logout request to User Service."""
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{USER_SERVICE_URL}/api/users/logout")
    return res.json()


# ----- HEALTHCHECK -----
@router.get("/test")
@limiter.limit("5/minute")
async def test_auth(request: Request):  # added request argument
    return {"msg": "Auth route works!"}
