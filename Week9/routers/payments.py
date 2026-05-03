from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Optional
from db import payments_db, new_id, now

router = APIRouter()


# Schema ─────────────────────────────────────────────────

class Amount(BaseModel):                          # THAY DOI: amount thanh object
    value: int = Field(..., example=150000)
    currency: str = Field("VND", example="VND")


class PaymentMethod(BaseModel):                   # THAY DOI: bo raw card, dung token
    type: str = Field("card", example="card")
    token: str = Field(..., example="tok_4111xxxx1111")


class PaymentCreate(BaseModel):
    amount: Amount
    payment_method: PaymentMethod
    description: Optional[str] = Field(None, example="Thanh toan don hang 99")


# Endpoints ──────────────────────────────────────────────

@router.post("/payments", status_code=201)
def create_payment(
    body: PaymentCreate,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    # THEM MOI: idempotency - neu key da ton tai thi tra lai record cu
    if idempotency_key:
        for record in payments_db.values():
            if record.get("idempotency_key") == idempotency_key:
                return record

    pay_id = new_id("pay")
    record = {
        "payment_id": pay_id,             # THAY DOI: "id" -> "payment_id"
        "status": "completed",            # THAY DOI: "success" -> "completed"
        "amount": {                       # THAY DOI: so nguyen -> object
            "value": body.amount.value,
            "currency": body.amount.currency,
        },
        "payment_method": body.payment_method.type,
        "description": body.description,
        "created_at": now(),              # THAY DOI: ISO 8601 day du (xem db.py)
        "idempotency_key": idempotency_key,
    }
    payments_db[pay_id] = record
    return record


# THAY DOI: {id} -> {payment_id}
@router.get("/payments/{payment_id}")
def get_payment(payment_id: str):
    record = payments_db.get(payment_id)
    if not record:
        raise HTTPException(status_code=404, detail="Payment not found")
    return record


@router.get("/payments")
def list_payments():
    return {"payments": list(payments_db.values())}
