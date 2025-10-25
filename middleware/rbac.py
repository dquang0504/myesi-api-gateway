from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
import json, os

with open("config/rbac.json") as f:
    RBAC = json.load(f)

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
JWT_ALGO = os.getenv("JWT_ALGO", "HS256")

async def rbac_middleware(request: Request, call_next):
    if request.url.path.startswith("/public"):
        return await call_next(request)
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_roles = payload.get("roles", [])
    if isinstance(user_roles, str):
        user_roles = [user_roles]

    allowed = []
    if request.url.path in RBAC:
        allowed = RBAC[request.url.path]
    else:
        for pattern, roles in RBAC.items():
            if pattern.endswith("/*") and request.url.path.startswith(pattern[:-1]):
                allowed = roles
                break

    if not allowed or not set(user_roles).intersection(allowed):
        raise HTTPException(status_code=403, detail="Access denied")

    return await call_next(request)
