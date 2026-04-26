from fastapi import FastAPI
from routers import payments, refunds

app = FastAPI(
    title="Payment API",
    version="1.0.0",
    description="API thanh toán phiên bản 1",
)

app.include_router(payments.router, prefix="/api/v1", tags=["Payments"])
app.include_router(refunds.router,  prefix="/api/v1", tags=["Refunds"])


@app.get("/", include_in_schema=False)
def root():
    return {"api": "Payment API", "version": "1.0.0", "docs": "/docs"}
