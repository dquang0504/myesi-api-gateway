import time
import uuid
import logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from jose import JWTError, jwt
from dotenv import load_dotenv

from app.utils.logger import setup_logger
from app.core.redis_client import get_redis
from app.core.limiter import limiter
from app.core.config import settings

from app.db.models import User

# Middleware
from app.middleware.audit_logger import AuditLoggerMiddleware

# Routes
from app.modules.auth.routes import router as auth_router
from app.modules.vuln.routes import router as vuln_router
from app.modules.risk.routes import router as risk_router
from app.modules.billing.routes import router as billing_router
from app.modules.sbom.routes import router as sbom_router, projects_router
from app.routes import test as test_router

# Elasticsearch
from app.utils.es_client import ensure_connection


load_dotenv()

# Logging
logger = setup_logger()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
)

# FastAPI app
app = FastAPI(title="MyESI API Gateway", version="1.0.0")

# Middleware
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(AuditLoggerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://localhost:3000"
    ],  # Allow all origins for now (restrict in prod)
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
        logger.warning(
            "Elasticsearch not available at startup — logs may fail until it's up."
        )
    else:
        logger.info("Elasticsearch connection OK")


@app.on_event("shutdown")
async def shutdown_event():
    try:
        app.state.redis.close()
    except Exception:
        pass
    logger.info({"event": "shutdown", "msg": "App shutdown"})


# --------------------------------------------------------
# Authentication Middleware: attach user info to request.state
# --------------------------------------------------------
@app.middleware("http")
async def attach_user_middleware(request: Request, call_next):
    """
    Extract JWT from Authorization header or cookie,
    decode it using verify_jwt(), and attach user info to request.state.user
    as a User ORM instance.
    """
    try:
        auth_header = request.headers.get("Authorization")
        payload = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = jwt.decode(
                token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )
        elif "access_token" in request.cookies:
            token = request.cookies.get("access_token")
            payload = jwt.decode(
                token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )

        if payload:
            # Tạo instance User từ payload (chỉ lấy những field cần thiết)
            request.state.user = User(
                id=payload.get("id"),
                email=payload.get("sub"),
                role=payload.get("role", "developer"),
            )
        else:
            request.state.user = None

    except (HTTPException, JWTError):
        request.state.user = None

    response = await call_next(request)
    return response


# --------------------------------------------------------
# Analytics and Logging Middleware
# --------------------------------------------------------


@app.middleware("http")
async def analytics_and_logging_middleware(request: Request, call_next):
    start = time.time()
    request_id = str(uuid.uuid4())
    client_ip = (
        request.client.host
        if request.client
        else request.headers.get("x-forwarded-for", "unknown")
    )
    try:
        response = await call_next(request)
    except Exception:
        latency = time.time() - start
        logger.info(
            {
                "event": "request",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": 500,
                "latency_ms": int(latency * 1000),
                "client_ip": client_ip,
            }
        )
        try:
            r = app.state.redis
            r.incr(f"stats:hits:{request.url.path}")
            r.hincrby(f"stats:status:{request.url.path}", 500, 1)
        except Exception:
            pass
        raise
    latency = time.time() - start
    status = response.status_code
    logger.info(
        {
            "event": "request",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": status,
            "latency_ms": int(latency * 1000),
            "client_ip": client_ip,
        }
    )
    try:
        r = app.state.redis
        r.incr(f"stats:hits:{request.url.path}")
        r.hincrby(f"stats:status:{request.url.path}", status, 1)
    except Exception:
        logger.warning({"event": "analytics_error", "path": request.url.path})
    return response


# --------------------------------------------------------
# Register Routers
# --------------------------------------------------------
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(sbom_router, prefix="/api/sbom", tags=["SBOM"])
app.include_router(projects_router, prefix="/api/projects", tags=["Projects"])
app.include_router(vuln_router, prefix="/api/vulnerability", tags=["Vuln"])
app.include_router(risk_router, prefix="/api/risk", tags=["Risk"])
app.include_router(billing_router, prefix="/api/billing", tags=["Billing"])


# --------------------------------------------------------
# Healthcheck Endpoint
# --------------------------------------------------------
@app.get("/")
async def root():
    return {"status": "ok", "service": "api-gateway"}
