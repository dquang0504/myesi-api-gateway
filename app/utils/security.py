from datetime import datetime, timezone
import os
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY", "replace-with-secure-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def get_token_from_header(request: Request):
    """
    Extract Bearer token from Authorization header.
    Example: Authorization: Bearer <token>
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login first!",
        )
    return auth_header.split(" ")[1]


def verify_jwt(request: Request):
    """
    Verify and decode JWT token, check expiration.
    Returns the decoded payload if valid.
    """
    token = get_token_from_header(request)
    try:
        print(SECRET_KEY)
        print(ALGORITHM)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
            timezone.utc
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def require_role(required_roles: list):
    """
    Dependency to enforce role-based access control (RBAC).
    Example:
        @router.get("/admin", dependencies=[Depends(require_role(["admin"]))])
    """

    def wrapper(token_data=Depends(verify_jwt)):
        user_role = token_data.get("role")
        if not user_role:
            raise HTTPException(status_code=403, detail="User role missing in token")
        if user_role not in required_roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return token_data

    return wrapper
