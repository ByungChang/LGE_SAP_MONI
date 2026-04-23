from fastapi import FastAPI

from app.api.alerts import router as alerts_router

app = FastAPI(
    title="SAP AI Monitoring Supervisor",
    version="0.1.0",
)

app.include_router(alerts_router, prefix="/api")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
