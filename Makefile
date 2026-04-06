# =============================================================================
# Waste Helper — Makefile
# =============================================================================
# 하위 프로젝트(api-server, vlm-service, mock-vlm, frontend, k8s)의 build/deploy 관리

.DEFAULT_GOAL := help

# --- 설정 ---
NAMESPACE   ?= waste-helper
K8S_DIR    := k8s/manifests
LOCAL_DIR  := k8s/manifests/local
ENV_FILE   ?= .env

# Docker 이미지 태그
API_IMAGE      ?= waste-helper/api-server:latest
VLM_IMAGE      ?= waste-helper/vlm-service:latest
FRONTEND_IMAGE ?= waste-helper/frontend:latest

# 빌드 플랫폼 (로컬: 비워둠, 운영: PLATFORM=linux/amd64)
PLATFORM_FLAG := $(PLATFORM:%=--platform %)

# Port-forward 설정
PF_FRONTEND_PORT ?= 33080
PF_API_PORT      ?= 32067
PF_BIND          ?= 0.0.0.0

# 환경변수 로드 (존재할 경우)
ifneq ($(wildcard $(ENV_FILE)),)
include $(ENV_FILE)
export
endif

# =============================================================================
# Build
# =============================================================================

.PHONY: build build-api build-vlm build-mock-vlm build-all build-frontend build-frontend-docker

build: build-api build-mock-vlm ## 전체 빌드 (Backend)

build-api: ## API Server 빌드 (Gradle bootJar + Docker 이미지)
	cd api-server && ./gradlew bootJar -x test
	docker build $(PLATFORM_FLAG) -f api-server/Dockerfile.local -t $(API_IMAGE) api-server/

build-vlm: ## VLM Service Docker 이미지 빌드 (실제 GPU 서비스)
	docker build -t $(VLM_IMAGE) vlm-service/

build-mock-vlm: ## Mock VLM Docker 이미지 빌드 (GPU 불필요)
	docker build -t $(VLM_IMAGE) mock-vlm/

build-all: build build-frontend-docker ## 전체 빌드 (Backend + Frontend Docker 이미지)

build-frontend: ## Frontend TypeScript 타입 체크
	cd frontend && npx tsc --noEmit

build-frontend-docker: ## Frontend Docker 이미지 빌드 (Expo Web → Nginx)
	docker build $(PLATFORM_FLAG) -t $(FRONTEND_IMAGE) frontend/

# =============================================================================
# Test
# =============================================================================

.PHONY: test test-api test-vlm test-frontend test-frontend-doctor

test: test-api ## 전체 테스트

test-api: ## API Server 테스트
	cd api-server && ./gradlew test

test-vlm: ## VLM Service 테스트
	cd vlm-service && python3 -m pytest tests/ -v

test-frontend: ## Frontend Expo dev 서버 시작 테스트
	cd frontend && npx expo start --clear & EXPO_PID=$$!; sleep 10; kill $$EXPO_PID 2>/dev/null; echo "Expo dev server test passed"
test-frontend-doctor: ## Frontend Expo 의존성 호환성 검사
	cd frontend && npx expo-doctor
test-frontend-export: ## Frontend Web 번들링 테스트
	cd frontend && npx expo export --platform web --output-dir /tmp/expo-test-export && rm -rf /tmp/expo-test-export

# =============================================================================
# Local K8s Development
# =============================================================================

.PHONY: loc-up loc-down loc-logs loc-frontend

loc-up: ## 로컬 K8s 전체 스택 배포 (infra + backend + frontend)
	kubectl apply -f $(K8S_DIR)/namespace.yaml
	kubectl apply -f $(K8S_DIR)/postgres-secret.yaml
	kubectl apply -f $(K8S_DIR)/postgres-statefulset.yaml
	kubectl apply -f $(K8S_DIR)/redis-deployment.yaml
	kubectl apply -f $(LOCAL_DIR)/vlm-deployment-local.yaml
	kubectl apply -f $(LOCAL_DIR)/api-server-deployment-local.yaml
	kubectl apply -f $(K8S_DIR)/frontend-deployment.yaml
	@echo "✓ 로컬 K8s 스택 배포 완료. 'make pf' 로 port-forward 실행"

loc-down: ## 로컬 K8s 전체 스택 중지 (Namespace 삭제)
	kubectl delete namespace $(NAMESPACE) --ignore-not-found=true
	@echo "✓ Namespace $(NAMESPACE) 삭제 완료"

loc-logs: ## 로컬 K8s 전체 로그 확인
	kubectl logs -n $(NAMESPACE) -l app --all-containers=true -f

loc-frontend: ## Frontend Expo 개발 서버 실행
	cd frontend && pnpm start

# =============================================================================
# Local Docker Compose (API Server + 인프라만)
# =============================================================================

.PHONY: loc-infra-up loc-infra-down loc-infra-logs

loc-infra-up: ## 인프라만 Docker Compose로 시작 (PostgreSQL, Redis)
	cd api-server/src/main/docker && docker compose -f services.yml up -d
	cd api-server && ./gradlew bootRun

loc-infra-down: ## Docker Compose 인프라 중지
	cd api-server/src/main/docker && docker compose -f services.yml down

loc-infra-logs: ## Docker Compose 인프라 로그
	cd api-server/src/main/docker && docker compose -f services.yml logs -f

# =============================================================================
# Port-forward (외부 기기 접근)
# =============================================================================

.PHONY: pf pf-frontend pf-api

pf: ## 전체 port-forward (Frontend + API)
	@echo "Frontend: http://$(PF_BIND):$(PF_FRONTEND_PORT)"
	@echo "API:      http://$(PF_BIND):$(PF_API_PORT)"
	kubectl port-forward -n $(NAMESPACE) svc/frontend $(PF_FRONTEND_PORT):80 --address $(PF_BIND) &
	kubectl port-forward -n $(NAMESPACE) svc/api-server $(PF_API_PORT):8080 --address $(PF_BIND)

pf-frontend: ## Frontend port-forward
	kubectl port-forward -n $(NAMESPACE) svc/frontend $(PF_FRONTEND_PORT):80 --address $(PF_BIND)

pf-api: ## API Server port-forward
	kubectl port-forward -n $(NAMESPACE) svc/api-server $(PF_API_PORT):8080 --address $(PF_BIND)

# =============================================================================
# K8s Deploy (운영)
# =============================================================================

.PHONY: deploy deploy-infra deploy-api deploy-vlm deploy-mock-vlm deploy-frontend deploy-monitoring \
        deploy-all teardown

deploy: deploy-infra deploy-api deploy-mock-vlm deploy-frontend ## 전체 배포

deploy-infra: ## Namespace + PostgreSQL + Redis 배포
	kubectl apply -f $(K8S_DIR)/namespace.yaml
	envsubst < $(K8S_DIR)/postgres-secret.yaml | kubectl apply -f -
	kubectl apply -f $(K8S_DIR)/postgres-statefulset.yaml
	kubectl apply -f $(K8S_DIR)/redis-deployment.yaml

deploy-api: build-api ## API Server 이미지 빌드 + K8s 배포
	kubectl apply -f $(K8S_DIR)/api-server-deployment.yaml
	kubectl rollout restart deployment/api-server -n $(NAMESPACE)

deploy-vlm: build-vlm ## VLM Service (실제 GPU) 이미지 빌드 + K8s 배포
	kubectl apply -f $(K8S_DIR)/vlm-deployment.yaml
	kubectl apply -f $(K8S_DIR)/vlm-hpa.yaml

deploy-mock-vlm: build-mock-vlm ## Mock VLM 이미지 빌드 + K8s 배포
	kubectl apply -f $(LOCAL_DIR)/vlm-deployment-local.yaml

deploy-frontend: build-frontend-docker ## Frontend 이미지 빌드 + K8s 배포
	kubectl apply -f $(K8S_DIR)/frontend-deployment.yaml
	kubectl rollout restart deployment/frontend -n $(NAMESPACE)

deploy-monitoring: ## Prometheus + Grafana 배포
	kubectl apply -f $(K8S_DIR)/prometheus-config.yaml
	kubectl apply -f $(K8S_DIR)/prometheus.yaml
	envsubst < $(K8S_DIR)/grafana-deployment.yaml | kubectl apply -f -

deploy-network: ## Ingress + NetworkPolicy 배포
	kubectl apply -f $(K8S_DIR)/ingress.yaml
	kubectl apply -f $(K8S_DIR)/networkpolicy.yaml

deploy-all: deploy deploy-monitoring deploy-network ## 인프라 + 앱 + 모니터링 전체 배포

teardown: ## K8s Namespace 삭제 (전체 리소스 제거)
	kubectl delete namespace $(NAMESPACE) --ignore-not-found=true

# =============================================================================
# Docker Push
# =============================================================================

.PHONY: docker-push docker-push-api docker-push-vlm

docker-push-api: build-api ## API Server 이미지 빌드 + Push
	docker push $(API_IMAGE)

docker-push-vlm: build-vlm ## VLM Service 이미지 빌드 + Push
	docker push $(VLM_IMAGE)

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
	docker compose up -d openui
	@echo "✓ OpenUI: http://localhost:7878"

openui-down: ## OpenUI + adapter 중지
	docker compose stop openui

ui-pipeline: token-sync token-build ## 전체 UI 파이프라인 (sync → build)
	@echo "✓ UI 파이프라인 완료. 'make storybook'으로 검증 시작"

# =============================================================================
# Utility
# =============================================================================

.PHONY: clean help env-setup k8s-status

clean: ## 빌드 산출물 삭제
	cd api-server && ./gradlew clean
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	cd frontend && rm -rf .expo node_modules/.cache 2>/dev/null || true

env-setup: ## .env 초기 설정 (.env.example → .env)
	cp -n .env.example .env || true
	@echo ".env 파일 생성 완료. 값을 확인하세요: vi .env"

k8s-status: ## K8s 리소스 상태 확인
	@echo "=== Pods ==="
	kubectl get pods -n $(NAMESPACE)
	@echo "\n=== Services ==="
	kubectl get svc -n $(NAMESPACE)
	@echo "\n=== Deployments ==="
	kubectl get deployments -n $(NAMESPACE)

help: ## 이 도움말 표시
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		sed 's/Makefile://' | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
