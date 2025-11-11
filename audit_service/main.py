import os
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import databases
import sqlalchemy
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/auditdb")
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

audit_table = sqlalchemy.Table(
    "audit", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("trace_id", sqlalchemy.String(128)),
    sqlalchemy.Column("timestamp", sqlalchemy.DateTime),
    sqlalchemy.Column("service", sqlalchemy.String(128)),
    sqlalchemy.Column("event_type", sqlalchemy.String(50)),
    sqlalchemy.Column("operation", sqlalchemy.String(256)),
    sqlalchemy.Column("user_id", sqlalchemy.String(128), nullable=True),
    sqlalchemy.Column("client_ip", sqlalchemy.String(50), nullable=True),
    sqlalchemy.Column("method", sqlalchemy.String(10), nullable=True),
    sqlalchemy.Column("path", sqlalchemy.String(512), nullable=True),
    sqlalchemy.Column("status_code", sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column("duration_ms", sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column("request_body", sqlalchemy.JSON, nullable=True),
    sqlalchemy.Column("response_body", sqlalchemy.JSON, nullable=True),
    sqlalchemy.Column("metadata", sqlalchemy.JSON, nullable=True),
)

engine = sqlalchemy.create_engine(DATABASE_URL.replace("asyncpg","psycopg2"))
metadata.create_all(engine)

app = FastAPI(title="Audit Service")

class AuditIn(BaseModel):
    trace_id: str
    timestamp: str
    service: str
    event_type: str
    operation: str
    user_id: str | None = None
    client_ip: str | None = None
    method: str | None = None
    path: str | None = None
    status_code: int | None = None
    duration_ms: int | None = None
    request_body: dict | None = None
    response_body: dict | None = None
    metadata: dict | None = None

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/audit")
async def create_audit(item: AuditIn):
    query = audit_table.insert().values(
        trace_id=item.trace_id,
        timestamp=datetime.fromisoformat(item.timestamp.replace("Z","")),
        service=item.service,
        event_type=item.event_type,
        operation=item.operation,
        user_id=item.user_id,
        client_ip=item.client_ip,
        method=item.method,
        path=item.path,
        status_code=item.status_code,
        duration_ms=item.duration_ms,
        request_body=item.request_body,
        response_body=item.response_body,
        metadata=item.metadata,
    )
    record_id = await database.execute(query)
    return {"id": record_id}
