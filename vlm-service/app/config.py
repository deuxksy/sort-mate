"""VLM 서비스 환경 설정."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_name: str = "Qwen/Qwen3-VL-4B"
    max_model_len: int = 4096
    gpu_memory_utilization: float = 0.9
    trust_remote_code: bool = True
    grpc_port: int = 50051
    http_port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
