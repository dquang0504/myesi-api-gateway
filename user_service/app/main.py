from fastapi import FastAPI
from app.middleware.audit_middleware import AuditMiddleware

app = FastAPI(title="user-service")
app.add_middleware(AuditMiddleware)

@app.get("/")
def root():
    return {"message": "User Service Running 🚀"}

@app.post("/api/user/create")
def create_user():
    return {"message": "User created successfully"}

@app.get("/api/user/list")
def list_users():
    return {"message": "List of users"}
