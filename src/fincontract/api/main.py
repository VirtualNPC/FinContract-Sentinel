from fastapi import FastAPI

from fincontract.api.routes import audit, health
from fincontract.core.config import settings
from fincontract.core.logging import configure_logging

configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name, version="0.1.0")

app.include_router(health.router, tags=["health"])
app.include_router(audit.router, prefix="/audit", tags=["audit"])


@app.get("/")
def root() -> dict:
    return {"status": "ok", "service": settings.app_name}


def run() -> None:
    import uvicorn

    uvicorn.run(
        "fincontract.api.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.is_dev,
    )
