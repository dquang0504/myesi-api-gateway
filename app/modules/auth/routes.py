"""
Authentication module routes.
Handles registration, login, and token refresh endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.modules.auth import schemas, service

router = APIRouter()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=schemas.UserCreate)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing_user = db.query(service.models.User).filter(service.models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return service.create_user(db, user)


@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access and refresh tokens."""
    tokens = service.login_user(db, user.username, user.password)
    if not tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return tokens


@router.post("/refresh-token", response_model=schemas.Token)
def refresh_token(token_data: schemas.RefreshToken):
    """Refresh access token using the refresh token."""
    new_access = service.refresh_access_token(token_data.refresh_token)
    if not new_access:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    return {"access_token": new_access, "token_type": "bearer"}


@router.get("/test")
async def test_auth():
    """Simple endpoint to verify auth module routing works."""
    return {"msg": "Auth route works!"}
