FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proto 컴파일
COPY proto/vlm_service.proto ./proto/
RUN python -m grpc_tools.protoc \
    -I. \
    --python_out=./app \
    --grpc_python_out=./app \
    proto/vlm_service.proto

# 앱 코드
COPY app ./app

EXPOSE 50051 8000

CMD ["python", "-m", "app.main"]
