"""모듈 직접 실행 진입점."""

import threading

import uvicorn

from .config import settings
from .grpc_server import serve
from .main import app

if __name__ == "__main__":
    grpc_thread = threading.Thread(target=serve, kwargs={"port": settings.grpc_port})
    grpc_thread.daemon = True
    grpc_thread.start()

    uvicorn.run(app, host="0.0.0.0", port=settings.http_port)
