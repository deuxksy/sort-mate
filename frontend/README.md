# Frontend — waste-helper

Expo SDK 54 기반 크로스 플랫폼 앱 (웹 / iOS / Android).

## 기술 스택

| 항목 | 기술 |
|------|------|
| Framework | Expo SDK 54, React Native 0.81 |
| Routing | expo-router v6 (file-based) |
| Styling | NativeWind v4 (Tailwind CSS) |
| Camera | expo-image-picker (웹/네이티브 호환) |
| 이미지 처리 | expo-image-manipulator |

## 구조

```
frontend/
├── app/                    # expo-router 페이지
│   ├── (tabs)/             # 하단 탭 네비게이션
│   │   ├── index.tsx       # 홈 — 카메라 촬영
│   │   ├── _layout.tsx     # 탭 레이아웃
│   │   └── explore.tsx     # 탐색
│   ├── classify/
│   │   └── result.tsx      # 분류 결과 상세
│   ├── _layout.tsx         # 루트 레이아웃
│   └── +not-found.tsx
├── components/
│   ├── camera/             # CameraView (expo-image-picker)
│   └── ui/                 # LoadingOverlay, ErrorMessage
├── hooks/                  # useClassify (촬영→압축→API→결과)
├── services/               # api.ts (fetch), image.ts (압축)
├── constants/              # config.ts, theme.ts
├── types/                  # TypeScript 타입
├── Dockerfile              # Expo Web 빌드 → nginx
└── tailwind.config.js
```

## 주요 플로우

```mermaid
graph LR
    A["탭하여 촬영"] --> B["expo-image-picker"]
    B --> C["이미지 압축<br/>expo-image-manipulator"]
    C --> D["POST /api/v1/classify/detail<br/>multipart/form-data"]
    D --> E["분류 결과 화면"]
```

## 개발

```bash
# 의존성 설치
pnpm install

# 웹 개발 서버 (port 8081)
pnpm start -- --web

# TypeScript 타입 체크
npx tsc --noEmit
```

## Docker 빌드 & 배포

```bash
# Root Makefile 사용
make build-frontend-docker    # Docker 이미지 빌드
make deploy-frontend          # K8s 배포
```

Dockerfile은 2단계 빌드:
1. `node:20-alpine`에서 `npx expo export --platform web`
2. `nginx:alpine`에서 정적 파일 서빙 + `/api/` 프록시

### nginx 프록시

웹에서 API 호출 시 CORS 문제를 피하기 위해 nginx가 `/api/`를 API Server로 프록시:

```nginx
location /api/ {
    proxy_pass http://api-server:8080/api/;
}
```

Frontend 코드에서 `API_BASE_URL`은 빈 문자열(`""`)로 설정하여 상대 경로로 API 호출.
