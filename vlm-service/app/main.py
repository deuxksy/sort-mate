"""VLM 마이크로서비스 메인 엔트리포인트."""

from fastapi import FastAPI
from loguru import logger

app = FastAPI(
    title="Waste Helper VLM Service",
    description="AI 기반 폐기물 분류 VLM 마이크로서비스",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "healthy", "service": "vlm-service"}


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("VLM Service starting up...")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("VLM Service shutting down...")
