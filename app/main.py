from fastapi import FastAPI
from app.modules.auth.routes import router as auth_router

app = FastAPI(title="MyESI API Gateway", version="1.0.0")

# Register Auth routes
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])

# Healthcheck
@app.get("/")
def root():
    return {"status": "ok", "service": "api-gateway"}



