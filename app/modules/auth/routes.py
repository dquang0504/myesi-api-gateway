from fastapi import APIRouter, Request
from app.core.limiter import limiter

router = APIRouter()

@router.get("/test")
@limiter.limit("5/minute")
async def test_auth(request: Request):   # ✅ added request argument
    return {"msg": "Auth route works!"}
