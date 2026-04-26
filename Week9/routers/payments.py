from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from db import payments_db, new_id, now

router = APIRouter()


# ── Schema ──────────────────────────────────────────────

class PaymentCreate(BaseModel):
    amount: int = Field(..., example=150000, description="Số tiền (VND)")
    currency: str = Field("VND", example="VND")
    card_number: str = Field(..., example="4111111111111111")
    card_exp: str = Field(..., example="12/26")
    card_cvv: str = Field(..., example="123")
    description: Optional[str] = Field(None, example="Thanh toán đơn hàng #99")


# ── Endpoints ───────────────────────────────────────────

@router.post("/payments", status_code=201)
def create_payment(body: PaymentCreate):
    """Tạo một giao dịch thanh toán mới."""
    pay_id = new_id("pay")

    record = {
        "id": pay_id,
        "status": "success",
        "amount": body.amount,
        "currency": body.currency,
        "card_number": body.card_number,   # lưu raw — sẽ là vấn đề bảo mật
        "description": body.description,
        "created_at": now(),
    }
    payments_db[pay_id] = record
    return record


@router.get("/payments/{id}")
def get_payment(id: str):
    """Lấy chi tiết một giao dịch."""
    record = payments_db.get(id)
    if not record:
        raise HTTPException(status_code=404, detail="Payment not found")
    return record


@router.get("/payments")
def list_payments():
    """Lấy danh sách tất cả giao dịch."""
    return {"payments": list(payments_db.values())}
