from fastapi import FastAPI
from app.middleware.audit_middleware import AuditMiddleware

app = FastAPI(title="api-gateway")
app.add_middleware(AuditMiddleware)

@app.get("/")
def root():
    return {"message": "API Gateway Running 🚀"}

@app.get("/api/gateway/route")
def gateway_route():
    return {"message": "API Gateway route called"}
