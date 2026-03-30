# 내 손안의 AI 폐기물 처리 도우미 - Backend

> **sort-mate** — React Native 앱을 위한 백엔드 시스템

## 구조

```
kl/
├── api-server/          # JHipster API 서버 (Spring Boot 3.x, Gradle)
├── vlm-service/         # VLM 마이크로서비스 (FastAPI + gRPC, Qwen3-VL-4B)
├── k8s/                 # Kubernetes 매니페스트 & Helm Chart
│   ├── manifests/       # K8s raw manifests
│   ├── helm/            # Helm Chart
│   └── argocd/          # ArgoCD Application
├── docs/                # 설계 문서
└── README.md
```

## 기술 스택

| Component | Technology |
|-----------|------------|
| API Server | Spring Boot 3.x, JHipster 9, Java 21, Gradle |
| Database | PostgreSQL |
| Cache | Redis |
| Auth | JWT |
| VLM Service | Python 3.12, FastAPI, gRPC |
| AI Model | Qwen3-VL-4B |
| Infra | Proxmox Kubernetes, ArgoCD |

## 로컬 개발

### API 서버

```bash
cd api-server
./gradlew bootRun
```

### VLM 서비스

```bash
cd vlm-service
docker build -t vlm-service:latest .
docker run -p 50051:50051 vlm-service:latest
```

## 문서

- [Backend 설계 문서](docs/superpowers/specs/2026-03-30-waste-helper-backend-design.md)
