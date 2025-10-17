# from sqlalchemy.orm import Session
# from passlib.context import CryptContext
# from app.modules.auth import models, schemas
# from app.utils.security import create_access_token, create_refresh_token, verify_token

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# def get_password_hash(password):
#     return pwd_context.hash(password)


# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)


# def create_user(db: Session, user: schemas.UserCreate):
#     hashed_pw = get_password_hash(user.password)
#     db_user = models.User(username=user.username, email=user.email, password=hashed_pw)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


# def login_user(db: Session, username: str, password: str):
#     user = db.query(models.User).filter(models.User.username == username).first()
#     if not user or not verify_password(password, user.password):
#         return None

#     access_token = create_access_token({"sub": user.username})
#     refresh_token = create_refresh_token({"sub": user.username})
#     return {"access_token": access_token, "refresh_token": refresh_token}


# def refresh_access_token(refresh_token: str):
#     payload = verify_token(refresh_token)
#     if not payload or payload.get("type") != "refresh":
#         return None

#     username = payload.get("sub")
#     new_access = create_access_token({"sub": username})
#     return new_access
