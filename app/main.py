# app/main.py
import time
import uuid
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from dotenv import load_dotenv

from app.utils.logger import setup_logger
from app.core.redis_client import get_redis
from app.core.limiter import limiter
from app.modules.auth.routes import router as auth_router
from app.modules.sbom.routes import router as sbom_router
from app.modules.vuln.routes import router as vuln_router
from app.modules.risk.routes import router as risk_router
from app.middleware.audit_logger import AuditLoggerMiddleware
from app.routes import test as test_router
from app.utils.es_client import ensure_connection

load_dotenv()

# Logging
logger = setup_logger()
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")

# FastAPI app
app = FastAPI(title="MyESI API Gateway", version="1.0.0")

# Middleware
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(AuditLoggerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Routers
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(sbom_router, prefix="/api/sbom", tags=["SBOM"])
app.include_router(vuln_router, prefix="/api/vuln", tags=["Vuln"])
app.include_router(risk_router, prefix="/api/risk", tags=["Risk"])
app.include_router(test_router.router)

# Startup & Shutdown
@app.on_event("startup")
async def startup_event():
    # Redis
    try:
        app.state.redis = get_redis()
        logger.info({"event": "startup", "msg": "Redis client initialized"})
    except Exception:
        logger.warning("Redis init failed")
    
    # Elasticsearch connection
    ok = ensure_connection()
    if not ok:
        logger.warning("Elasticsearch not available at startup — logs may fail until it's up.")
    else:
        logger.info("Elasticsearch connection OK")

@app.on_event("shutdown")
async def shutdown_event():
    try:
        app.state.redis.close()
    except Exception:
        pass
    logger.info({"event": "shutdown", "msg": "App shutdown"})

# Analytics middleware
@app.middleware("http")
async def analytics_and_logging_middleware(request: Request, call_next):
    start = time.time()
    request_id = str(uuid.uuid4())
    client_ip = request.client.host if request.client else request.headers.get("x-forwarded-for", "unknown")
    try:
        response = await call_next(request)
    except Exception:
        latency = time.time() - start
        logger.info({"event": "request", "request_id": request_id, "method": request.method,
                     "path": request.url.path, "status": 500, "latency_ms": int(latency * 1000),
                     "client_ip": client_ip})
        try:
            r = app.state.redis
            r.incr(f"stats:hits:{request.url.path}")
            r.hincrby(f"stats:status:{request.url.path}", 500, 1)
        except Exception:
            pass
        raise
    latency = time.time() - start
    status = response.status_code
    logger.info({"event": "request", "request_id": request_id, "method": request.method,
                 "path": request.url.path, "status": status, "latency_ms": int(latency * 1000),
                 "client_ip": client_ip})
    try:
        r = app.state.redis
        r.incr(f"stats:hits:{request.url.path}")
        r.hincrby(f"stats:status:{request.url.path}", status, 1)
    except Exception:
        logger.warning({"event": "analytics_error", "path": request.url.path})
    return response

# Healthcheck
@app.get("/")
async def root():
    return {"status": "ok", "service": "api-gateway"}
