# 내 손안의 AI 폐기물 처리 도우미 — Backend 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** React Native 앱의 백엔드 시스템 구축 — JHipster API 서버, VLM 마이크로서비스, K8s 인프라

**Architecture:** Edge-Cloud 하이브리드 — 온디바이스 YOLO 1차 분류, 서버 사이드 Qwen3-VL-4B 상세 분석, gRPC 연동

**Tech Stack:** JHipster 8 (Spring Boot 3.x, Java 21), FastAPI (gRPC), Qwen3-VL-4B (vLLM), PostgreSQL, Redis, Milvus, Proxmox K8s

---

## 파일 구조 개요

```
waste-helper-backend/
├── api-server/                    # JHipster 8 프로젝트
│   ├── src/main/java/com/waste/helper/
│   │   ├── config/                # Security, Redis, gRPC 설정
│   │   ├── domain/                # JPA 엔티티
│   │   ├── repository/            # Spring Data JPA
│   │   ├── service/               # 비즈니스 로직
│   │   ├── web/rest/              # REST 컨트롤러
│   │   ├── grpc/                  # gRPC 클라이언트
│   │   └── security/              # JWT (게스트 + 소셜)
│   ├── src/main/resources/
│   │   ├── config/                # application.yml
│   │   ├── db/migration/          # Flyway 마이그레이션
│   │   └── proto/                 # gRPC Proto 파일
│   └── src/test/java/
├── vlm-service/                   # Python FastAPI + gRPC
│   ├── app/
│   │   ├── main.py
│   │   ├── grpc_server.py
│   │   ├── vlm_engine.py          # vLLM wrapper
│   │   └── prompt.py
│   ├── proto/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── k8s/
│   ├── manifests/                 # K8s 매니페스트
│   ├── helm/                      # Helm 차트
│   └── argocd/                    # ArgoCD Application
└── docs/
```

---

# Phase 1: MVP (4주)

**목표:** 핵심 분류 + 배출 요령 제공

**배포:** JHipster API + PostgreSQL + Redis + VLM 단일 파드

---

## Task 1: 프로젝트 초기 설정

**Files:**
- Create: `api-server/` (JHipster generated)
- Create: `vlm-service/`
- Create: `k8s/manifests/`
- Create: `README.md`

- [ ] **Step 1: JHipster 프로젝트 생성**

```bash
# JHipster 8 설치 확인
npm list -g generator-jhipster

# 프로젝트 생성
cd /Users/crong/git/kl
jhipster create api-server \
  --application-type monolith \
  --base-name waste_helper \
  --package-name com.waste.helper \
  --auth-type jwt \
  --build-tool gradle \
  --db postgresql \
  --cache-provider redis \
  --test-framework junit
```

Expected: `api-server/` 디렉토리 생성 및 모든 기본 파일 생성

- [ ] **Step 2: VLM 서비스 디렉토리 생성**

```bash
cd /Users/crong/git/kl
mkdir -p vlm-service/{app,proto,tests}
touch vlm-service/{requirements.txt,pyproject.toml,Dockerfile}
```

Expected: 디렉토리 구조 생성

- [ ] **Step 3: K8s 매니페스트 디렉토리 생성**

```bash
mkdir -p k8s/manifests k8s/helm/waste-helper/templates k8s/argocd
```

Expected: K8s 디렉토리 구조 생성

- [ ] **Step 4: 프로젝트 README 작성**

```markdown
# 내 손안의 AI 폐기물 처리 도우미 - Backend

## 구조
- `api-server/`: JHipster API 서버 (Spring Boot 3.x)
- `vlm-service/`: VLM 마이크로서비스 (FastAPI + gRPC)
- `k8s/`: Kubernetes 매니페스트

## 실행

### 로컬 개발
```bash
cd api-server
./gradlew bootRun
```

### VLM 서비스 (Docker)
```bash
cd vlm-service
docker build -t vlm-service:latest .
docker run -p 50051:50051 vlm-service:latest
```

## 문서
- [Spec](../specs/2026-03-30-waste-helper-backend-design.md)
```

Expected: README 생성

- [ ] **Step 5: 초기 커밋**

```bash
git add .
git commit -m "feat: 프로젝트 구조 초기화

- JHipster API 서버 스캐폴딩
- VLM 서비스 디렉토리 구조
- K8s 매니페스트 디렉토리"
```

Expected: Clean commit

---

## Task 2: 도메인 모델 정의 (JDL)

**Files:**
- Create: `api-server/.jhipster/`
- Create: `api-server/.jhipster/User.json`
- Create: `api-server/.jhipster/WasteClassification.json`
- Create: `api-server/.jhipster/Region.json`
- Create: `api-server/.jhipster/DisposalGuide.json`
- Create: `api-server/.jhipster/SearchHistory.json`
- Create: `api-server/.jhipster/FavoriteRegion.json`
- Create: `api-server/.jhipster/NotificationSetting.json`
- Create: `api-server/.jhipster/WasteImage.json`
- Create: `api-server/.jhipster/Feedback.json`

- [ ] **Step 1: User 엔티티 정의**

```json
{
  "name": "User",
  "fields": [
    {
      "fieldName": "username",
      "fieldType": "String"
    },
    {
      "fieldName": "email",
      "fieldType": "String"
    },
    {
      "fieldName": "imageUrl",
      "fieldType": "String"
    },
    {
      "fieldName": "langKey",
      "fieldType": "String",
      "fieldValidateRules": ["required"]
    }
  ]
}
```

- [ ] **Step 2: WasteClassification 엔티티 정의**

```json
{
  "name": "WasteClassification",
  "fields": [
    {
      "fieldName": "detectedClass",
      "fieldType": "String",
      "fieldValidateRules": ["required"]
    },
    {
      "fieldName": "confidence",
      "fieldType": "Float",
      "fieldValidateRules": ["required", "min"],
      "fieldValidateRulesMin": 0
    },
    {
      "fieldName": "imageUrl",
      "fieldType": "String"
    },
    {
      "fieldName": "detailResult",
      "fieldType": "TextBlob",
      "fieldTypeBlobContent": "text"
    },
    {
      "fieldName": "classifiedAt",
      "fieldType": "Instant",
      "fieldValidateRules": ["required"]
    }
  ],
  "relationships": [
    {
      "relationshipType": "many-to-one",
      "otherEntityName": "user",
      "otherEntityRelationshipName": "wasteClassifications"
    }
  ]
}
```

- [ ] **Step 3: Region 엔티티 정의**

```json
{
  "name": "Region",
  "fields": [
    {
      "fieldName": "sido",
      "fieldType": "String"
    },
    {
      "fieldName": "sigungu",
      "fieldType": "String"
    },
    {
      "fieldName": "emdName",
      "fieldType": "String"
    },
    {
      "fieldName": "emdCode",
      "fieldType": "String",
      "fieldValidateRules": ["unique"]
    }
  ],
  "relationships": [
    {
      "relationshipType": "one-to-many",
      "otherEntityName": "disposalGuide",
      "otherEntityRelationshipName": "region"
    }
  ]
}
```

- [ ] **Step 4: DisposalGuide 엔티티 정의**

```json
{
  "name": "DisposalGuide",
  "fields": [
    {
      "fieldName": "wasteType",
      "fieldType": "String",
      "fieldValidateRules": ["required"]
    },
    {
      "fieldName": "disposalMethod",
      "fieldType": "TextBlob",
      "fieldTypeBlobContent": "text",
      "fieldValidateRules": ["required"]
    },
    {
      "fieldName": "source",
      "fieldType": "Source",
      "fieldValues": ["PUBLIC_API", "LLM_GENERATED", "LLM_SUPPLEMENTED"]
    }
  ],
  "relationships": [
    {
      "relationshipType": "many-to-one",
      "otherEntityName": "region",
      "otherEntityRelationshipName": "disposalGuides"
    }
  ]
}
```

- [ ] **Step 5: SearchHistory 엔티티 정의**

```json
{
  "name": "SearchHistory",
  "fields": [
    {
      "fieldName": "query",
      "fieldType": "String"
    },
    {
      "fieldName": "resultSummary",
      "fieldType": "TextBlob",
      "fieldTypeBlobContent": "text"
    },
    {
      "fieldName": "classifiedAt",
      "fieldType": "Instant",
      "fieldValidateRules": ["required"]
    }
  ],
  "relationships": [
    {
      "relationshipType": "many-to-one",
      "otherEntityName": "user",
      "otherEntityRelationshipName": "searchHistories"
    }
  ]
}
```

- [ ] **Step 6: FavoriteRegion 엔티티 정의**

```json
{
  "name": "FavoriteRegion",
  "fields": [],
  "relationships": [
    {
      "relationshipType": "many-to-one",
      "otherEntityName": "user",
      "otherEntityRelationshipName": "favoriteRegions"
    },
    {
      "relationshipType": "many-to-one",
      "otherEntityName": "region",
      "otherEntityRelationshipName": "favoriteRegions"
    }
  ]
}
```

- [ ] **Step 7: NotificationSetting 엔티티 정의**

```json
{
  "name": "NotificationSetting",
  "fields": [
    {
      "fieldName": "enabled",
      "fieldType": "Boolean"
    },
    {
      "fieldName": "fcmToken",
      "fieldType": "String"
    }
  ],
  "relationships": [
    {
      "relationshipType": "many-to-one",
      "otherEntityName": "user",
      "otherEntityRelationshipName": "notificationSettings"
    }
  ]
}
```

- [ ] **Step 8: WasteImage 엔티티 정의**

```json
{
  "name": "WasteImage",
  "fields": [
    {
      "fieldName": "originalUrl",
      "fieldType": "String"
    },
    {
      "fieldName": "thumbnailUrl",
      "fieldType": "String"
    }
  ],
  "relationships": [
    {
      "relationshipType": "many-to-one",
      "otherEntityName": "wasteClassification",
      "otherEntityRelationshipName": "wasteImages"
    }
  ]
}
```

- [ ] **Step 9: Feedback 엔티티 정의**

```json
{
  "name": "Feedback",
  "fields": [
    {
      "fieldName": "isAccurate",
      "fieldType": "Boolean"
    },
    {
      "fieldName": "correctedClass",
      "fieldType": "String"
    },
    {
      "fieldName": "comment",
      "fieldType": "String"
    }
  ],
  "relationships": [
    {
      "relationshipType": "many-to-one",
      "otherEntityName": "user",
      "otherEntityRelationshipName": "feedbacks"
    },
    {
      "relationshipType": "many-to-one",
      "otherEntityName": "wasteClassification",
      "otherEntityRelationshipName": "feedbacks"
    }
  ]
}
```

- [ ] **Step 10: Source Enum 생성**

Create: `api-server/src/main/java/com/waste/helper/domain/enumeration/Source.java`

```java
package com.waste.helper.domain.enumeration;

public enum Source {
    PUBLIC_API,
    LLM_GENERATED,
    LLM_SUPPLEMENTED
}
```

- [ ] **Step 11: JDL import**

```bash
cd api-server
jhipster import-jdl .jhipster/*.json
```

Expected: 엔티티 클래스, Repository, Resource 생성

- [ ] **Step 12: 생성된 코드 검증**

```bash
ls src/main/java/com/waste/helper/domain/
ls src/main/java/com/waste/helper/repository/
ls src/main/java/com/waste/helper/web/rest/
```

Expected: 각 디렉토리에 생성된 파일 확인

- [ ] **Step 13: 커밋**

```bash
git add api-server/
git commit -m "feat: 도메인 모델 정의 (JDL)

- User, WasteClassification, Region 엔티티
- DisposalGuide, SearchHistory 엔티티
- FavoriteRegion, NotificationSetting, WasteImage, Feedback 엔티티
- Source Enum"
```

---

## Task 3: 데이터베이스 마이그레이션

**Files:**
- Create: `api-server/src/main/resources/db/migration/V1__init_schema.sql`
- Create: `api-server/src/main/resources/db/migration/V2__device_users.sql`

- [ ] **Step 1: device_users 테이블 마이그레이션 작성**

```sql
-- V2__device_users.sql

-- 게스트 → 유저 마이그레이션을 위한 매핑 테이블
CREATE TABLE device_users (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    user_id BIGINT REFERENCES users(id),
    fingerprint_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_device_users_device_id ON device_users(device_id);
CREATE INDEX idx_device_users_user_id ON device_users(user_id);

-- waste_classifications에 device_id 컬럼 추가
ALTER TABLE waste_classifications
ADD COLUMN device_id VARCHAR(255);

CREATE INDEX idx_waste_classifications_device_id ON waste_classifications(device_id);

-- search_histories에 device_id 컬럼 추가
ALTER TABLE search_history
ADD COLUMN device_id VARCHAR(255);

CREATE INDEX idx_search_history_device_id ON search_history(device_id);
```

- [ ] **Step 2: Flyway 실행으로 마이그레이션 검증**

```bash
cd api-server
./gradlew bootRun
```

Expected: 앱 시작 시 Flyway가 마이그레이션 실행

- [ ] **Step 3: PostgreSQL에서 테이블 생성 확인**

```sql
\dt
\d device_users
\d waste_classifications
```

Expected: 테이블 구조 확인

- [ ] **Step 4: 커밋**

```bash
git add api-server/src/main/resources/db/migration/
git commit -m "feat: 게스트-유저 마이그레이션 스키마

- device_users 매핑 테이블
- waste_classifications, search_histories에 device_id 컬럼
- 인덱스 추가"
```

---

## Task 4: 게스트 인증 구현

**Files:**
- Create: `api-server/src/main/java/com/waste/helper/security/GuestTokenProvider.java`
- Create: `api-server/src/main/java/com/waste/helper/security/DeviceIdValidator.java`
- Modify: `api-server/src/main/java/com/waste/helper/web/rest/AuthResource.java`

- [ ] **Step 1: GuestTokenProvider 작성**

```java
package com.waste.helper.security;

import java.util.UUID;
import org.springframework.security.oauth2.jwt.*;
import org.springframework.stereotype.Component;

@Component
public class GuestTokenProvider {

    private final JwtEncoder encoder;
    private final long TOKEN_VALIDITY = 7 * 24 * 60 * 60 * 1000; // 7 days

    public GuestTokenProvider(JwtEncoder encoder) {
        this.encoder = encoder;
    }

    public String createToken(String deviceId) {
        var claims = JwtClaimsSet.builder()
            .subject(deviceId)
            .claim("role", "GUEST")
            .issuedAt(java.time.Instant.now())
            .expiresAt(java.time.Instant.now().plusMillis(TOKEN_VALIDITY))
            .build();

        return encoder.encode(JwtEncoderParameters.from(claims)).getTokenValue();
    }

    public boolean validateDeviceId(String deviceId) {
        try {
            UUID.fromString(deviceId);
            return true;
        } catch (IllegalArgumentException e) {
            return false;
        }
    }
}
```

- [ ] **Step 2: DeviceIdValidator 작성**

```java
package com.waste.helper.security;

import java.util.regex.Pattern;
import org.springframework.stereotype.Component;

@Component
public class DeviceIdValidator {

    private static final Pattern UUID_V4_PATTERN = Pattern.compile(
        "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    );

    public boolean isValid(String deviceId) {
        if (deviceId == null) {
            return false;
        }
        return UUID_V4_PATTERN.matcher(deviceId.toLowerCase()).matches();
    }

    public String generateFingerprintHash(String userAgent, String screenResolution, String timezone) {
        String data = userAgent + screenResolution + timezone;
        return org.apache.commons.codec.digest.DigestUtils.sha256Hex(data);
    }
}
```

- [ ] **Step 3: AuthResource에 게스트 토큰 엔드포인트 추가**

```java
// api-server/src/main/java/com/waste/helper/web/rest/AuthResource.java

package com.waste.helper.web.rest;

import com.waste.helper.security.*;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/auth")
public class AuthResource {

    private final GuestTokenProvider guestTokenProvider;
    private final DeviceIdValidator deviceIdValidator;

    public AuthResource(GuestTokenProvider guestTokenProvider, DeviceIdValidator deviceIdValidator) {
        this.guestTokenProvider = guestTokenProvider;
        this.deviceIdValidator = deviceIdValidator;
    }

    @PostMapping("/guest")
    public ResponseEntity<GuestTokenResponse> createGuestToken(
        @RequestBody GuestTokenRequest request
    ) {
        if (!deviceIdValidator.isValid(request.deviceId())) {
            return ResponseEntity.badRequest().build();
        }

        String token = guestTokenProvider.createToken(request.deviceId());
        return ResponseEntity.ok(new GuestTokenResponse(token));
    }

    public record GuestTokenRequest(String deviceId) {}
    public record GuestTokenResponse(String token) {}
}
```

- [ ] **Step 4: application.yml에 JWT 설정 추가**

```yaml
# api-server/src/main/resources/application.yml

spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: http://localhost:9080/realms/waste-helper

jwt:
  secret: ${JWT_SECRET:your-secret-key-at-least-256-bits-long-for-hs256}
  token-validity-in-seconds: 604800  # 7 days
```

- [ ] **Step 5: 테스트 작성**

Create: `api-server/src/test/java/com/waste/helper/web/rest/AuthResourceTest.java`

```java
package com.waste.helper.web.rest;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class AuthResourceTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void createGuestToken_withValidDeviceId_returnsToken() throws Exception {
        mockMvc.perform(post("/api/v1/auth/guest")
            .contentType(MediaType.APPLICATION_JSON)
            .content("{\"deviceId\":\"550e8400-e29b-41d4-a716-446655440000\"}"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.token").isNotEmpty());
    }

    @Test
    void createGuestToken_withInvalidDeviceId_returns400() throws Exception {
        mockMvc.perform(post("/api/v1/auth/guest")
            .contentType(MediaType.APPLICATION_JSON)
            .content("{\"deviceId\":\"invalid-device-id\"}"))
            .andExpect(status().isBadRequest());
    }
}
```

- [ ] **Step 6: 테스트 실행**

```bash
cd api-server
./gradlew test --tests AuthResourceTest
```

Expected: 테스트 통과

- [ ] **Step 7: 커밋**

```bash
git add api-server/
git commit -m "feat: 게스트 인증 구현

- GuestTokenProvider: JWT 생성 (7일 TTL)
- DeviceIdValidator: UUID v4 검증
- POST /api/v1/auth/guest 엔드포인트
- 테스트 코드"
```

---

## Task 4.5: Rate Limiting 구현

**Files:**
- Create: `api-server/src/main/java/com/waste/helper/config/RateLimitConfig.java`
- Create: `api-server/src/main/java/com/waste/helper/security/RateLimitFilter.java`

- [ ] **Step 1: RateLimitConfig 작성 (Bucket4j)**

```java
// api-server/src/main/java/com/waste/helper/config/RateLimitConfig.java

package com.waste.helper.config;

import io.github.bucket4j.*;
import io.github.bucket4j.distributed.proxy.ProxyManager;
import org.springframework.context.annotation.*;
import org.springframework.data.redis.core.RedisTemplate;

import java.time.Duration;

@Configuration
public class RateLimitConfig {

    @Bean
    public Bucket guestBucket() {
        // 게스트: 30회/일
        return Bucket.builder()
            .addLimit(Bandwidth.classic(30, Refill.intervally(30, Duration.ofDays(1))))
            .build();
    }

    @Bean
    public Bucket userBucket() {
        // 유저: 100회/일
        return Bucket.builder()
            .addLimit(Bandwidth.classic(100, Refill.intervally(100, Duration.ofDays(1))))
            .build();
    }

    @Bean
    public Bucket ipRateLimitBucket() {
        // IP당 분당 10회
        return Bucket.builder()
            .addLimit(Bandwidth.classic(10, Refill.intervally(10, Duration.ofMinutes(1))))
            .build();
    }
}
```

- [ ] **Step 2: RateLimitFilter 작성**

```java
// api-server/src/main/java/com/waste/helper/security/RateLimitFilter.java

package com.waste.helper.security;

import io.github.bucket4j.*;
import jakarta.servlet.*;
import jakarta.servlet.http.*;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

import java.io.IOException;

@Component
public class RateLimitFilter implements Filter {

    private final Bucket guestBucket;
    private final Bucket userBucket;
    private final Bucket ipBucket;

    public RateLimitFilter(Bucket guestBucket, Bucket userBucket, Bucket ipBucket) {
        this.guestBucket = guestBucket;
        this.userBucket = userBucket;
        this.ipBucket = ipBucket;
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpRequest = (HttpServletRequest) request;

        // VLM 분류 API에만 적용
        if (!httpRequest.getRequestURI().startsWith("/api/v1/classify")) {
            chain.doFilter(request, response);
            return;
        }

        // IP 기본 제한 확인
        String clientIp = getClientIp(httpRequest);
        if (!ipBucket.tryConsume(1)) {
            ((HttpServletResponse) response).sendError(429, "Too Many Requests - IP limit exceeded");
            return;
        }

        // 사용자/게스트별 제한
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        Bucket targetBucket = (auth != null && auth.isAuthenticated() && !"GUEST".equals(auth.getAuthorities().iterator().next().getAuthority()))
            ? userBucket
            : guestBucket;

        if (!targetBucket.tryConsume(1)) {
            ((HttpServletResponse) response).sendError(429, "Too Many Requests - Daily limit exceeded");
            return;
        }

        chain.doFilter(request, response);
    }

    private String getClientIp(HttpServletRequest request) {
        String xfHeader = request.getHeader("X-Forwarded-For");
        if (xfHeader == null) {
            return request.getRemoteAddr();
        }
        return xfHeader.split(",")[0];
    }
}
```

- [ ] **Step 3: SecurityConfig에 Filter 등록**

```java
// SecurityConfig.java에 추가
http.addFilterBefore(rateLimitFilter, UsernamePasswordAuthenticationFilter.class);
```

- [ ] **Step 4: build.gradle에 Bucket4j 의존성 추가**

```gradle
implementation 'com.bucket4j:bucket4j-core:8.7.0'
```

- [ ] **Step 5: 테스트 작성**

```java
// api-server/src/test/java/com/waste/helper/security/RateLimitFilterTest.java

package com.waste.helper.security;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class RateLimitFilterTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void rateLimit_exceedsIpLimit_returns429() throws Exception {
        // IP 제한 (10회/분) 초과 테스트
        for (int i = 0; i < 11; i++) {
            mockMvc.perform(post("/api/v1/classify/detail"))
                .andExpect(i < 10 ? status().isBadRequest() : status().isTooManyRequests());
        }
    }
}
```

- [ ] **Step 6: 커밋**

```bash
git add api-server/
git commit -m "feat: Rate Limiting 구현

- Bucket4j 기반 요청 제한
- 게스트 30회/일, 유저 100회/일
- IP당 분당 10회 제한
- RateLimitFilter 적용"
```

---

## Task 5: gRPC Proto 정의 및 클라이언트

**Files:**
- Create: `api-server/src/main/resources/proto/vlm_service.proto`
- Create: `api-server/src/main/java/com/waste/helper/grpc/VlmGrpcClient.java`
- Create: `vlm-service/proto/vlm_service.proto`

- [ ] **Step 1: Proto 파일 작성 (API 서버)**

```protobuf
syntax = "proto3";

package vlm;

service VLMInference {
  rpc AnalyzeWaste(AnalyzeRequest) returns (AnalyzeResponse);
}

message AnalyzeRequest {
  bytes image_data = 1;
  string yolo_class = 2;
  float confidence = 3;
  string region_code = 4;
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
  string waste_type = 1;
  DisposalMethod disposal_method = 2;
  string cost_info = 3;
  string warnings = 4;
  float confidence = 5;
}
```

- [ ] **Step 2: Proto 파일 복사 (VLM 서비스)**

```bash
cp api-server/src/main/resources/proto/vlm_service.proto vlm-service/proto/
```

- [ ] **Step 3: Gradle gRPC 설정 추가**

Modify: `api-server/build.gradle`

```gradle
// api-server/build.gradle

plugins {
    id 'com.google.protobuf' version '0.9.4'
}

protobuf {
    protoc {
        artifact = "com.google.protobuf:protoc:3.24.0"
    }
    plugins {
        grpc {
            artifact = "io.grpc:protoc-gen-grpc-java:1.59.0"
        }
    }
    generateProtoTasks {
        all()*.plugins {
            grpc {}
        }
    }
}

dependencies {
    implementation 'io.grpc:grpc-netty-shaded:1.59.0'
    implementation 'io.grpc:grpc-protobuf:1.59.0'
    implementation 'io.grpc:grpc-stub:1.59.0'
    implementation 'javax.annotation:javax.annotation-api:1.3.2'
}
```

- [ ] **Step 4: VlmGrpcClient 작성**

```java
package com.waste.helper.grpc;

import io.grpc.*;
import org.springframework.stereotype.Service;
import vlm.VLMInferenceGrpc;
import vlm.Vlm.*;

@Service
public class VlmGrpcClient {

    private final ManagedChannel channel;
    private final VLMInferenceGrpc.VLMInferenceBlockingStub stub;

    public VlmGrpcClient() {
        this.channel = ManagedChannelBuilder
            .forAddress("vlm-service", 50051)
            .usePlaintext()
            .build();
        this.stub = VLMInferenceGrpc.newBlockingStub(channel);
    }

    public AnalyzeResponse analyzeWaste(byte[] imageData, String yoloClass,
                                        float confidence, String regionCode) {
        AnalyzeRequest request = AnalyzeRequest.newBuilder()
            .setImageData(com.google.protobuf.ByteString.copyFrom(imageData))
            .setYoloClass(yoloClass)
            .setConfidence(confidence)
            .setRegionCode(regionCode != null ? regionCode : "")
            .build();

        return stub.analyzeWaste(request);
    }

    public void shutdown() throws InterruptedException {
        channel.shutdown().awaitTermination(5, java.util.concurrent.TimeUnit.SECONDS);
    }
}
```

- [ ] **Step 5: gRPC 설정 (Circuit Breaker 포함)**

Create: `api-server/src/main/java/com/waste/helper/config/GrpcConfig.java`

```java
package com.waste.helper.config;

import io.github.resilience4j.circuitbreaker.*;
import io.github.resilience4j.retry.*;
import org.springframework.context.annotation.*;
import org.waste.helper.grpc.VlmGrpcClient;

@Configuration
public class GrpcConfig {

    @Bean
    public CircuitBreaker vlmCircuitBreaker() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(50)
            .waitDurationInOpenState(java.time.Duration.ofSeconds(30))
            .permittedNumberOfCallsInHalfOpenState(3)
            .slidingWindowSize(10)
            .build();

        return CircuitBreaker.of("vlm-service", config);
    }

    @Bean
    public Retry vlmRetry() {
        RetryConfig config = RetryConfig.custom()
            .maxAttempts(2)
            .waitDuration(java.time.Duration.ofSeconds(1))
            .build();

        return Retry.of("vlm-service", config);
    }

    @Bean
    public VlmGrpcClient vlmGrpcClient() {
        return new VlmGrpcClient();
    }
}
```

- [ ] **Step 6: Proto 컴파일**

```bash
cd api-server
./gradlew generateProto
```

Expected: `build/generated/source/proto/main/`에 Java 코드 생성

- [ ] **Step 7: 커밋**

```bash
git add api-server/ vlm-service/proto/
git commit -m "feat: gRPC Proto 정의 및 클라이언트

- vlm_service.proto 정의
- VlmGrpcClient: gRPC 클라이언트
- Circuit Breaker + Retry 설정
- Gradle protobuf 플러그인"
```

---

## Task 6: VLM 서비스 구현 (Python)

**Files:**
- Create: `vlm-service/requirements.txt`
- Create: `vlm-service/app/main.py`
- Create: `vlm-service/app/grpc_server.py`
- Create: `vlm-service/app/vlm_engine.py`
- Create: `vlm-service/app/prompt.py`
- Create: `vlm-service/app/config.py`
- Create: `vlm-service/Dockerfile`

- [ ] **Step 1: requirements.txt 작성**

```txt
# vlm-service/requirements.txt

fastapi==0.109.0
uvicorn[standard]==0.27.0
grpcio==1.60.0
grpcio-tools==1.60.0
protobuf==4.25.1
vllm==0.2.7
torch==2.1.0
transformers==4.36.0
pillow==10.2.0
pydantic==2.5.3
python-dotenv==1.0.0
```

- [ ] **Step 2: config.py 작성**

```python
# vlm-service/app/config.py

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
```

- [ ] **Step 3: prompt.py 작성**

```python
# vlm-service/app/prompt.py

SYSTEM_PROMPT = """당신은 한국 폐기물 분리배출 전문가입니다.

제공된 이미지와 YOLO 1차 분류 결과를 바탕으로:
1. 폐기물 종류 확인
2. 올바른 배출 요령 안내
3. 지역별 특이사항 반영
4. 처리 비용 안내
5. 주의사항 표기

답변은 한국어로, 명확하고 친절하게 작성하세요."""

PROMPT_TEMPLATE = """
[YOLO 1차 분류 결과]
- 분류: {yolo_class}
- 신뢰도: {confidence:.2%}

[사용자 지역]
{region_info}

위 정보와 이미지를 바탕으로 분석 결과를 JSON 형식으로 출력하세요:
{{
  "waste_type": "최종 분류",
  "disposal_method": {{
    "method": "배출 방법",
    "notes": ["주의사항1", "주의사항2"],
    "items": [{{"label": "부분명", "action": "처리방법"}}]
  }},
  "cost_info": "비용 정보",
  "warnings": "주의사항",
  "confidence": 0.0-1.0
}}
"""
```

- [ ] **Step 4: vlm_engine.py 작성**

```python
# vlm-service/app/vlm_engine.py

from vllm import LLM, SamplingParams
from .config import settings
from .prompt import SYSTEM_PROMPT, PROMPT_TEMPLATE

class VLMEngine:
    def __init__(self):
        self.llm = LLM(
            model=settings.model_name,
            max_model_len=settings.max_model_len,
            gpu_memory_utilization=settings.gpu_memory_utilization,
            trust_remote_code=settings.trust_remote_code
        )
        self.sampling_params = SamplingParams(
            temperature=0.1,
            max_tokens=2048
        )

    def analyze(self, image_bytes: bytes, yolo_class: str,
                confidence: float, region: str) -> dict:
        region_info = f"{region} 지역 기준" if region else "기본 지역 기준"

        prompt = PROMPT_TEMPLATE.format(
            yolo_class=yolo_class,
            confidence=confidence,
            region_info=region_info
        )

        # vLLM 추론
        inputs = {
            "prompt": SYSTEM_PROMPT + "\n\n" + prompt,
            "multi_modal_data": {"image": image_bytes}
        }

        outputs = self.llm.generate([inputs], self.sampling_params)
        response_text = outputs[0].outputs[0].text

        # JSON 파싱
        import json
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback: 텍스트에서 JSON 추론
            return self._parse_json_from_text(response_text)

    def _parse_json_from_text(self, text: str) -> dict:
        # 간단한 fallback 파싱 로직
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass

        # 최소 기본 반환
        return {
            "waste_type": "분류 불가",
            "disposal_method": {"method": "다시 시도해주세요", "notes": [], "items": []},
            "cost_info": "",
            "warnings": "분류 실패",
            "confidence": 0.0
        }
```

- [ ] **Step 5: grpc_server.py 작성**

```python
# vlm-service/app/grpc_server.py

import grpc
from concurrent import futures
import vlm_service_pb2
import vlm_service_pb2_grpc
from .vlm_engine import VLMEngine

class VLMInferenceServicer(vlm_service_pb2_grpc.VLMInferenceServicer):
    def __init__(self):
        self.engine = VLMEngine()

    def AnalyzeWaste(self, request, context):
        try:
            result = self.engine.analyze(
                image_bytes=request.image_data,
                yolo_class=request.yolo_class,
                confidence=request.confidence,
                region=request.region_code
            )

            # DisposalMethod 변환
            items = [
                vlm_service_pb2.DisposalItem(label=item["label"], action=item["action"])
                for item in result.get("disposal_method", {}).get("items", [])
            ]

            disposal_method = vlm_service_pb2.DisposalMethod(
                method=result.get("disposal_method", {}).get("method", ""),
                notes=result.get("disposal_method", {}).get("notes", []),
                items=items
            )

            return vlm_service_pb2.AnalyzeResponse(
                waste_type=result.get("waste_type", ""),
                disposal_method=disposal_method,
                cost_info=result.get("cost_info", ""),
                warnings=result.get("warnings", ""),
                confidence=result.get("confidence", 0.0)
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"VLM inference failed: {str(e)}")
            return vlm_service_pb2.AnalyzeResponse()

def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    vlm_service_pb2_grpc.add_VLMInferenceServicer_to_server(
        VLMInferenceServicer(), server
    )
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    print(f"VLM gRPC server started on port {port}")
    server.wait_for_termination()
```

- [ ] **Step 6: main.py 작성 (HTTP health check용)**

```python
# vlm-service/app/main.py

from fastapi import FastAPI
from .grpc_server import serve

app = FastAPI(title="VLM Service")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "vlm-service"}

if __name__ == "__main__":
    import uvicorn
    import threading

    # gRPC 서버를 별도 스레드에서 실행
    grpc_thread = threading.Thread(target=serve, kwargs={"port": 50051})
    grpc_thread.daemon = True
    grpc_thread.start()

    # HTTP 서버 실행
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

- [ ] **Step 7: Dockerfile 작성**

```dockerfile
# vlm-service/Dockerfile

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
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/vlm_service.proto

# 앱 코드
COPY app ./app

EXPOSE 50051 8000

CMD ["python", "-m", "app.main"]
```

- [ ] **Step 8: 커밋**

```bash
git add vlm-service/
git commit -m "feat: VLM 서비스 구현

- FastAPI + gRPC 서버
- vLLM 기반 Qwen3-VL-4B 추론 엔진
- 시스템 프롬프트 및 응답 파싱
- Dockerfile"
```

---

## Task 7: 분류 API 구현

**Files:**
- Create: `api-server/src/main/java/com/waste/helper/service/ClassificationService.java`
- Create: `api-server/src/main/java/com/waste/helper/service/dto/ClassifyDetailRequest.java`
- Create: `api-server/src/main/java/com/waste/helper/service/dto/ClassifyDetailResponse.java`
- Create: `api-server/src/main/java/com/waste/helper/web/rest/ClassificationResource.java`
- Create: `api-server/src/main/java/com/waste/helper/service/CacheService.java`

- [ ] **Step 1: DTO 작성**

```java
// api-server/src/main/java/com/waste/helper/service/dto/ClassifyDetailRequest.java

package com.waste.helper.service.dto;

public record ClassifyDetailRequest(
    String detectedClass,
    float confidence,
    String regionCode
) {}
```

```java
// api-server/src/main/java/com/waste/helper/service/dto/ClassifyDetailResponse.java

package com.waste.helper.service.dto;

import java.util.List;

public record ClassifyDetailResponse(
    String detectedClass,
    String confirmedClass,
    float confidence,
    DisposalMethodResponse disposalMethod,
    CostInfoResponse costInfo,
    List<String> warnings,
    String regionSpecific,
    String source,
    boolean cached
) {}

public record DisposalMethodResponse(
    String method,
    List<String> notes,
    List<DisposalItemResponse> items
) {}

public record DisposalItemResponse(
    String label,
    String action
) {}

public record CostInfoResponse(
    String type,
    int amount,
    String currency,
    String collectionSchedule,
    String notes
) {}
```

- [ ] **Step 2: CacheService 작성**

```java
// api-server/src/main/java/com/waste/helper/service/CacheService.java

package com.waste.helper.service;

import org.springframework.data.redis.core.*;
import org.springframework.stereotype.Service;
import java.util.concurrent.TimeUnit;

@Service
public class CacheService {

    private final RedisTemplate<String, Object> redisTemplate;

    private static final String CLASSIFY_CACHE_PREFIX = "classify:";
    private static final long CACHE_TTL_HOURS = 24;

    public CacheService(RedisTemplate<String, Object> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public ClassifyDetailResponse getCachedClassification(String cacheKey) {
        return (ClassifyDetailResponse) redisTemplate.opsForValue()
            .get(CLASSIFY_CACHE_PREFIX + cacheKey);
    }

    public void cacheClassification(String cacheKey, ClassifyDetailResponse response) {
        redisTemplate.opsForValue().set(
            CLASSIFY_CACHE_PREFIX + cacheKey,
            response,
            CACHE_TTL_HOURS,
            TimeUnit.HOURS
        );
    }

    private String generateCacheKey(String detectedClass, String regionCode) {
        return detectedClass + ":" + (regionCode != null ? regionCode : "default");
    }
}
```

- [ ] **Step 3: ClassificationService 작성**

```java
// api-server/src/main/java/com/waste/helper/service/ClassificationService.java

package com.waste.helper.service;

import com.waste.helper.grpc.*;
import com.waste.helper.service.dto.*;
import io.github.resilience4j.circuitbreaker.*;
import io.github.resilience4j.retry.*;
import org.springframework.stereotype.*;
import org.springframework.web.multipart.*;
import vlm.*;

import java.io.IOException;
import java.util.*;

@Service
public class ClassificationService {

    private final VlmGrpcClient vlmClient;
    private final CacheService cacheService;
    private final CircuitBreaker circuitBreaker;
    private final Retry retry;

    public ClassificationService(VlmGrpcClient vlmClient, CacheService cacheService,
                               CircuitBreaker vlmCircuitBreaker, Retry vlmRetry) {
        this.vlmClient = vlmClient;
        this.cacheService = cacheService;
        this.circuitBreaker = vlmCircuitBreaker;
        this.retry = vlmRetry;
    }

    public ClassifyDetailResponse classifyDetail(
        MultipartFile image,
        String detectedClass,
        float confidence,
        String regionCode
    ) throws IOException {
        String cacheKey = detectedClass + ":" + (regionCode != null ? regionCode : "default");

        // 캐시 확인
        ClassifyDetailResponse cached = cacheService.getCachedClassification(cacheKey);
        if (cached != null) {
            return new ClassifyDetailResponse(
                cached.detectedClass(),
                cached.confirmedClass(),
                cached.confidence(),
                cached.disposalMethod(),
                cached.costInfo(),
                cached.warnings(),
                cached.regionSpecific(),
                cached.source(),
                true
            );
        }

        // Circuit Breaker + Retry 데코레이션
        Callable<ClassifyDetailResponse> callable = CircuitBreaker.decorateCallable(
            circuitBreaker,
            Retry.decorateCallable(retry, () -> {
                try {
                    AnalyzeResponse response = vlmClient.analyzeWaste(
                        image.getBytes(),
                        detectedClass,
                        confidence,
                        regionCode
                    );
                    return mapToResponse(response, regionCode);
                } catch (Exception e) {
                    throw new RuntimeException("VLM call failed", e);
                }
            })
        );

        try {
            ClassifyDetailResponse result = callable.call();
            // 캐시 저장
            cacheService.cacheClassification(cacheKey, result);
            return result;
        } catch (Exception e) {
            // Fallback: YOLO 결과만 반환
            return createFallbackResponse(detectedClass, confidence);
        }
    }

    private ClassifyDetailResponse mapToResponse(AnalyzeResponse response, String regionCode) {
        // gRPC 응답 → DTO 변환
        // (상세 구현 생략)
        return new ClassifyDetailResponse(
            response.getWasteType(),
            response.getWasteType(),
            response.getConfidence(),
            new DisposalMethodResponse(
                response.getDisposalMethod().getMethod(),
                List.of(response.getDisposalMethod().getNotesList().toArray(new String[0])),
                response.getDisposalMethod().getItemsList().stream()
                    .map(item -> new DisposalItemResponse(item.getLabel(), item.getAction()))
                    .toList()
            ),
            new CostInfoResponse("무료", 0, "KRW", null, null),
            List.of(response.getWarnings()),
            regionCode != null ? "지역별 정보 있음" : null,
            "VLM_ANALYSIS",
            false
        );
    }

    private ClassifyDetailResponse createFallbackResponse(String detectedClass, float confidence) {
        return new ClassifyDetailResponse(
            detectedClass,
            detectedClass,
            confidence,
            new DisposalMethodResponse("기본 배출 요령", List.of(), List.of()),
            new CostInfoResponse("알 수 없음", 0, "KRW", null, null),
            List.of("VLM 서비스 일시 장애"),
            null,
            "YOLO_ONLY",
            false
        );
    }
}
```

- [ ] **Step 4: ClassificationResource 작성**

```java
// api-server/src/main/java/com/waste/helper/web/rest/ClassificationResource.java

package com.waste.helper.web.rest;

import com.waste.helper.service.*;
import com.waste.helper.service.dto.*;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.*;

@RestController
@RequestMapping("/api/v1")
public class ClassificationResource {

    private final ClassificationService classificationService;

    public ClassificationResource(ClassificationService classificationService) {
        this.classificationService = classificationService;
    }

    @PostMapping(value = "/classify/detail", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<ClassifyDetailResponse> classifyDetail(
        @RequestParam("image") MultipartFile image,
        @RequestParam("yoloResult") String yoloResultJson
    ) {
        try {
            // yoloResult JSON 파싱
            // (Jackson ObjectMapper 사용)

            ClassifyDetailResponse response = classificationService.classifyDetail(
                image,
                detectedClass,
                confidence,
                regionCode
            );
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}
```

- [ ] **Step 5: 테스트 작성**

```java
// api-server/src/test/java/com/waste/helper/service/ClassificationServiceTest.java

package com.waste.helper.service;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.mock.web.MockMultipartFile;

import static org.assertj.core.api.Assertions.*;

@SpringBootTest
class ClassificationServiceTest {

    @Autowired
    private ClassificationService classificationService;

    @Test
    void classifyDetail_withValidImage_returnsResponse() throws Exception {
        MockMultipartFile image = new MockMultipartFile(
            "image", "test.jpg", "image/jpeg", "test image".getBytes()
        );

        ClassifyDetailResponse response = classificationService.classifyDetail(
            image, "플라스틱", 0.95f, null
        );

        assertThat(response).isNotNull();
        assertThat(response.detectedClass()).isEqualTo("플라스틱");
    }
}
```

- [ ] **Step 6: 테스트 실행**

```bash
cd api-server
./gradlew test --tests ClassificationServiceTest
```

Expected: 테스트 통과

- [ ] **Step 7: 커밋**

```bash
git add api-server/
git commit -m "feat: 분류 API 구현

- POST /api/v1/classify/detail 엔드포인트
- Redis 캐싱 (24h TTL)
- Circuit Breaker + Retry 폴백
- YOLO 전용 응답"
```

---

## Task 8: 배출 요령 API 구현

**Files:**
- Create: `api-server/src/main/java/com/waste/helper/service/DisposalGuideService.java`
- Modify: `api-server/src/main/java/com/waste/helper/web/rest/DisposalGuideResource.java`

- [ ] **Step 1: DisposalGuideService 작성**

```java
// api-server/src/main/java/com/waste/helper/service/DisposalGuideService.java

package com.waste.helper.service;

import com.waste.helper.repository.*;
import com.waste.helper.domain.*;
import org.springframework.stereotype.*;
import java.util.*;

@Service
public class DisposalGuideService {

    private final DisposalGuideRepository disposalGuideRepository;
    private final RegionRepository regionRepository;

    public DisposalGuideService(DisposalGuideRepository disposalGuideRepository,
                                RegionRepository regionRepository) {
        this.disposalGuideRepository = disposalGuideRepository;
        this.regionRepository = regionRepository;
    }

    // 지역별 배출 요령 우선순위 로직
    public Optional<DisposalGuide> findByRegionAndWasteType(String regionCode, String wasteType) {
        // 1순위: 공공데이터 (source = PUBLIC_API)
        Optional<DisposalGuide> publicApiGuide = disposalGuideRepository
            .findByRegionEmdCodeAndWasteTypeAndSource(regionCode, wasteType, Source.PUBLIC_API);
        if (publicApiGuide.isPresent()) {
            return publicApiGuide;
        }

        // 2순위: LLM 보완 (source = LLM_SUPPLEMENTED)
        return disposalGuideRepository
            .findByRegionEmdCodeAndWasteTypeAndSource(regionCode, wasteType, Source.LLM_SUPPLEMENTED);
    }

    public List<DisposalGuide> findByWasteType(String wasteType) {
        return disposalGuideRepository.findByWasteType(wasteType);
    }
}
```

- [ ] **Step 2: DisposalGuideRepository 수정**

```java
// api-server/src/main/java/com/waste/helper/repository/DisposalGuideRepository.java

package com.waste.helper.repository;

import com.waste.helper.domain.*;
import org.springframework.data.jpa.repository.*;
import java.util.*;

public interface DisposalGuideRepository extends JpaRepository<DisposalGuide, Long> {

    Optional<DisposalGuide> findByRegionEmdCodeAndWasteTypeAndSource(
        String regionCode, String wasteType, Source source
    );

    List<DisposalGuide> findByWasteType(String wasteType);
}
```

- [ ] **Step 3: DisposalGuideResource 작성**

```java
// api-server/src/main/java/com/waste/helper/web/rest/DisposalGuideResource.java

package com.waste.helper.web.rest;

import com.waste.helper.service.*;
import com.waste.helper.domain.*;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/disposal-guide")
public class DisposalGuideResource {

    private final DisposalGuideService disposalGuideService;

    public DisposalGuideResource(DisposalGuideService disposalGuideService) {
        this.disposalGuideService = disposalGuideService;
    }

    @GetMapping
    public ResponseEntity<?> getDisposalGuide(
        @RequestParam String wasteType,
        @RequestParam(required = false) String regionCode
    ) {
        if (regionCode != null) {
            Optional<DisposalGuide> guide = disposalGuideService
                .findByRegionAndWasteType(regionCode, wasteType);
            if (guide.isPresent()) {
                return ResponseEntity.ok(guide.get());
            }
            // 지역별 없으면 기본 반환
            return ResponseEntity.ok(
                disposalGuideService.findByWasteType(wasteType)
            );
        }
        return ResponseEntity.ok(disposalGuideService.findByWasteType(wasteType));
    }
}
```

- [ ] **Step 4: 커밋**

```bash
git add api-server/
git commit -m "feat: 배출 요령 API 구현

- GET /api/v1/disposal-guide 엔드포인트
- 지역별 우선순위 로직 (공공데이터 → LLM 보완)
- Repository 쿼리 메서드 추가"
```

---

## Task 8.5: Region API 구현

**Files:**
- Create: `api-server/src/main/java/com/waste/helper/service/RegionService.java`
- Create: `api-server/src/main/java/com/waste/helper/web/rest/RegionResource.java`

- [ ] **Step 1: RegionService 작성**

```java
// api-server/src/main/java/com/waste/helper/service/RegionService.java

package com.waste.helper.service;

import com.waste.helper.repository.*;
import com.waste.helper.domain.*;
import org.springframework.stereotype.*;
import java.util.*;

@Service
public class RegionService {

    private final RegionRepository regionRepository;

    public RegionService(RegionRepository regionRepository) {
        this.regionRepository = regionRepository;
    }

    public List<Region> findAll() {
        return regionRepository.findAll();
    }

    public Optional<Region> findByEmdCode(String emdCode) {
        return regionRepository.findByEmdCode(emdCode);
    }

    public List<Region> findBySido(String sido) {
        return regionRepository.findBySido(sido);
    }

    public List<Region> searchByKeyword(String keyword) {
        return regionRepository.findBySidoContainingOrSigunguContainingOrEmdNameContaining(
            keyword, keyword, keyword
        );
    }
}
```

- [ ] **Step 2: RegionRepository 커스텀 메서드 추가**

```java
// api-server/src/main/java/com/waste/helper/repository/RegionRepository.java

package com.waste.helper.repository;

import com.waste.helper.domain.*;
import org.springframework.data.jpa.repository.*;
import java.util.*;

public interface RegionRepository extends JpaRepository<Region, Long> {

    Optional<Region> findByEmdCode(String emdCode);

    List<Region> findBySido(String sido);

    List<Region> findBySidoContainingOrSigunguContainingOrEmdNameContaining(
        String sido, String sigungu, String emdName
    );
}
```

- [ ] **Step 3: RegionResource 작성**

```java
// api-server/src/main/java/com/waste/helper/web/rest/RegionResource.java

package com.waste.helper.web.rest;

import com.waste.helper.service.*;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/regions")
public class RegionResource {

    private final RegionService regionService;

    public RegionResource(RegionService regionService) {
        this.regionService = regionService;
    }

    @GetMapping
    public ResponseEntity<?> getRegions(
        @RequestParam(required = false) String sido,
        @RequestParam(required = false) String keyword
    ) {
        if (keyword != null) {
            return ResponseEntity.ok(regionService.searchByKeyword(keyword));
        }
        if (sido != null) {
            return ResponseEntity.ok(regionService.findBySido(sido));
        }
        return ResponseEntity.ok(regionService.findAll());
    }

    @GetMapping("/{emdCode}")
    public ResponseEntity<?> getRegion(@PathVariable String emdCode) {
        return regionService.findByEmdCode(emdCode)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/{emdCode}/schedule")
    public ResponseEntity<?> getSchedule(@PathVariable String emdCode) {
        // 수거 일정은 DisposalGuide를 통해 제공
        // Phase 2에서 공공데이터 연동 시 상세 구현
        return regionService.findByEmdCode(emdCode)
            .map(region -> ResponseEntity.ok().build())
            .orElse(ResponseEntity.notFound().build());
    }
}
```

- [ ] **Step 4: 테스트 작성**

```java
// api-server/src/test/java/com/waste/helper/web/rest/RegionResourceTest.java

package com.waste.helper.web.rest;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class RegionResourceTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void getRegions_returnsList() throws Exception {
        mockMvc.perform(get("/api/v1/regions"))
            .andExpect(status().isOk());
    }

    @Test
    void getRegionByCode_existing_returns200() throws Exception {
        mockMvc.perform(get("/api/v1/regions/00000000"))
            .andExpect(status().isOk());
    }

    @Test
    void getRegionByCode_nonexistent_returns404() throws Exception {
        mockMvc.perform(get("/api/v1/regions/INVALID"))
            .andExpect(status().isNotFound());
    }
}
```

- [ ] **Step 5: 커밋**

```bash
git add api-server/
git commit -m "feat: Region API 구현

- GET /api/v1/regions (시도/키워드 필터)
- GET /api/v1/regions/{emdCode}
- GET /api/v1/regions/{emdCode}/schedule
- RegionRepository 커스텀 쿼리"
```

---

## Task 9: K8s 매니페스트 작성 (Phase 1)

**Files:**
- Create: `k8s/manifests/namespace.yaml`
- Create: `k8s/manifests/postgres-statefulset.yaml`
- Create: `k8s/manifests/redis-deployment.yaml`
- Create: `k8s/manifests/api-server-deployment.yaml`
- Create: `k8s/manifests/vlm-deployment.yaml`
- Create: `k8s/manifests/vlm-hpa.yaml`
- Create: `k8s/manifests/ingress.yaml`
- Create: `k8s/manifests/networkpolicy.yaml`

- [ ] **Step 1: namespace.yaml 작성**

```yaml
# k8s/manifests/namespace.yaml

apiVersion: v1
kind: Namespace
metadata:
  name: waste-helper
  labels:
    name: waste-helper
```

- [ ] **Step 1.5: postgres-secret.yaml 작성**

```yaml
# k8s/manifests/postgres-secret.yaml

apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: waste-helper
type: Opaque
stringData:
  password: "your-secure-postgres-password"  # 운영환경에서는 Sealed Secrets 등으로 대체
```

**Note:** 운영 환경에서는 `kubeseal` 등을 사용하여 Sealed Secrets로 변환 권장

- [ ] **Step 2: postgres-statefulset.yaml 작성**

```yaml
# k8s/manifests/postgres-statefulset.yaml

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: waste-helper
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: waste-helper
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        env:
        - name: POSTGRES_DB
          value: wastehelper
        - name: POSTGRES_USER
          value: wastehelper
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: waste-helper
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
  clusterIP: None
```

- [ ] **Step 3: redis-deployment.yaml 작성**

```yaml
# k8s/manifests/redis-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: waste-helper
spec:
  replicas: 1
  selector:
    matchLabels:
    app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"

---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: waste-helper
spec:
  selector:
    app: redis
  ports:
  - port: 6379
```

- [ ] **Step 4: api-server-deployment.yaml 작성**

```yaml
# k8s/manifests/api-server-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
  namespace: waste-helper
spec:
  replicas: 1
  selector:
    matchLabels:
    app: api-server
  template:
    metadata:
      labels:
        app: api-server
    spec:
      containers:
      - name: api-server
        image: api-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "prod"
        - name: SPRING_DATASOURCE_URL
          value: "jdbc:postgresql://postgres:5432/wastehelper"
        - name: SPRING_REDIS_HOST
          value: "redis"
        - name: VLM_SERVICE_URL
          value: "vlm-service:50051"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /management/health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /management/health/readiness
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: api-server
  namespace: waste-helper
spec:
  selector:
    app: api-server
  ports:
  - port: 8080
```

- [ ] **Step 5: vlm-deployment.yaml 작성**

```yaml
# k8s/manifests/vlm-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: vlm-service
  namespace: waste-helper
spec:
  replicas: 1
  selector:
    matchLabels:
    app: vlm-service
  template:
    metadata:
      labels:
        app: vlm-service
    spec:
      containers:
      - name: vlm-service
        image: vlm-service:latest
        ports:
        - containerPort: 50051
          name: grpc
        - containerPort: 8000
          name: http
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
          initialDelaySeconds: 60
          periodSeconds: 30

---
apiVersion: v1
kind: Service
metadata:
  name: vlm-service
  namespace: waste-helper
spec:
  selector:
    app: vlm-service
  ports:
  - port: 50051
    name: grpc
  - port: 8000
    name: http
```

- [ ] **Step 6: vlm-hpa.yaml 작성 (Prometheus custom metric)**

```yaml
# k8s/manifests/vlm-hpa.yaml

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vlm-hpa
  namespace: waste-helper
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vlm-service
  minReplicas: 1
  maxReplicas: 3
  metrics:
  - type: Pods
    pods:
      metric:
        name: vlm_request_queue_depth  # Prometheus custom metric
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

- [ ] **Step 7: ingress.yaml 작성**

```yaml
# k8s/manifests/ingress.yaml

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: waste-helper-ingress
  namespace: waste-helper
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.waste-helper.com
    secretName: waste-helper-tls
  rules:
  - host: api.waste-helper.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-server
            port:
              number: 8080
```

- [ ] **Step 8: networkpolicy.yaml 작성**

```yaml
# k8s/manifests/networkpolicy.yaml

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: vlm-service-policy
  namespace: waste-helper
spec:
  podSelector:
    matchLabels:
      app: vlm-service
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api-server
    ports:
    - protocol: TCP
      port: 50051
```

- [ ] **Step 9: 커밋**

```bash
git add k8s/
git commit -m "feat: K8s 매니페스트 (Phase 1)

- Namespace, PostgreSQL, Redis
- API Server Deployment
- VLM Service Deployment + HPA
- Ingress, NetworkPolicy"
```

---

## Task 10: Observability (Prometheus + Grafana)

**Files:**
- Create: `k8s/manifests/prometheus-config.yaml`
- Create: `k8s/manifests/grafana-deployment.yaml`

- [ ] **Step 1: Prometheus ConfigMap 작성**

```yaml
# k8s/manifests/prometheus-config.yaml

apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: waste-helper
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s

    scrape_configs:
    - job_name: 'api-server'
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - waste-helper
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: api-server
        action: keep

    - job_name: 'vlm-service'
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - waste-helper
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: vlm-service
        action: keep
```

- [ ] **Step 2: Prometheus Deployment 작성**

```yaml
# k8s/manifests/prometheus.yaml (추가)

apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: waste-helper
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        args:
        - '--config.file=/etc/prometheus/prometheus.yml'
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        volumes:
        - name: config
          configMap:
            name: prometheus-config

---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: waste-helper
spec:
  selector:
    app: prometheus
  ports:
  - port: 9090
```

- [ ] **Step 3: Grafana Deployment 작성**

```yaml
# k8s/manifests/grafana-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: waste-helper
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "admin"

---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: waste-helper
spec:
  selector:
    app: grafana
  ports:
  - port: 3000
```

- [ ] **Step 4: 커밋**

```bash
git add k8s/
git commit -m "feat: Prometheus + Grafana 배포

- Prometheus ConfigMap
- Grafana Deployment"
```

---

# Phase 1 완료 체크리스트

- [ ] JHipster 프로젝트 생성 및 설정
- [ ] 도메인 모델 정의 (9개 엔티티)
- [ ] 데이터베이스 마이그레이션 (device_users 포함)
- [ ] 게스트 인증 (JWT)
- [ ] Rate Limiting (Bucket4j)
- [ ] gRPC Proto 정의 및 클라이언트
- [ ] VLM 서비스 (Python FastAPI)
- [ ] 분류 API (Circuit Breaker + 캐싱)
- [ ] 배출 요령 API
- [ ] Region API (지역 목록/상세)
- [ ] K8s 매니페스트 완료 (Secret 포함)
- [ ] Observability (Prometheus + Grafana)

---

# Phase 2: 소셜 로그인 + 히스토리 + Vector DB (2주)

**목표:** 소셜 로그인, 검색 기록, 피드백, 공공데이터 연동, Milvus Vector DB

**주요 구현:**
- 소셜 로그인 (Kakao/Naver/Google OAuth2) — `POST /api/v1/auth/social`
- 게스트 → 소셜 계정 마이그레이션
- SearchHistory CRUD — `POST/GET /api/v1/search-histories`
- Feedback CRUD — `POST /api/v1/feedbacks`
- 공공데이터포털 연동 (Spring Batch 스케줄러)
- Milvus Vector DB 배포 및 유사도 검색
- Spring Cloud Gateway 도입 (Rate Limiting, IP 블랙리스트)
- `springdoc-openapi` 구성

**추가 예정** - Phase 1 완료 후 상세 계획

---

# Phase 3: 고도화 (2주)

**목표:** 대규모 트래픽 대응, 알림 시스템, 모니터링 고도화

**주요 구현:**
- FCM 푸시 알림 (배출 알림, 수거일 알림)
- 분류 결과 캐싱 고도화 (Vector 유사도 기반)
- HPA 커스텀 메트릭 세부 튜닝
- ArgoCD GitOps 파이프라인 구축
- 부하 테스트 (k6/Gatling)
- OpenAPI 문서 자동화

**추가 예정** - Phase 2 완료 후 상세 계획
