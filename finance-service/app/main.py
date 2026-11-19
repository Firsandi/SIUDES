from fastapi import FastAPI

app = FastAPI(title="SIUDES Finance Service")


@app.get("/api/finance/health")
@app.get("/health")
async def health():
    return {
        "success": True,
        "data": {
            "status": "ok",
            "service": "finance-service",
        },
        "error": None,
    }
