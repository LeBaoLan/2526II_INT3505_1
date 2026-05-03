from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routers import payments, refunds

app = FastAPI(
    title="Payment API",
    version="2.0.0",
    description="API thanh toan phien ban 2",
)


# Middleware: moi request den /api/v1/ tra ve 410 Gone + huong dan migrate
@app.middleware("http")
async def block_v1(request: Request, call_next):
    if request.url.path.startswith("/api/v1/"):
        return JSONResponse(
            status_code=410,
            content={
                "error": "API v1 da ngung hoat dong",
                "message": "Vui long chuyen sang v2",
                "migration_guide": "https://docs.example.com/migrate-v2",
            }
        )
    return await call_next(request)


app.include_router(payments.router, prefix="/api/v2", tags=["Payments"])
app.include_router(refunds.router,  prefix="/api/v2", tags=["Refunds"])


@app.get("/", include_in_schema=False)
def root():
    return {"api": "Payment API", "version": "2.0.0", "docs": "/docs"}
