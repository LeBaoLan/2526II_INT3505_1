from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from db import payments_db, refunds_db, new_id, now

router = APIRouter()


# ── Schema ──────────────────────────────────────────────

class RefundCreate(BaseModel):
    payment_id: str = Field(..., example="pay_abc123")
    reason: Optional[str] = Field(None, example="Khách hàng yêu cầu hoàn tiền")


# ── Endpoints ───────────────────────────────────────────

@router.post("/refunds", status_code=201)
def create_refund(body: RefundCreate):
    """Tạo yêu cầu hoàn tiền cho một giao dịch."""
    payment = payments_db.get(body.payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment["status"] == "refunded":
        raise HTTPException(status_code=409, detail="Payment already refunded")

    ref_id = new_id("ref")
    record = {
        "id": ref_id,
        "payment_id": body.payment_id,
        "amount": payment["amount"],
        "status": "refunded",
        "reason": body.reason,
        "created_at": now(),
    }
    refunds_db[ref_id] = record
    payments_db[body.payment_id]["status"] = "refunded"
    return record
