
"""
Main entrypoint for the MyESI API Gateway service.
Handles app initialization, middleware setup, and router registration.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logger import setup_logger
from app.modules.auth.routes import router as auth_router

# Initialize Loguru logger
logger = setup_logger()

# Create FastAPI app instance
app = FastAPI(title="MyESI API Gateway",version="1.0.0")

# ---- Middleware: CORS ----
# Allow frontend and other microservices to make cross-origin requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all during dev; restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Middleware: Request Logging ----
# Logs every request and response status for observability.
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"{response.status_code} {request.url}")
    return response

# ---- Register Routers ----
# Each module handles a specific feature or service.
app.include_router(auth_router, prefix="/api/auth",tags=["Auth"])

# ---- Healthcheck Endpoint ----
@app.get("/")
def root():
    return {"status": "ok", "service": "api-gateway"}