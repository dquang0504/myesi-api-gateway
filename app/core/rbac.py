from fastapi import Depends, HTTPException, status, Request
from app.utils.security import verify_jwt


def role_required(allowed_roles: list):
    """
    Restrict access to specific roles using JWT payload from verify_jwt().
    """

    def wrapper(request: Request, payload: dict = Depends(verify_jwt)):
        user_role = payload.get("role")

        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user role",
            )

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for role '{user_role}'",
            )

        return payload  # forward decoded JWT payload if authorized

    return wrapper
