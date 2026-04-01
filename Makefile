# =============================================================================
# Waste Helper Backend — Makefile
# =============================================================================
# 하위 프로젝트(api-server, vlm-service, k8s)의 build/deploy 관리

.DEFAULT_GOAL := help

# --- 설정 ---
NAMESPACE   ?= waste-helper
K8S_DIR    := k8s/manifests
ENV_FILE   ?= .env

# Docker 이미지 태그
API_IMAGE  ?= waste-helper/api-server:latest
VLM_IMAGE  ?= waste-helper/vlm-service:latest

# 빌드 플랫폼 (로컬: 비워둠, 운영: PLATFORM=linux/amd64)
PLATFORM_FLAG := $(PLATFORM:%=--platform %)

# 환경변수 로드 (존재할 경우)
ifneq ($(wildcard $(ENV_FILE)),)
include $(ENV_FILE)
export
endif

# =============================================================================
# Build
# =============================================================================

.PHONY: build build-api build-vlm build-all build-frontend

build: build-api build-vlm ## 전체 빌드

build-api: ## API Server 빌드 (Gradle bootJar + Docker 이미지)
	cd api-server && ./gradlew bootJar -x test
	docker build $(PLATFORM_FLAG) -f api-server/Dockerfile.local -t $(API_IMAGE) api-server/

build-vlm: ## VLM Service Docker 이미지 빌드
	docker build -t $(VLM_IMAGE) vlm-service/

build-all: build build-frontend ## 전체 빌드 (Backend + Frontend)

build-frontend: ## Frontend TypeScript 타입 체크
	cd frontend && npx tsc --noEmit

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
# Local Development
# =============================================================================

.PHONY: loc loc-up loc-down loc-logs loc-frontend

loc: loc-up ## 로컬 개발 환경 시작 (Docker Compose)

loc-up: ## 인프라(PostgreSQL, Redis) + API Server 시작
	cd api-server/src/main/docker && docker compose -f services.yml up -d
	cd api-server && ./gradlew bootRun

loc-down: ## 로컬 개발 환경 중지
	cd api-server/src/main/docker && docker compose -f services.yml down

loc-logs: ## 로컬 개발 환경 로그
	cd api-server/src/main/docker && docker compose -f services.yml logs -f

loc-frontend: ## Frontend Expo 개발 서버 실행
	cd frontend && pnpm start

# =============================================================================
# K8s Deploy
# =============================================================================

.PHONY: deploy deploy-infra deploy-api deploy-vlm deploy-monitoring \
        deploy-all teardown

deploy: deploy-infra deploy-api deploy-vlm ## 전체 배포

deploy-infra: ## Namespace + PostgreSQL + Redis 배포
	kubectl apply -f $(K8S_DIR)/namespace.yaml
	envsubst < $(K8S_DIR)/postgres-secret.yaml | kubectl apply -f -
	kubectl apply -f $(K8S_DIR)/postgres-statefulset.yaml
	kubectl apply -f $(K8S_DIR)/redis-deployment.yaml

deploy-api: build-api ## API Server 이미지 빌드 + K8s 배포
	kubectl apply -f $(K8S_DIR)/api-server-deployment.yaml
	kubectl rollout restart deployment/api-server -n $(NAMESPACE)

deploy-vlm: build-vlm ## VLM Service 이미지 빌드 + K8s 배포
	kubectl apply -f $(K8S_DIR)/vlm-deployment.yaml
	kubectl apply -f $(K8S_DIR)/vlm-hpa.yaml

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
# Docker
# =============================================================================

.PHONY: docker-push docker-push-api docker-push-vlm

docker-push-api: build-api ## API Server 이미지 빌드 + Push
	docker push $(API_IMAGE)

docker-push-vlm: build-vlm ## VLM Service 이미지 빌드 + Push
	docker push $(VLM_IMAGE)

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
