from fastapi import FastAPI
from app.middleware.audit_middleware import AuditMiddleware

app = FastAPI(title="risk-service-report")
app.add_middleware(AuditMiddleware)

@app.get("/")
def root():
    return {"message": "Risk Service Report Running 🚀"}

@app.post("/api/risk/report")
def create_report():
    return {"message": "Risk report created"}

@app.get("/api/risk/list")
def list_reports():
    return {"message": "List of risk reports"}
