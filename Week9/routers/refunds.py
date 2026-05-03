from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from db import payments_db, refunds_db, new_id, now

router = APIRouter()


# ── Schema ──────────────────────────────────────────────

class RefundCreate(BaseModel):
    reason: Optional[str] = Field(None, example="Khach hang yeu cau hoan tien")


# ── Endpoints ───────────────────────────────────────────

# THAY DOI: v1 la POST /refunds voi payment_id trong body
#           v2 la POST /payments/{payment_id}/refund
@router.post("/payments/{payment_id}/refund", status_code=201)
def create_refund(payment_id: str, body: RefundCreate):
    """Hoan tien cho mot giao dich."""
    payment = payments_db.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment["status"] == "refunded":
        raise HTTPException(status_code=409, detail="Payment already refunded")

    ref_id = new_id("ref")
    record = {
        "id": ref_id,
        "payment_id": payment_id,
        "amount": payment["amount"],
        "status": "refunded",
        "reason": body.reason,
        "created_at": now(),
    }
    refunds_db[ref_id] = record
    payments_db[payment_id]["status"] = "refunded"
    return record
