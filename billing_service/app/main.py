from fastapi import FastAPI
from app.middleware.audit_middleware import AuditMiddleware

app = FastAPI(title="billing-service")
app.add_middleware(AuditMiddleware)

@app.get("/")
def root():
    return {"message": "Billing Service Running 🚀"}

@app.post("/api/billing/checkout")
def checkout():
    return {"message": "Checkout endpoint called"}
