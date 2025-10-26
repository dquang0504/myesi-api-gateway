from fastapi import APIRouter, Depends
from app.core.rbac import role_required

router = APIRouter()

@router.get("/admin/dashboard")
def admin_dashboard(user=Depends(role_required(["admin"]))):
    return {"message": "Welcome Admin!", "user": user}

@router.get("/user/profile")
def user_profile(user=Depends(role_required(["user", "admin"]))):
    return {"message": "User Profile Accessed", "user": user}
