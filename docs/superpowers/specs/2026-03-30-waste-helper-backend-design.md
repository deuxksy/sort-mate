# 내 손안의 AI 폐기물 처리 도우미 — Backend 설계 문서

> 작성일: 2026-03-30
> 상태: Draft → Approved

## 1. 프로젝트 개요

**목적**: 일반 시민이 스마트폰 카메라로 폐기물을 촬영하면, AI가 실시간 분류하고 지역별 분리배출 요령·비용·수거일정을 안내하는 모바일 앱 + 백엔드 시스템.

**핵심 가치**:
- 온디바이스 YOLO로 실시간 1차 분류 (오프라인 동작 보장)
- VLM 기반 상세 분석 (배출 요령, 지역 규정, 비용 안내)
- 공공데이터 + LLM 하이브리드로 정확한 지역별 정보 제공

## 2. 시스템 아키텍처

```
┌─────────────┐    WiFi/5G    ┌──────────────────┐    gRPC/REST    ┌─────────────────┐
│  React Native │ ──────────▶ │  JHipster API     │ ────────────▶ │  VLM Service      │
│  Mobile App   │            │  Server (Spring)   │              │  (Qwen3-VL-4B)   │
│  - YOLO TFLite │◀──────────│  - REST API        │◀─────────────│  - vLLM runtime   │
└─────────────┘  result     └──────────────────┘  detail info   └─────────────────┘
      │                          │          ▲                                  ▲
      │ classification           │          │                                  │
      │ result (tiny payload)    │          │                                  │
      │                          ▼          │                                  │
                        ┌──────────────┐  │  ┌──────────────┐
                        │  PostgreSQL   │──┘  │  Vector DB    │
                        │  (영구 저장)   │     │  (Milvus)     │
                        └──────────────┘     └──────────────┘
                               ▲
                        ┌──────┴──────┐
                        │   Redis      │
                        │  (캐시/세션) │
                        └─────────────┘
```

### 핵심 원칙

- **Edge-First**: YOLO 온디바이스 1차 분류 → 네트워크 트래픽 최소화
- **VLM은 독립 마이크로서비스**: JHipster API 서버에서 gRPC로 호출, 장애 격리
- **게스트 우선**: 인증 없이 분류 가능, 히스토리/즐겨찾기만 로그인 필요

## 3. 모바일 앱 (React Native)

### 기술 스택

- React Native + TypeScript
- YOLO → TFLite 변환 → 온디바이스 추론
- 상태관리: Zustand
- 네비게이션: React Navigation
- 타겟: iOS + Android

### YOLO 모델 사양

| 항목 | 값 |
|------|-----|
| 모델 | YOLOv8n (320x320 input) |
| 클래스 수 | 50개 (플라스틱, 종이, 캔, 유리, 비닐, 스티로폼, 음식물, 대형폐기물, 의류, 전자제품, 배터리, 형광등, 의약품, 폐유, 고철 등) |
| mAP@0.5 목표 | > 85% |
| 모델 크기 | < 20MB (TFLite 양자화) |
| 추론 속도 | < 100ms (Snapdragon 8 Gen2 기준) |
| 업데이트 | 앱 스토어 업데이트로 모델 교체 (분기 1회), 향후 OTA 다운로드 검토 |

### 화면 구성

| 화면 | 설명 | 인증 |
|------|------|------|
| 카메라 | 실시간 YOLO 감지 오버레이 + 분류 결과 표시 | 게스트 |
| 상세 결과 | VLM 상세 분석 (배출 요령, 비용, 지역 정보) | 게스트 |
| 검색 히스토리 | 최근 분류 기록 목록 | 로그인 |
| 지역 설정 | 시/군/구 선택 → 공공데이터 API 연동 | 로그인 |
| 즐겨찾기 | 자주 보는 폐기물 분류 북마크 | 로그인 |
| 설정 | 알림, 지역, 계정 관리 | 로그인 |

### 데이터 흐름

```
카메라 프레임 → YOLO TFLite (로컬)
    → 1차 분류 결과 (예: "플라스틱", 신뢰도 95%)
    → [사용자 탭] 상세 보기 요청
    → JHipster API 호출 (분류 결과 + 크롭 이미지 전송)
    → VLM 상세 분석 응답
```

- **오프라인 동작**: YOLO 1차 분류는 네트워크 없이도 동작
- **캐시 전략**: 동일 분류 결과는 Redis 캐시에서 즉시 반환 (TTL 24h)
- **추론 실패 폴백**: YOLO confidence < 70% 시 "분류 불확실" 표시 → 사용자가 VLM 상세 분석 선택 가능

## 4. JHipster API 서버

### 기술 스택

- JHipster 8 (Spring Boot 3.x + JDL 기반 엔티티 생성)
- Java 21 + Gradle
- Spring Security + JWT (게스트는 익명 토큰)
- Spring Cloud OpenFeign (공공데이터 API 호출)

### 도메인 모델 (JDL)

```jdl
entity User {
  username(String)
  email(String)
  imageUrl(String)
  langKey(String)
}

entity WasteClassification {
  detectedClass(String) required
  confidence(Float) required
  imageUrl(String)
  detailResult(TextJson)
  classifiedAt(Instant) required
}

entity Region {
  sido(String)
  sigungu(String)
  emdName(String)
  emdCode(String)
}

entity DisposalGuide {
  wasteType(String) required
  disposalMethod(TextJson) required
  region(Region)
  source(String) // "PUBLIC_API" | "LLM_GENERATED" | "LLM_SUPPLEMENTED"
}

entity SearchHistory {
  query(String)
  resultSummary(TextJson)
  classifiedAt(Instant) required
  user(User)
}

entity FavoriteRegion {
  user(User)
  region(Region) required
}

entity NotificationSetting {
  user(User)
  enabled(Boolean)
  fcmToken(String)
}

entity WasteImage {
  originalUrl(String)
  thumbnailUrl(String)
  classification(WasteClassification)
}

entity Feedback {
  classification(WasteClassification)
  isAccurate(Boolean)
  correctedClass(String)
  comment(String)
  user(User)
}

relationship ManyToOne { WasteClassification(user) }
relationship ManyToOne { WasteImage(classification) }
relationship ManyToOne { SearchHistory(user) }
relationship OneToMany { Region(disposalGuide) }
relationship ManyToOne { FavoriteRegion(user) }
relationship ManyToOne { FavoriteRegion(region) }
relationship ManyToOne { Feedback(user) }
relationship ManyToOne { Feedback(classification) }
relationship ManyToOne { NotificationSetting(user) }
```

### API 엔드포인트

| Method | Path | 설명 | Auth |
|--------|------|------|------|
| POST | /api/v1/classify/detail | VLM 상세 분석 요청 | Guest |
| GET | /api/v1/disposal-guide | 폐기물별 배출 요령 조회 | Guest |
| GET | /api/v1/regions | 지역 목록 | Guest |
| GET | /api/v1/regions/{code}/schedule | 수거 일정 | Guest |
| POST | /api/v1/search-histories | 검색 기록 저장 | User |
| GET | /api/v1/search-histories | 내 검색 기록 | User |
| POST | /api/v1/feedbacks | 분류 피드백 | User |
| POST | /api/v1/auth/guest | 게스트 토큰 발급 | Public |
| POST | /api/v1/auth/social | 소셜 로그인 (Kakao/Naver/Google) | Public |

### VLM 서비스 연동 (gRPC)

**Proto 정의** (`vlm_service.proto`):
```protobuf
syntax = "proto3";

service VLMInference {
  rpc AnalyzeWaste(AnalyzeRequest) returns (AnalyzeResponse);
}

message AnalyzeRequest {
  bytes image_data = 1;       // JPEG/PNG 바이너리
  string yolo_class = 2;     // YOLO 1차 분류 결과
  float confidence = 3;      // YOLO 신뢰도
  string region_code = 4;    // 법정동코드
}

message DisposalMethod {
  string method = 1;
  repeated string notes = 2;
  repeated DisposalItem items = 3;
}

message DisposalItem {
  string label = 1;
  string action = 2;
}

message AnalyzeResponse {
  string waste_type = 1;           // 최종 분류
  DisposalMethod disposal_method = 2; // 배출 방법 (JSON)
  string cost_info = 3;           // 비용 정보
  string warnings = 4;           // 주의사항
  float confidence = 5;           // VLM 신뢰도
}
```

### API 계약 (OpenAPI/Swagger)

**POST /api/v1/classify/detail** — VLM 상세 분석 요청

```yaml
# Request ( multipart/form-data )
image: binary file               # 크롭 이미지 (max 5MB)
yoloResult:                          # JSON
  detectedClass: "플라스틱"
  confidence: 0.95
  bbox: [120, 80, 280, 200]
regionCode: "11500101"             # 선택, 법정동코드

# Response 200
classification:
  detectedClass: "플라스틱 (페트병)"
  confirmedClass: "PET 병"
  confidence: 0.92
disposalMethod:
  method: "내용물을 헹궈어 라벨과 뚜껑을 제거 후 배출"
  notes: ["뚜껑이 남아있으면 일반 종량 배출", "부착물이 있으면 부착분 배출"]
  items:
    - label: "뚜껑"
      action: "제거"
    - label: "부착물"
      action: "부창분 배출"
costInfo:
  type: "무료"
  amount: 0
  currency: "KRW"
  collectionSchedule: "매주 화요일"
  notes: null
warnings:
  - "열탄제를 사용한 적은 횟수는 있는 경우 안전하게 비우세요"
regionSpecific:
  emdName: "역삼동"
  notes: "종이컵은 화장실 지정. 종량 배출 가능"
source: "VLM_ANALYSIS"
# regionCode 미전송 시 응답:
# regionSpecific: null  # "지역 정보가 없습니다. 기본 배출 요령을 확인하세요."
cached: false

# Response 429
error: "RATE_LIMIT_EXCEEDED"
detail: "일일 요청 한도 초과. 내일 다시 시도해주세요."
retryAfter: 3600

# Response 503
error: "VLM_SERVICE_ERROR"
detail: "VLM 서비스 일시적 오류. YOLO 결과만 표시됩니다."
fallbackResult:
  detectedClass: "플라스틱"
  confidence: 0.95
  source: "YOLO_ONLY"

# Response 400
error: "INVALID_REQUEST"
detail: "지원하지 않는 이미지 형식입니다."
```

### 페이지네이션 (히스토리 조회)

```
GET /api/v1/search-histories?page=0&size=20&sort=classifiedAt,desc
```

### 에러 응답 표준

```json
{
  "error": "ERROR_CODE",
  "detail": "상세 메시지",
  "timestamp": "2026-03-30T10:00:00Z",
  "requestId": "uuid"
}
```

### 연동 세부사항

- **전송 방식**: multipart/form-data (이미지 바이너리 + 메타데이터 JSON)
- **응답 캐싱**: 동일 분류+지역 조합은 Redis TTL 24h 캐시
- **Vector DB**: VLM 응답 임베딩 저장 → 유사 질문 시 캐시 hit
- **API 버전 관리**: URL 경로에 `/v1/` prefix, Breaking change 시 `/v2/` 추가, 기존 버전 최소 6개월 유지(deprecated 안내), N+1 릴리스 시 N-1 버전 shutdown 3개월 전 예고

## 5. VLM 서비스 (Qwen3-VL-4B)

### 기술 스택

- Python FastAPI + gRPC 서버
- Qwen3-VL-4B + vLLM 런타임
- K8s Deployment (GPU 파드)

### K8s 배포

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vlm-service
  namespace: waste-helper
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: vlm-service
        image: vlm-service:latest
        resources:
          requests:
            nvidia.com/gpu: 1
          limits:
            nvidia.com/gpu: 1
        env:
        - name: MODEL_NAME
          value: "Qwen/Qwen3-VL-4B"
        - name: VLLM_MAX_MODEL_LEN
          value: "4096"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: vlm-service
  namespace: waste-helper
spec:
  ports:
  - port: 8000
    name: http
  - port: 50051
    name: grpc
  selector:
    app: vlm-service
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vlm-hpa
  namespace: waste-helper
spec:
  minReplicas: 1
  maxReplicas: 3
  metrics:
  # K8s HPA는 GPU 메트릭을 네이티브 지원하지 않으믛 Prometheus Adapter 필요
  - type: Pods
    pods:
      metric:
        name: vlm_request_queue_depth  # vLLM custom metric (Prometheus)
      target:
        type: AverageValue
        averageValue: "5"
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### VLM 프롬프트 파이프라인

```
입력: 이미지 + YOLO 1차 분류 결과
  ↓
시스템 프롬프트 구성:
  - 역할: 한국 폐기물 분리배출 전문가
  - 컨텍스트: 사용자 지역({region}) 기준 배출 규정
  - 태스크: 분류 확인 + 배출 요령 + 비용 안내
  ↓
VLM 추론 (Qwen3-VL-4B)
  ↓
출력: JSON (분류, 배출법, 주의사항, 비용, 지역 특이사항)
```

### 모델 확장 경로

| 단계 | 모델 | GPU 요구 | 시점 |
|------|------|---------|------|
| MVP | Qwen3-VL-4B | 1x GPU (8GB VRAM) | 초기 런칭 |
| v2 | Qwen3-VL-8B | 1x GPU (16GB VRAM) | 사용자 피드백 기반 정확도 개선 |
| v3 | Qwen3-VL-30B | 2x GPU (A100 40GB) | 대규모 서비스 |

## 6. 인프라 (Proxmox K8s)

### 클러스터 구성 (3~5노드)

| 노드 | 역할 | vCPU | RAM | Storage | GPU |
|------|------|------|-----|---------|-----|
| master-1 | Control Plane | 4 | 8GB | 100GB SSD | - |
| worker-1 | API + DB | 8 | 32GB | 500GB SSD | - |
| worker-2 | VLM Service | 8 | 32GB | 200GB SSD | 1x RTX 3060 (12GB) |
| worker-3 *(옵션)* | API 복제 + Redis | 8 | 16GB | 200GB SSD | - |
| worker-4 *(옵션)* | VLM 복제 | 8 | 32GB | 200GB SSD | 1x GPU |

### 네트워크 (Proxmox SDN)

```
Proxmox Host
  ├── vmbr0 (외부 네트워크)
  │     └── pfSense/OPNsense VM (라우터 + 방화벽)
  │           ├── WAN: 공인 IP
  │           └── VLAN 10: 10.10.0.0/24 (K8s 클러스터)
  ├── vmbr1 (내부 스토리지 네트워크)
  │     └── NFS Server (Longhorn 백엔드)
  └── vmbr2 (관리 네트워크)
        └── Proxmox GUI, SSH 점프 호스트
```

### K8s 네임스페이스

```
waste-helper/
  ├── api-server        (JHipster, 2 replicas)
  ├── vlm-service        (Qwen3-VL-4B, 1~3 replicas + HPA)
  ├── postgres           (PostgreSQL 16, PVC 50Gi)
  ├── redis              (Redis 7, Sentinel 모드)
  ├── milvus             (Vector DB, etcd + MinIO 백엔드)
  ├── ingress-nginx      (Ingress Controller + Let's Encrypt)
  └── monitoring         (Prometheus + Grafana + Loki)
```

### GitOps (ArgoCD)

```
GitHub repo
  ├── /k8s/manifests/     # K8s 매니페스트
  ├── /k8s/helm/          # Helm 차트
  └── /k8s/argocd/        # ArgoCD Application 정의
       └── ArgoCD가 자동 감지 → 클러스터에 배포
```

### 백업 전략

- PostgreSQL: pg_dump 일일 + S3 호환 스토리지(MinIO) 업로드
- Vector DB: Milvus 백업 도구 주간 스냅샷
- K8s etcd: 자동 스냅샷 5분 간격

## 7. 데이터 레이어

### PostgreSQL — 영구 저장

```sql
users                    -- 사용자 계정 (게스트 익명 포함)
regions                  -- 시/도/군/구 코드 + 공공데이터 메타
disposal_guides          -- 폐기물 배출 요령 (공공데이터 + LLM 보완)
waste_classifications    -- 분류 기록 (1차 YOLO + 2차 VLM 결과)
search_histories         -- 검색 히스토리
favorite_regions         -- 즐겨찾는 지역
notification_settings    -- 알림 설정 (수거일, 비용 변동 등)
feedbacks                -- 분류 정확도 피드백 (모델 개선용)
```

### Redis — 캐시 + 세션

```
session:{token}          → 사용자 정보 (TTL: 7d)
classify:{hash}          → VLM 상세 분석 결과 (TTL: 24h)
guide:{region}:{type}    → 배출 요령 JSON (TTL: 7d)
ratelimit:{ip}           → 분당 요청 수 (분류 30/min, 상세 10/min)
```

### Milvus — Vector DB

```
Collection: waste_embeddings
  - id: UUID
  - embedding: float[1024]    -- VLM 출력 임베딩
  - metadata: {
      waste_type, confidence, region,
      vlm_response_summary, created_at
    }

용도:
  1. 유사 폐기물 분류 검색 → 캐시 히트율 향상
  2. 사용자 피드백 기반 임베딩 클러스터링 → 모델 개선 데이터
```

### 데이터 소스 연동

```
공공데이터포털 API
  ├── 환경부_생활폐기물배출정보  → disposal_guides
  ├── 지자체_분리배출기준       → disposal_guides (지역별)
  └── 대형폐기물수거신청       → disposal_guides (비용)

연동 방식:
  Spring Batch 스케줄러 → 주간 동기화
  → 신규/변경 데이터 감지
  → DisposalGuide upsert
  → source = "PUBLIC_API"
  → LLM으로 누락 필드 보완 시 source = "LLM_SUPPLEMENTED"
```

## 8. 장애 격리 및 폴백

| 장애 상황 | 동작 | 사용자 경험 |
|----------|------|-----------|
| VLM 서비스 다운 | Circuit Breaker Open → YOLO 결과만 반환 | "상세 분석 일시 중단" 안내 |
| Redis 다운 | DB 직접 조회 (성능 저하) | 응답 지연, 캐시 미사용 안내 |
| 공공데이터 API 장애 | 7일 캐시 사용 | "최신 정보가 아닐 수 있음" timestamp 표시 |
| Vector DB 다운 | 임베딩 없이 직접 VLM 호출 | 응답 속도 저하, 기능은 정상 |
| PostgreSQL 다운 | Circuit Breaker + 503 반환 | "일시적 서비스 장애" 안내 |
| K8s 파드 장애 | 자동 재시작 (readiness/liveness probe) | 사용자 인지 불가 |

### Circuit Breaker 설정

```yaml
resilience4j:
  circuitbreaker:
    instances:
      vlm-service:
        failureRateThreshold: 50
        waitDurationInOpenState: 30s
        permittedNumberOfCallsInHalfOpenState: 3
        slidingWindowSize: 10
      public-data-api:
        failureRateThreshold: 30
        waitDurationInOpenState: 60s
  retry:
    instances:
      vlm-service:
        maxAttempts: 2
        waitDuration: 1s
      public-data-api:
        maxAttempts: 3
        waitDuration: 2s
```

## 9. 성능 목표 (SLA)

| 지표 | 목표 | 측정 방식 |
|------|------|----------|
| API 응답 시간 P50 | < 200ms | Prometheus histogram |
| API 응답 시간 P95 | < 500ms | Prometheus histogram |
| API 응답 시간 P99 | < 2s | Prometheus histogram |
| VLM 추론 시간 P95 | < 3s | vLLM metrics |
| YOLO 온디바이스 추론 | < 100ms | 클라이언트 측정 |
| 가용성 | 99.5% (월간) | K8s uptime probe |
| 동시 사용자 (초기) | 100명 | HPA 메트릭 |
| 동시 사용자 (확장) | 1,000명 | HPA 메트릭 |
| Redis 캐시 적중률 | > 70% | Redis INFO keyspace_hits/misses |

## 10. Observability (모니터링)

### 로그 포맷 (JSON — Loki 적재)

```json
{
  "timestamp": "2026-03-30T10:00:00Z",
  "level": "INFO",
  "service": "api-server",
  "traceId": "abc123",
  "spanId": "def456",
  "userId": "guest_device123",
  "action": "classify_detail",
  "latencyMs": 245,
  "success": true,
  "metadata": {
    "wasteClass": "플라스틱",
    "region": "11680101",
    "cacheHit": false
  }
}
```

### 핵심 메트릭 (Prometheus)

| 메트릭명 | 유형 | 설명 |
|---------|------|------|
| api_server_request_duration_seconds | histogram | API 응답 시간 |
| vlm_inference_duration_seconds | histogram | VLM 추론 시간 |
| redis_cache_hit_ratio | gauge | 캐시 적중률 |
| db_connection_pool_active | gauge | DB 커넥션 풀 |
| classification_requests_total | counter | 분류 요청 수 |
| feedback_submissions_total | counter | 피드백 제출 수 |

### Grafana 대시보드 패널

- **API Overview**: 응답 시간 P50/P95/P99, 에러율, RPS
- **VLM Performance**: 추론 시간, GPU 활용률, 큐 길이
- **Cache Efficiency**: Redis hit ratio, 캐시 크기
- **Business**: 일별 분류 수, 피드백 정확도, 지역별 사용량

### 알림 규칙 (Alertmanager)

| 규칙 | 조건 | 심각도 | 채널 |
|------|------|--------|------|
| API 5xx Rate | > 1% (5분 윈도우) | P1 | Pushover |
| VLM P95 Latency | > 5s (5분 윈도우) | P2 | Pushover |
| Pod CrashLoopBackOff | 발생 시 | P1 | Pushover |
| GPU 메모리 부족 | > 90% 사용률 | P2 | Pushover |
| DB 커넥션 풀 고갈 | 활성 연결 > 80% 최대 | P2 | Pushover |
| 디스크 사용량 | > 85% | P3 | Pushover |

## 11. 보안

### 인증 흐름

```
앱 실행 → 게스트 토큰 발급 (POST /api/v1/auth/guest)
       → deviceId 검증 (UUID v4 + fingerprint hash)
       → 익명 JWT (role: GUEST, deviceId 기반)
       → 분류 API 즉시 사용 가능
            │
            ▼ [사용자가 "히스토리 저장" 등 선택 시]
       소셜 로그인 (POST /api/v1/auth/social)
       → Kakao/Naver/Google OAuth2 (PKCE 플로우)
       → 정식 JWT (role: USER, 기존 게스트 데이터 마이그레이션)
```

### JWT 구성

```
게스트 토큰: { sub: deviceId, role: GUEST, exp: 7d }
유저 토큰:  { sub: userId, role: USER, exp: 30d, refresh: 90d }

Redis 세션(session:{token})은 JWT와 동일 TTL 유지:
  - 게스트: session:{guest_jwt} TTL 7d (JWT 만료와 동기화)
  - 유저: session:{user_jwt} TTL 30d (refresh 시 갱신)
  - 목적: 토큰 블랙리스트, rate limit 카운터, 즉시 로그아웃 처리
```

### deviceId 보안 검증

- **포맷**: UUID v4 필수 (`^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`)
- **스푸핑 방지**: 동일 IP에서 분당 10회 초과 시 429
- **디바이스 지문**: `sha256(userAgent + screenResolution + timezone)` → fingerprint_hash

### OAuth2 소셜 로그인 상세

| Provider | Scope | Token Endpoint | PKCE |
|----------|-------|---------------|------|
| Kakao | profile, account_email | /oauth/token | 필수 |
| Naver | profile, email | /oauth2.0/token | 권장 |
| Google | openid, profile, email | /token | 필수 |

- **Token 갱신**: Refresh Token은 HttpOnly Secure Cookie에 저장, 자동 갱신
- **계정 연동**: 동일 이메일로 여러 소셜 로그인 시 계정 자동 병합

### 게스트 → 유저 데이터 마이그레이션

```sql
-- device_users 매핑 테이블
CREATE TABLE device_users (
  id BIGSERIAL PRIMARY KEY,
  device_id VARCHAR(255) UNIQUE NOT NULL,
  user_id BIGINT REFERENCES users(id),
  fingerprint_hash VARCHAR(64) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 마이그레이션 절차 (트랜잭션)
BEGIN;
  1. 소셜 로그인 완료 후 deviceId로 device_users 조회
  2. UPDATE waste_classifications SET user_id = :userId
     WHERE user_device_id = :deviceId AND user_id IS NULL;
  3. UPDATE search_histories SET user_id = :userId
     WHERE user_device_id = :deviceId AND user_id IS NULL;
  4. UPDATE device_users SET user_id = :userId WHERE device_id = :deviceId;
COMMIT;

-- 다중 디바이스: 이미 user_id가 있으면 device_users 매핑만 추가
```

### 보안 조치

| 영역 | 조치 |
|------|------|
| API Gateway | Spring Cloud Gateway → Rate Limiting, IP 블랙리스트 |
| 이미지 업로드 | 최대 10MB, 해상도 제한 4096x4096, HEIC/AVIF 차단, EXIF 메타데이터 제거 |
| VLM 요청 | 게스트 30회/일, 유저 100회/일 제한 |
| 이미지 보안 | DoS 방지: 업로드 속도 제한 1회/3초, 악성 콘텐츠 필터링(NSFW 차단) |
| 데이터 보호 | 이미지 분석 후 서버 임시 파일 즉시 삭제 (TTL 1h) |
| 네트워크 | K8s NetworkPolicy — VLM 파드는 API 서버에서만 접근 가능 |
| 시크릿 관리 | Vault/K8s Secrets → DB 비밀번호, OAuth client secret |
| 컨테이너 | Trivy 이미지 스캔, non-root 컨테이너 실행 |
| 감사(Audit) | 분류 API 호출 로그 → Loki 적재, 90일 보관 |

## 15. 결정사항 요약

| 항목 | 결정사항 |
|------|---------|
| 프로젝트명 | 내 손안의 AI 폐기물 처리 도우미 |
| 타겟 사용자 | 일반 시민, 분리배출 헬퍼 |
| 모바일 | React Native (iOS + Android), YOLO TFLite 온디바이스 |
| API 서버 | JHipster 8 (Spring Boot 3.x), Java 21 |
| VLM | Qwen3-VL-4B, vLLM, K8s 독립 마이크로서비스 (gRPC) |
| 인증 | 게스트 우선 + 선택적 소셜 로그인 (Kakao/Naver/Google) |
| DB | PostgreSQL + Redis + Milvus (Vector DB) |
| 데이터 | 공공데이터포털 API + LLM 하이브리드 보완 |
| 인프라 | Proxmox K8s 3~5노드, ArgoCD GitOps |
| 확장 | 4B→8B→30B, 1→3 replica, HPA 오토스케일링 |

## 12. 테스트 전략

### 단위 테스트 (각 서비스 독립)

| 계층 | 도구 | 커버리지 | 예시 |
|------|------|---------|------|
| API 서버 | JUnit 5 + Mockito | Service, Repository, Controller | `WasteClassificationService.classifyDetail()` |
| VLM 연동 | WireMock (Feign) | VLM 응답 파싱, 오류 케이스 | gRPC 타임아웃, 서버 오류, 빈 응답 |
| 공공데이터 API | WireMock | API 장애/지연/데이터 포맷 변경 | XML 응답, 503 타임아웃 |
| DB | Testcontainers (PostgreSQL) | 엔티티 CRUD, 제약조건 | unique 제약, 외래키 검증 |

### 통합 테스트 (E2E)

| 시나리오 | 도구 | 설명 |
|--------|------|------|
| 분류 전체 흐름 | Testcontainers + REST Assured | YOLO 결과 → API → VLM Mock → 응답 검증 |
| 게스트 → 유저 전환 | Testcontainers | 게스트 분류 → 소셜 로그인 → 히스토리 마이그레이션 검증 |
| 캐시 동작 | Testcontainers + Redis | 최초 요청 → DB 조회, 재요청 → Redis hit |
| Rate Limiting | REST Assured | 한계 초과 → 429 응답 확인 |
| 인증 만료 | REST Assured | 만료 토큰 → 401, 잘못된 토큰 → 401 |

### 모델 정확도 평가

| 항목 | 방식 | 기준 |
|------|------|------|
| YOLO | 테스트셋 500장 (수동 라벨링) | mAP@0.5 > 85%, 클래스별 recall > 80% |
| VLM | 사용자 피드백 기반 | 긍정 피드백 비율 > 90% |
| 전체 | A/B 테스트 (rule-based vs VLM) | VLM 승률 > 95% |

## 13. 배포 단계 (Phasing)

### Phase 1: MVP (4주)

- **목표**: 핵심 분류 + 배출 요령 제공
- **배포**: JHipster API + PostgreSQL + Redis (단일 파드), VLM 단일 GPU 파드
- **기능**: YOLO 분류 → VLM 상세 분석 → 배출 요령 (공공데이터만)
- **모니터링**: 기본 Prometheus + Grafana
- **인프라**: K8s 3노드 (master-1 + worker-1 + worker-2)

### Phase 2: 소셜 로그인 + 히스토리 (2주)

- **기능**: Kakao/Naver/Google 소셜 로그인, 검색 히스토리, 즐겨찾기
- **데이터**: 게스트→유저 마이그레이션, LLM 하이브리드 보완
- **인프라**: Vector DB(Milvus) 추가

### Phase 3: Vector DB + 고도화 (2주)

- **기능**: 유사 분류 캐시(임베딩 검색), 사용자 피드백 기반 모델 개선
- **인프라**: HPA 오토스케일링 (Custom Metrics: GPU 메모리 사용률), worker-3 추가
- **모델**: Qwen3-VL-4B → 8B 업그레이드 검토

### 롤백 전략

| 변경 | 롤백 방식 |
|------|---------|
| VLM 모델 업그레이드 | ArgoCD → 이전 이미지 태그로 rollback |
| API 서버 배포 | Blue/Green → 이전 버전으로 트래픽 전환 |
| DB 스키마 변경 | Flyway forward-only + 롤백 마이그레이션 스크립트 별도 관리 |
| K8s 매니페스트 | Git revert → ArgoCD 자동 동기화 |

## 14. 지역별 배출 요령 우선순위 로직

```
사용자 지역 + 폐기물 분류 결과
  │
  ▼ [1순위] 공공데이터 조회 (disposal_guides WHERE region=:code AND waste_type=:class)
  │   ├─ hit → 공공데이터 그대로 반환 (source: PUBLIC_API)
  │   └─ miss ↓
  ▼ [2순위] Vector DB 유사 검색 (Milvus similarity search, threshold: 0.85)
  │   ├─ hit → 캐시된 LLM 응답 반환 (source: VECTOR_CACHE)
  │   └─ miss ↓
  ▼ [3순위] VLM 실시간 추론 (Qwen3-VL-4B)
      → VLM 응답 반환 (source: VLM_REALTIME)
      → 응답 임베딩을 Vector DB에 저장
      → 공공데이터 누락 필드를 LLM으로 보완 (source: LLM_SUPPLEMENTED)
```

**우선순위 원칙**:
- 공공데이터가 있으면 LLM 사용하지 않음 (비용/속도/정확도)
- 공공데이터가 없으면 LLM이 생성하고 `disposal_guides`에 저장
- 이후 동일 요청은 Vector DB에서 캐시 hit
