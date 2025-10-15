"""
Authentication module routes.
Handles login and registration endpoints.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/test")
async def test_auth():
    """Simple endpoint to verify auth module routing works."""
    return {"msg": "Auth route works!"}
