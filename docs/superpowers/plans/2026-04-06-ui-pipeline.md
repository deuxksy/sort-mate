# UI Pipeline Implementation Plan (Figma → OpenUI → Storybook → Appsmith)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Figma 토큰을 Style Dictionary가 Tailwind + Appsmith CSS로 변환하고, Storybook에서 컴포넌트를 시각 검수하는 파이프라인 구축.

**Architecture:** `ui/`는 토큰 파이프라인 인프라(OpenUI Docker, Style Dictionary, 스크립트). `frontend/`에 Storybook을 설치하여 Web + RN 컴포넌트를 `react-native-web`으로 렌더링. Appsmith는 루트 `compose.yaml`에 Docker 서비스로 추가.

**Tech Stack:** Style Dictionary, Storybook 8 (`@storybook/react`), `@storybook/addon-designs`, Tailwind CSS / NativeWind v4, Appsmith EE (Docker)

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `ui/compose.yaml` | Rename from `docker-compose.yaml` | OpenUI + adapter 서비스 |
| `ui/tokens/tokens.json` | Create | Figma 토큰 샘플 (초기 dev용) |
| `ui/sd/config.js` | Create | Style Dictionary 설정 (tailwind + appsmith 플랫폼) |
| `ui/sd/package.json` | Create | Style Dictionary 의존성 (ui/sd 독립 실행) |
| `ui/scripts/figma-sync.sh` | Create | Figma API → tokens.json 동기화 |
| `ui/scripts/sd-build.sh` | Create | Style Dictionary 빌드 실행 |
| `frontend/tailwind.tokens.js` | Generated | Style Dictionary 출력 (tailwind.colors 등) |
| `frontend/appsmith-theme.css` | Generated | Style Dictionary 출력 (CSS custom properties) |
| `frontend/tailwind.config.js` | Modify | tokens.js import 병합 |
| `frontend/.storybook/main.ts` | Create | Storybook 설정 + addon-designs |
| `frontend/.storybook/preview.tsx` | Create | 글로벌 데코레이터 (NativeWind) |
| `frontend/components/Button.tsx` | Create | 샘플 컴포넌트 (토큰 사용 검증) |
| `frontend/stories/Button.stories.tsx` | Create | 샘플 스토리 (Figma 임베드 포함) |
| `compose.yaml` | Modify | Appsmith 서비스 추가 |
| `Makefile` | Modify | 파이프라인 타겟 추가 |
| `frontend/package.json` | Modify | Storybook 의존성 추가 |

---

## Task 1: ui/compose.yaml 파일명 통일

**Files:**
- Rename: `ui/docker-compose.yaml` → `ui/compose.yaml`

- [ ] **Step 1: 파일명 변경**

```bash
git mv ui/docker-compose.yaml ui/compose.yaml
```

- [ ] **Step 2: 내용에 host.docker.internal 경로가 있으면 확인**

```bash
grep -n "host.docker.internal" ui/compose.yaml
```

Expected: 결과 없음 (현재는 host 네트워크 모드 사용)

- [ ] **Step 3: Commit**

```bash
git add ui/compose.yaml
git commit -m "refactor: rename ui/docker-compose.yaml → ui/compose.yaml

compose.yaml로 파일명 통일 (Docker Compose V2 표준)"
```

---

## Task 2: Style Dictionary 환경 구성

**Files:**
- Create: `ui/sd/package.json`
- Create: `ui/sd/config.js`
- Create: `ui/tokens/tokens.json`

- [ ] **Step 1: ui/sd/package.json 작성**

```json
{
  "name": "waste-helper-tokens",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "build": "style-dictionary build --config config.js"
  },
  "devDependencies": {
    "style-dictionary": "^4.3.2"
  }
}
```

- [ ] **Step 2: ui/tokens/tokens.json 샘플 작성**

```json
{
  "color": {
    "primary": {
      "DEFAULT": { "value": "#22c55e", "type": "color" },
      "dark":    { "value": "#16a34a", "type": "color" },
      "darker":  { "value": "#166534", "type": "color" }
    },
    "eco": {
      "bg":     { "value": "#f0faf0", "type": "color" },
      "surface": { "value": "#ffffff", "type": "color" }
    }
  },
  "spacing": {
    "sm": { "value": "8", "type": "spacing" },
    "md": { "value": "16", "type": "spacing" },
    "lg": { "value": "24", "type": "spacing" }
  },
  "radius": {
    "sm": { "value": "4", "type": "borderRadius" },
    "md": { "value": "8", "type": "borderRadius" },
    "lg": { "value": "16", "type": "borderRadius" }
  }
}
```

- [ ] **Step 3: ui/sd/config.js 작성**

```js
const path = require("path");

module.exports = {
  source: [path.join(__dirname, "../tokens/**/*.json")],
  platforms: {
    tailwind: {
      transformGroup: "css",
      buildPath: path.join(__dirname, "../../frontend/"),
      files: [
        {
          destination: "tailwind.tokens.js",
          format: "javascript/es6",
        },
      ],
    },
    appsmith: {
      transformGroup: "css",
      buildPath: path.join(__dirname, "../../frontend/"),
      files: [
        {
          destination: "appsmith-theme.css",
          format: "css/variables",
          options: {
            outputReferences: true,
          },
        },
      ],
    },
  },
};
```

- [ ] **Step 4: Style Dictionary 빌드 테스트**

```bash
cd ui/sd && pnpm install && pnpm build
```

Expected: `frontend/tailwind.tokens.js` + `frontend/appsmith-theme.css` 생성

- [ ] **Step 5: 생성된 파일 확인**

```bash
head -20 frontend/tailwind.tokens.js
head -20 frontend/appsmith-theme.css
```

Expected:
- `tailwind.tokens.js`: `export const ColorPrimaryDefault = "#22c55e";` 형식
- `appsmith-theme.css`: `:root { --color-primary-default: #22c55e; }` 형식

- [ ] **Step 6: Commit**

```bash
git add ui/sd/ ui/tokens/
git commit -m "feat: add Style Dictionary token pipeline

- ui/tokens/tokens.json: Figma 토큰 샘플 (primary, eco, spacing, radius)
- ui/sd/config.js: Tailwind + Appsmith CSS 플랫폼 설정
- 기존 tailwind.config.js 색상과 일치하는 초기 토큰"
```

---

## Task 3: Tailwind 토큰 병합

**Files:**
- Modify: `frontend/tailwind.config.js`
- Generated: `frontend/tailwind.tokens.js` (Task 2에서 생성됨)

- [ ] **Step 1: tailwind.config.js 수정**

```js
/** @type {import('tailwindcss').Config} */

// Style Dictionary에서 생성된 토큰 import
const tokens = require("./tailwind.tokens.js");

// 토큰 → Tailwind theme 값으로 변환
const tokenColors = {};
const tokenSpacing = {};
const tokenBorderRadius = {};

for (const [key, value] of Object.entries(tokens)) {
  if (key.startsWith("Color")) {
    // ColorPrimaryDefault → primary-DEFAULT 등으로 매핑
    const name = key.replace(/^Color/, "").replace(/Default$/, "");
    tokenColors[name.charAt(0).toLowerCase() + name.slice(1)] = value;
  } else if (key.startsWith("Spacing")) {
    const name = key.replace(/^Spacing/, "").toLowerCase();
    tokenSpacing[name] = `${value}px`;
  } else if (key.startsWith("Radius")) {
    const name = key.replace(/^Radius/, "").toLowerCase();
    tokenBorderRadius[name] = `${value}px`;
  }
}

module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#22c55e",
          dark: "#16a34a",
          darker: "#166534",
          ...tokenColors,
        },
        eco: {
          bg: "#f0faf0",
          surface: "#ffffff",
        },
      },
      spacing: {
        ...tokenSpacing,
      },
      borderRadius: {
        ...tokenBorderRadius,
      },
    },
  },
  plugins: [],
};
```

- [ ] **Step 2: 기존 Expo 앱 정상 동작 확인**

```bash
cd frontend && pnpm start --web &
sleep 8 && kill %1
```

Expected: 에러 없이 Web 번들링 성공

- [ ] **Step 3: Commit**

```bash
git add frontend/tailwind.config.js
git commit -m "feat: integrate Style Dictionary tokens into Tailwind config

tailwind.tokens.js를 import하여 colors/spacing/borderRadius에 병합.
토큰 업데이트 시 token-build → 자동 반영."
```

---

## Task 4: Figma 동기화 스크립트

**Files:**
- Create: `ui/scripts/figma-sync.sh`
- Create: `ui/scripts/sd-build.sh`

- [ ] **Step 1: figma-sync.sh 작성**

```bash
#!/usr/bin/env bash
set -euo pipefail

# Figma Variables API → tokens.json 동기화
# 사용법: FIGMA_TOKEN=<pat> FIGMA_FILE_KEY=<file-key> ./figma-sync.sh

FIGMA_API="https://api.figma.com/v1"
TOKEN="${FIGMA_TOKEN:?FIGMA_TOKEN 환경변수가 필요합니다}"
FILE_KEY="${FIGMA_FILE_KEY:?FIGMA_FILE_KEY 환경변수가 필요합니다}"
OUTPUT_DIR="$(dirname "$0")/../tokens"
OUTPUT="${OUTPUT_DIR}/tokens.json"

mkdir -p "${OUTPUT_DIR}"

echo "Figma Variables 조회 중... (file: ${FILE_KEY})"

# Figma Variables API 호출
RESPONSE=$(curl -sf \
  -H "X-Figma-Token: ${TOKEN}" \
  "${FIGMA_API}/files/${FILE_KEY}/variables/local") || {
    echo "ERROR: Figma API 호출 실패. TOKEN과 FILE_KEY를 확인하세요." >&2
    exit 1
  }

# Variables → Design Tokens 형식 변환 (python 사용)
python3 - "$RESPONSE" <<'PYEOF' > "${OUTPUT}"
import sys, json

data = json.load(sys.stdin)
tokens = {}

variables = data.get("variables", {})
for var_id, var in variables.items():
    name = var["name"].replace("/", ".")
    var_type = var.get("variableType", "other")
    resolved_type = var.get("resolvedType", "string")

    # 모드별 값 (light/dark 등) → 첫 번째 모드 값 사용
    values_by_mode = var.get("valuesByMode", {})
    value = next(iter(values_by_mode.values()), None)

    if value is None:
        continue

    # 그룹 분리 (color.primary.DEFAULT 형태)
    parts = name.split(".")
    current = tokens
    for part in parts[:-1]:
        current = current.setdefault(part, {})

    token_type = {
        "COLOR": "color",
        "FLOAT": "number",
        "STRING": "string",
        "BOOLEAN": "boolean",
    }.get(resolved_type, "other")

    current[parts[-1]] = {
        "value": str(value) if not isinstance(value, (int, float)) else value,
        "type": token_type,
    }

json.dump(tokens, sys.stdout, indent=2)
PYEOF

echo "✓ tokens.json 저장 완료: ${OUTPUT}"
echo "  토큰 수: $(python3 -c "import json; d=json.load(open('${OUTPUT}')); print(sum(1 for _ in __import__('json').load(open('${OUTPUT}'))))" 2>/dev/null || echo '?')"
```

- [ ] **Step 2: sd-build.sh 작성**

```bash
#!/usr/bin/env bash
set -euo pipefail

SD_DIR="$(dirname "$0")/../sd"

echo "Style Dictionary 빌드 시작..."
cd "${SD_DIR}"

# 의존성 확인
if [ ! -d "node_modules" ]; then
  echo "의존성 설치 중..."
  pnpm install --frozen-lockfile 2>/dev/null || pnpm install
fi

pnpm build

echo "✓ 빌드 완료:"
echo "  → frontend/tailwind.tokens.js"
echo "  → frontend/appsmith-theme.css"
```

- [ ] **Step 3: 실행 권한 부여**

```bash
chmod +x ui/scripts/figma-sync.sh ui/scripts/sd-build.sh
```

- [ ] **Step 4: Commit**

```bash
git add ui/scripts/
git commit -m "feat: add figma-sync and sd-build scripts

- figma-sync.sh: Figma Variables API → tokens.json 변환
- sd-build.sh: Style Dictionary 빌드 (tailwind + appsmith CSS)"
```

---

## Task 5: Storybook 설치 및 설정

**Files:**
- Modify: `frontend/package.json` (의존성 추가)
- Create: `frontend/.storybook/main.ts`
- Create: `frontend/.storybook/preview.tsx`

- [ ] **Step 1: Storybook 의존성 설치**

```bash
cd frontend && pnpm add -D \
  storybook@^8 \
  @storybook/react@^8 \
  @storybook/react-webpack5@^8 \
  @storybook/addon-designs@^8 \
  @storybook/addon-essentials@^8 \
  @storybook/addon-interactions@^8
```

- [ ] **Step 2: Storybook 스크립트 추가 (package.json)**

`frontend/package.json`의 `scripts`에 추가:

```json
{
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web",
    "storybook": "storybook dev -p 6006",
    "storybook-build": "storybook build -o storybook-static"
  }
}
```

- [ ] **Step 3: frontend/.storybook/main.ts 작성**

```ts
import type { StorybookConfig } from "@storybook/react-webpack5";

const config: StorybookConfig = {
  stories: ["../stories/**/*.stories.@(ts|tsx)", "../components/**/*.stories.@(ts|tsx)"],
  addons: [
    "@storybook/addon-essentials",
    "@storybook/addon-interactions",
    "@storybook/addon-designs",
  ],
  framework: {
    name: "@storybook/react-webpack5",
    options: {},
  },
  // react-native-web 호환
  webpackFinal: async (config) => {
    config.resolve = config.resolve || {};
    config.resolve.alias = {
      ...config.resolve.alias,
      "react-native$": "react-native-web",
    };
    // NativeWind/Tailwind CSS 로더
    config.module?.rules?.push({
      test: /\.css$/,
      use: ["style-loader", "css-loader"],
    });
    return config;
  },
};

export default config;
```

- [ ] **Step 4: frontend/.storybook/preview.tsx 작성**

```tsx
import "../global.css";
import type { Preview } from "@storybook/react";

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/,
      },
    },
    // addon-designs 기본 설정 (Figma 파일 URL)
    design: {
      type: "figma",
    },
  },
};

export default preview;
```

- [ ] **Step 5: Storybook 실행 테스트**

```bash
cd frontend && pnpm storybook &
sleep 15
curl -sf http://localhost:6006 > /dev/null && echo "OK" || echo "FAIL"
kill %1
```

Expected: `OK` (Storybook dev 서버가 port 6006에서 응답)

- [ ] **Step 6: Commit**

```bash
git add frontend/.storybook/ frontend/package.json frontend/pnpm-lock.yaml
git commit -m "feat: add Storybook with react-native-web and Figma addon

- @storybook/react-webpack5로 Web + RN 컴포넌트 렌더링
- @storybook/addon-designs로 Figma 프레임 임베드
- react-native → react-native-web alias 설정
- NativeWind/Tailwind CSS 로더 포함"
```

---

## Task 6: 샘플 컴포넌트 + Story

**Files:**
- Create: `frontend/components/Button.tsx`
- Create: `frontend/stories/Button.stories.tsx`

- [ ] **Step 1: Button 컴포넌트 작성**

```tsx
import { TouchableOpacity, Text, ActivityIndicator } from "react-native";
import { ComponentProps } from "react";

type ButtonVariant = "primary" | "secondary" | "outline";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends Omit<ComponentProps<typeof TouchableOpacity>, "children"> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  disabled?: boolean;
  children: string;
  onPress?: () => void;
}

const variantStyles: Record<ButtonVariant, string> = {
  primary: "bg-primary items-center justify-center rounded-md",
  secondary: "bg-eco-surface items-center justify-center rounded-md border border-primary",
  outline: "bg-transparent items-center justify-center rounded-md border border-gray-300",
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "px-2 py-1",
  md: "px-4 py-2",
  lg: "px-6 py-3",
};

export function Button({
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  children,
  onPress,
  ...rest
}: ButtonProps) {
  return (
    <TouchableOpacity
      className={`${variantStyles[variant]} ${sizeStyles[size]} ${disabled ? "opacity-50" : ""}`}
      disabled={disabled || loading}
      onPress={onPress}
      activeOpacity={0.7}
      {...rest}
    >
      {loading ? (
        <ActivityIndicator color={variant === "primary" ? "#fff" : "#22c55e"} />
      ) : (
        <Text className={`text-sm font-semibold ${variant === "primary" ? "text-white" : "text-primary-dark"}`}>
          {children}
        </Text>
      )}
    </TouchableOpacity>
  );
}
```

- [ ] **Step 2: Button 스토리 작성**

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "../components/Button";

const meta: Meta<typeof Button> = {
  title: "Components/Button",
  component: Button,
  tags: ["autodocs"],
  // Figma 디자인 참조 (실제 Figma 프레임 URL로 교체)
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/EXAMPLE?node-id=1-2",
    },
  },
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "secondary", "outline"],
    },
    size: {
      control: "select",
      options: ["sm", "md", "lg"],
    },
    loading: { control: "boolean" },
    disabled: { control: "boolean" },
    onPress: { action: "pressed" },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    variant: "primary",
    size: "md",
    children: "폐기물 분류하기",
  },
};

export const Secondary: Story = {
  args: {
    variant: "secondary",
    size: "md",
    children: "다시 촬영",
  },
};

export const Outline: Story = {
  args: {
    variant: "outline",
    size: "md",
    children: "취소",
  },
};

export const Loading: Story = {
  args: {
    variant: "primary",
    size: "md",
    loading: true,
    children: "처리 중...",
  },
};

export const Disabled: Story = {
  args: {
    variant: "primary",
    size: "md",
    disabled: true,
    children: "비활성",
  },
};

export const AllSizes: Story = {
  render: () => (
    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
};
```

- [ ] **Step 3: Storybook에서 렌더링 확인**

```bash
cd frontend && pnpm storybook &
sleep 15
curl -sf http://localhost:6006 > /dev/null && echo "OK" || echo "FAIL"
kill %1
```

Expected: `OK` (Storybook에 Button 컴포넌트 6개 스토리 표시)

- [ ] **Step 4: Commit**

```bash
git add frontend/components/Button.tsx frontend/stories/Button.stories.tsx
git commit -m "feat: add Button component with Storybook stories

- variant: primary/secondary/outline
- size: sm/md/lg
- 상태: loading, disabled
- addon-designs로 Figma 프레임 참조"
```

---

## Task 7: Appsmith Docker 서비스 추가

**Files:**
- Modify: `compose.yaml`

- [ ] **Step 1: 현재 compose.yaml 내용 백업 확인**

```bash
cat compose.yaml
```

- [ ] **Step 2: Appsmith 서비스 추가**

기존 내용을 유지하고 `appsmith` 서비스를 추가:

```yaml
services:

  adapter:
    container_name: aperture-adapter
    build:
      context: ./ui
      dockerfile: Dockerfile.adapter
    network_mode: host
    environment:
      - APERTURE_BASE=http://100.118.111.59
      - APERTURE_API_KEY=${ZAI_API_KEY}
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8765/v1/models')"]
      interval: 5s
      retries: 10

  openui:
    container_name: openui
    image: ghcr.io/wandb/openui:latest
    network_mode: host
    depends_on:
      adapter:
        condition: service_healthy
    environment:
      - OPENUI_ENVIRONMENT=local
      - OPENAI_COMPATIBLE_ENDPOINT=http://localhost:8765/v1
      - OPENAI_COMPATIBLE_API_KEY=${ZAI_API_KEY}
      - OPENAI_COMPATIBLE_MODEL=glm-5.1
      - DEFAULT_MODEL=glm-5.1
      - OPENAI_API_KEY=sk-dummy
      - LITELLM_BASE_URL=http://localhost:8765/v1
      - LITELLM_API_KEY=${ZAI_API_KEY}

  appsmith:
    container_name: appsmith
    image: appsmith/appsmith-ee:latest
    ports:
      - "8080:80"
    volumes:
      - appsmith-data:/appsmith-stacks
    restart: unless-stopped

volumes:
  appsmith-data:
```

- [ ] **Step 3: Appsmith 시작 테스트**

```bash
docker compose up -d appsmith
sleep 10
docker compose ps appsmith
```

Expected: `appsmith` 컨테이너 `running` 상태, port 8080

- [ ] **Step 4: Commit**

```bash
git add compose.yaml
git commit -m "feat: add Appsmith EE service to compose.yaml

- appsmith/appsmith-ee:latest on port 8080
- Persistent volume: appsmith-data
- Appsmith Custom Theme에 appsmith-theme.css 주입 예정"
```

---

## Task 8: Makefile 파이프라인 타겟 추가

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: 파이프라인 타겟 추가**

기존 Makefile 끝(`help:` 타겟 직전)에 추가:

```makefile
# =============================================================================
# UI Pipeline (Figma → OpenUI → Storybook → Appsmith)
# =============================================================================

.PHONY: token-sync token-build storybook storybook-build \
        appsmith-up appsmith-down openui-up openui-down \
        ui-pipeline

token-sync: ## Figma Variables API → ui/tokens/tokens.json 동기화
	@echo "Figma 토큰 동기화..."
	cd ui/scripts && ./figma-sync.sh

token-build: ## Style Dictionary → Tailwind tokens + Appsmith CSS
	@echo "Style Dictionary 빌드..."
	cd ui/scripts && ./sd-build.sh

storybook: ## Storybook dev 서버 시작 (port 6006)
	cd frontend && pnpm storybook

storybook-build: ## Storybook 정적 빌드
	cd frontend && pnpm storybook-build

appsmith-up: ## Appsmith 컨테이너 시작 (port 8080)
	docker compose up -d appsmith
	@echo "✓ Appsmith: http://localhost:8080"

appsmith-down: ## Appsmith 컨테이너 중지
	docker compose stop appsmith

openui-up: ## OpenUI + adapter 시작 (port 7878)
	cd ui && docker compose -f compose.yaml up -d
	@echo "✓ OpenUI: http://localhost:7878"

openui-down: ## OpenUI + adapter 중지
	cd ui && docker compose -f compose.yaml down

ui-pipeline: token-sync token-build ## 전체 UI 파이프라인 (sync → build)
	@echo "✓ UI 파이프라인 완료. 'make storybook'으로 검수 시작"
```

- [ ] **Step 2: help 출력 확인**

```bash
make help
```

Expected: `token-sync`, `token-build`, `storybook`, `appsmith-up` 등 신규 타겟 표시

- [ ] **Step 3: Commit**

```bash
git add Makefile
git commit -m "feat: add UI pipeline Makefile targets

- token-sync: Figma → tokens.json
- token-build: Style Dictionary → Tailwind + Appsmith CSS
- storybook/storybook-build: Storybook dev/build
- appsmith-up/down: Appsmith Docker 관리
- openui-up/down: OpenUI Docker 관리
- ui-pipeline: 전체 워크플로우 순차 실행"
```

---

## Task 9: 통합 검증

**Files:** 없음 (실행만)

- [ ] **Step 1: Style Dictionary 전체 빌드**

```bash
make token-build
```

Expected: `frontend/tailwind.tokens.js`, `frontend/appsmith-theme.css` 재생성

- [ ] **Step 2: Storybook 실행 + 스토리 확인**

```bash
cd frontend && pnpm storybook
```

Expected:
- `http://localhost:6006` 에서 Storybook UI 표시
- Components/Button 에 6개 스토리 표시
- Primary, Secondary, Outline variant 렌더링

- [ ] **Step 3: Appsmith 접속 확인**

```bash
make appsmith-up
curl -sf http://localhost:8080 > /dev/null && echo "OK" || echo "FAIL"
```

Expected: `OK`

- [ ] **Step 4: Makefile help 전체 확인**

```bash
make help
```

Expected: 모든 신규 타겟이 도움말에 표시됨

- [ ] **Step 5: 최종 tag**

```bash
git tag 260406/ui-pipeline
```
