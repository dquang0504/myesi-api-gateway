# app/routes/test.py
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["api"])


class OrderIn(BaseModel):
    amount: int


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/orders")
async def create_order(payload: OrderIn, x_user_id: str | None = Header(None)):
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be > 0")
    # pretend to create order
    return {"order_id": "order_123", "amount": payload.amount, "created_by": x_user_id}
