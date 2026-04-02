# waste-helper 시스템 아키텍처

> Phase 1 기준 — 전체 시스템 아키텍처 다이어그램

---

## 1. 전체 시스템 아키텍처

```mermaid
graph TB
    subgraph Client["📱 Client"]
        Camera["📷 Camera<br/>expo-image-picker"]
        App[" waste-helper App<br/>Expo SDK 54 + expo-router v6"]
    end

    subgraph K8s["☸️ Kubernetes Cluster (OrbStack / Proxmox)"]
        subgraph FE["🖥️ Frontend"]
            NginxFE["nginx<br/>Expo Web Static + API Proxy"]
        end

        subgraph API["🔧 API Server (JHipster)"]
            API1["api-server<br/>Spring Boot 3.x"]
            RateLimit["RateLimitFilter<br/>Bucket4j"]
            GrpcClient["gRPC Stub<br/>VLMInference"]
            Cache["Redis Cache<br/>TTL 24h"]
        end

        subgraph VLM["🤖 VLM Service"]
            VLM1["vlm-service<br/>gRPC Server"]
            VLMNote["Mock: Python gRPC<br/>Prod: Qwen3-VL-4B"]
        end

        subgraph Data["💾 Data Layer"]
            PG["PostgreSQL 16<br/>StatefulSet + PVC 10Gi"]
            Redis["Redis 7<br/>Cache & Session"]
        end
    end

    Camera -->|"이미지 촬영<br/>(웹: file input)"| App
    App -->|"POST /api/v1/classify/detail<br/>multipart/form-data"| NginxFE
    NginxFE -->|"proxy_pass /api/"| API1
    API1 --> RateLimit --> GrpcClient
    GrpcClient -->|"gRPC :50051<br/>AnalyzeWaste()"| VLM1
    VLM1 --> VLMNote
    API1 <-->|"조회/저장"| PG
    API1 <-->|"캐시"| Redis
```

---

## 2. 분류 요청 데이터 흐름

```mermaid
sequenceDiagram
    participant App as Mobile App
    participant YOLO as YOLO TFLite
    participant API as API Server
    participant Redis as Redis Cache
    participant VLM as VLM Service
    participant DB as PostgreSQL

    App->>YOLO: 카메라 프레임 입력
    YOLO-->>App: 1차 분류 (예: "플라스틱", 95%)
    Note over App: confidence ≥ 70% → 결과 표시

    App->>API: POST /api/v1/classify/detail<br/>(image + yoloResult + regionCode)
    API->>API: Rate Limit 체크 (Guest 30/일, User 100/일)
    API->>Redis: 캐시 조회 (classify:{hash})

    alt 캐시 HIT
        Redis-->>API: 캐시된 분석 결과
    else 캐시 MISS
        API->>VLM: gRPC AnalyzeWaste(image, yoloClass, region)
        VLM-->>API: AnalyzeResponse (분류, 배출법, 비용, 경고)
        API->>Redis: 결과 캐싱 (TTL 24h)
        API->>DB: 분류 기록 저장
    end

    API-->>App: 상세 분석 결과 JSON
```

---

## 3. K8s 네임스페이스 배포 구성

```mermaid
graph TB
    subgraph NS["Namespace: waste-helper"]
        subgraph Net["NetworkPolicy"]
            IngressCtrl["Ingress NGINX<br/>+ cert-manager"]
        end

        subgraph Apps["Applications"]
            APIDep["api-server Deployment<br/>replicas: 2"]
            APISvc["Service :8080"]
            VLMDep["vlm-service Deployment<br/>GPU: nvidia.com/gpu: 1"]
            VLMSvc["Service :50051 (gRPC)<br/>Service :8000 (http)"]
            HPA["HPA vlm-hpa<br/>min: 1, max: 3"]
        end

        subgraph Infra["Infrastructure"]
            PGSS["PostgreSQL StatefulSet<br/>PVC 10Gi"]
            PGSvc["Service :5432"]
            RedisDep["Redis Deployment"]
            RedisSvc["Service :6379"]
            Secret["Secret: postgres-secret<br/>(envsubst 관리)"]
        end

        subgraph Mon["Monitoring"]
            PromDep["Prometheus Deployment"]
            PromCfg["ConfigMap<br/>scrape targets"]
            GrafanaDep["Grafana Deployment"]
            GrafanaSvc["Service :3000"]
        end
    end

    IngressCtrl --> APISvc
    APISvc --> APIDep
    VLMSvc --> VLMDep
    HPA -.-> VLMDep
    APIDep --> PGSvc
    APIDep --> RedisSvc
    VLMDep -.->|"NetworkPolicy<br/>API Server만 접근 허용"| APIDep
    PGSvc --> PGSS
    RedisSvc --> RedisDep
    GrafanaDep -.-> PromDep
```

---

## 4. 인증 흐름

```mermaid
sequenceDiagram
    participant App as Mobile App
    participant API as API Server
    participant JWT as JWT Provider
    participant Redis as Redis Session
    participant OAuth as Social OAuth<br/>(Kakao/Naver/Google)

    rect rgb(240, 248, 255)
        Note over App,Redis: Guest Flow (인증 없이 분류 가능)
        App->>API: POST /api/v1/auth/guest<br/>{deviceId, fingerprint}
        API->>API: deviceId 검증 (UUID v4)
        API->>JWT: 익명 JWT 발급 {role: GUEST, exp: 7d}
        JWT-->>API: guest token
        API->>Redis: session:{token} TTL 7d
        API-->>App: Guest JWT
        App->>API: POST /api/v1/classify/detail<br/>Authorization: Bearer {guestJWT}
        API-->>App: 분류 결과 (정상)
    end

    rect rgb(255, 248, 240)
        Note over App,Redis: Social Login (히스토리/즐겨찾기 필요 시)
        App->>API: POST /api/v1/auth/social<br/>{provider, code, PKCE}
        API->>OAuth: Token + Profile 조회
        OAuth-->>API: 사용자 정보
        API->>JWT: 정식 JWT 발급 {role: USER, exp: 30d}
        API->>DB: 게스트 데이터 마이그레이션<br/>(waste_classifications, search_histories)
        API->>Redis: session:{token} TTL 30d
        API-->>App: User JWT
    end
```

---

## 5. 배출 요령 조회 우선순위

```mermaid
flowchart TD
    Req["분류 결과 + 지역 코드"] --> PG{PostgreSQL<br/>공공데이터 조회}

    PG -->|"HIT"| Return1["PUBLIC_API<br/>공공데이터 그대로 반환"]
    PG -->|"MISS"| Vec{"Vector DB<br/>유사 검색 threshold 0.85"}

    Vec -->|"HIT"| Return2["VECTOR_CACHE<br/>캐시된 LLM 응답 반환"]
    Vec -->|"MISS"| VLM["VLM 실시간 추론<br/>Qwen3-VL-4B"]

    VLM --> SaveVec["임베딩 → Vector DB 저장"]
    VLM --> Return3["VLM_REALTIME<br/>VLM 응답 반환"]
    VLM --> SavePG["공공데이터 누락 필드<br/>LLM 보완 → DB 저장"]

    style Return1 fill:#4CAF50,color:#fff
    style Return2 fill:#FF9800,color:#fff
    style Return3 fill:#F44336,color:#fff
```

---

## 6. Proxmox 클러스터 노드 구성

```mermaid
graph TB
    subgraph Proxmox["Proxmox Host"]
        subgraph Net["Network"]
            vmbr0["vmbr0 — 외부<br/>WAN: 공인 IP"]
            vmbr1["vmbr1 — 스토리지<br/>NFS (Longhorn)"]
            vmbr2["vmbr2 — 관리<br/>Proxmox GUI, SSH"]
        end

        subgraph Router["pfSense/OPNsense VM"]
            WAN["WAN"]
            VLAN10["VLAN 10: 10.10.0.0/24<br/>K8s Cluster"]
        end

        subgraph Nodes["K8s Nodes"]
            M1["master-1<br/>Control Plane<br/>4vCPU / 8GB / 100GB"]
            W1["worker-1<br/>API + DB<br/>8vCPU / 32GB / 500GB"]
            W2["worker-2<br/>VLM Service<br/>8vCPU / 32GB / 200GB<br/>RTX 3060 12GB"]
            W3["worker-3 (opt)<br/>API 복제 + Redis<br/>8vCPU / 16GB / 200GB"]
        end

        NFS["NFS Server<br/>(Longhorn Backend)"]
    end

    vmbr0 --> Router
    Router --> VLAN10
    VLAN10 --> M1 & W1 & W2 & W3
    vmbr1 --> NFS
    W2 ---|"GPU Passthrough"| GPU["🖥️ RTX 3060"]
```

---

## 7. GitOps 배포 흐름

```mermaid
graph LR
    Dev["Developer<br/>git push"] --> GitHub["GitHub Repo<br/>deuxksy/waste-helper"]

    subgraph ArgoCD["ArgoCD"]
        Sync["Auto Sync"]
        Diff["Drift Detection"]
    end

    GitHub -->|"Webhook / Poll"| Sync
    Sync -->|"Apply Manifests"| K8s["K8s Cluster"]

    subgraph Repo["/k8s Directory"]
        Manifests["/manifests/<br/>K8s raw YAML"]
        Helm["/helm/<br/>Helm Chart"]
        App["/argocd/<br/>Application CRD"]
    end

    GitHub --- Repo
    App --> Sync
    Diff -->|"Git Diff"| GitHub
```

---

## 8. Frontend 아키텍처

```mermaid
graph TB
    subgraph Expo["Expo SDK 54 App"]
        Router["expo-router v6<br/>File-based Routing"]
        Tabs["(tabs)/<br/>Bottom Tab Navigator"]
        Classify["/classify/result<br/>분류 결과 상세"]
    end

    subgraph CameraModule["📷 Camera"]
        ImagePicker["expo-image-picker<br/>launchCameraAsync()"]
        WebFallback["Web: input[type=file]<br/>capture=environment"]
        Native["Native: 카메라 직접 제어"]
    end

    subgraph Services["Services"]
        APIClient["api.ts<br/>fetch + FormData"]
        ImageComp["image.ts<br/>expo-image-manipulator<br/>압축 + 리사이즈"]
    end

    subgraph Hooks["Hooks"]
        UseClassify["useClassify<br/>촬영 → 압축 → API → 결과"]
    end

    Router --> Tabs
    Tabs -->|"onCapture(uri)"| UseClassify
    UseClassify --> ImagePicker
    UseClassify --> ImageComp
    UseClassify --> APIClient
    ImagePicker --> WebFallback
    ImagePicker --> Native
    APIClient -->|"POST /api/v1/classify/detail<br/>multipart/form-data"| Nginx["nginx Proxy"]
    UseClassify -->|"result"| Classify
```

### Frontend 기술 스택

| 항목 | 기술 |
|------|------|
| Framework | Expo SDK 54, React Native 0.81 |
| Routing | expo-router v6 (file-based) |
| Styling | NativeWind v4 (Tailwind CSS) |
| Camera | expo-image-picker (웹/네이티크 호환) |
| 이미지 처리 | expo-image-manipulator (압축/리사이즈) |
| 상태 관리 | React Hooks (useClassify) |
| 웹 배포 | nginx (정적 파일 + API 프록시) |

### 웹 vs 네이티브 카메라 동작

| Platform | 동작 |
|----------|------|
| **웹 브라우저** | `<input type="file" capture="environment">` → OS 카메라 앱 호출 |
| **iOS/Android 앱** | `expo-image-picker` native 카메라 모듈 직접 실행 |

### nginx 프록시 설정

```nginx
# /api/ → API Server (K8s 내부 통신)
location /api/ {
    proxy_pass http://api-server:8080/api/;
    proxy_connect_timeout 10s;
    proxy_read_timeout 30s;
}
```

---

## 9. Mock VLM Service

개발 환경에서 실제 AI 모델(Qwen3-VL-4B) 없이 gRPC 응답을 테스트하기 위한 Mock 서비스.

```mermaid
graph LR
    API["API Server"] -->|"gRPC :50051<br/>AnalyzeWaste()"| Mock["mock-vlm<br/>Python gRPC Server"]
    Mock --> WASTE_DATA["WASTE_DATA dict<br/>plastic, glass, paper,<br/>metal, food_waste, general"]
    Health["Health Check<br/>Flask :8000"]
```

| Port | Protocol | 용도 |
|------|----------|------|
| 50051 | gRPC | AnalyzeWaste RPC |
| 8000 | HTTP | /health 엔드포인트 |

### Mock 응답 예시

```json
{
  "waste_type": "플라스틱",
  "disposal_method": {
    "method": "재활용 분리배출",
    "notes": ["라벨 제거 후 배출", "내용물 비우고 헹구기"],
    "items": [
      {"label": "본체", "action": "재활용"},
      {"label": "라벨", "action": "제거 후 일반 쓰레기"}
    ]
  },
  "confidence": 0.9
}
```
