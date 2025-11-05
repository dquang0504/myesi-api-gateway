"""
Billing module routes.
Forwards requests from API Gateway to Billing Service.
"""
from app.utils.logger import setup_logger
from fastapi import APIRouter, Depends, HTTPException, Request
import httpx
from app.utils.security import require_role

router = APIRouter()
logger = setup_logger()

# URL of Billing Service
BILLING_SERVICE_URL = "http://billing-service:8005"

# ----- CREATE CHECKOUT SESSION -----
@router.post("/create-checkout-session", dependencies=[Depends(require_role(["developer", "admin"]))])
async def create_checkout(request: Request):
    """
    Forward checkout request to Billing Service.
    """
    try:
        body = await request.json()
        # Inject user info if available
        user = getattr(request.state, "user", None)
        if user:
            body["user"] = {"id": user.id, "email": user.email}
        logger.info(
            f"Forwarding /create-checkout-session to Billing Service: {BILLING_SERVICE_URL}/api/billing/create-checkout-session"
        )

        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{BILLING_SERVICE_URL}/api/billing/create-checkout-session",
                json=body,
                timeout=30.0,
            )

        return res.json()
    except Exception as e:
        logger.error(f"Error forwarding /create-checkout-session request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Gateway -> Billing Service checkout error: {str(e)}",
        )
        
# ----- STRIPE WEBHOOK -----
@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Forward Stripe webhook payload to Billing Service.
    Note: No authentication required — this is called directly by Stripe servers.
    """
    try:
        payload = await request.body()
        headers = dict(request.headers)

        logger.info(
            f"Forwarding /webhook to Billing Service: {BILLING_SERVICE_URL}/api/billing/webhook"
        )

        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{BILLING_SERVICE_URL}/api/billing/webhook",
                content=payload,
                headers=headers,
                timeout=30.0,
            )

        return res.json()
    except Exception as e:
        logger.error(f"Error forwarding /webhook request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Gateway -> Billing Service webhook error: {str(e)}",
        )
        
# ----- GET LATEST SUBSCRIPTION -----
@router.get("/latest-subscription", dependencies=[Depends(require_role(["developer", "admin"]))])
async def get_latest_subscription(request: Request):
    """Forward request to Billing Service to fetch user's latest subscription."""
    try:
        user = getattr(request.state, "user", None)
        headers = {"X-User-ID": str(user.id)} if user else {}
        
        print("User: ", user)

        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{BILLING_SERVICE_URL}/api/billing/latest-subscription",
                headers=headers,
                timeout=15.0,
            )

        return res.json()
    except Exception as e:
        logger.error(f"Error forwarding /latest-subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")
        
# ----- GET SUBSCRIPTION PLANS -----
@router.get("/plans", dependencies=[Depends(require_role(["developer", "admin"]))])
async def get_subscription_plans(request: Request):
    """
    Forward request to Billing Service to fetch all available subscription plans.
    """
    try:
        logger.info(
            f"Forwarding /plans to Billing Service: {BILLING_SERVICE_URL}/api/billing/plans"
        )

        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{BILLING_SERVICE_URL}/api/billing/plans",
                timeout=15.0,
            )

        return res.json()
    except Exception as e:
        logger.error(f"Error forwarding /plans request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Gateway -> Billing Service plans error: {str(e)}",
        )