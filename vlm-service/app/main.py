"""VLM 마이크로서비스 — FastAPI + gRPC."""

from fastapi import FastAPI

app = FastAPI(
    title="Waste Helper VLM Service",
    description="AI 기반 폐기물 분류 VLM 마이크로서비스",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "healthy", "service": "vlm-service"}
