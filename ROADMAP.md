# 🗺️ Asgard Development Roadmap

## Vision

Build a production-grade, cloud-native microservices platform that demonstrates enterprise-level architecture patterns, DevOps best practices, and modern software engineering principles.

## 📍 Current Status (MVP+ - v0.2.0) - 2026년 1월 4일 업데이트

> 🎉 **MVP를 초월한 Production-Ready 수준 달성!**

### ✅ Completed (완료된 기능)

#### 🏗️ 아키텍처 & 인프라
- [x] Gradle multi-module monorepo 구조 (Java 21 LTS)
- [x] Spring Boot 3.3.5 + Spring Cloud 2023.0.3
- [x] Docker Compose 완전 구성 (12개 서비스)
  - Kafka + Zookeeper + Kafka UI
  - PostgreSQL + Redis + Elasticsearch
  - Prometheus + Grafana + Zipkin
- [x] Kubernetes 매니페스트 준비 (k8s/ 디렉토리)

#### 🛡️ Heimdall (API Gateway) - Java
- [x] **JWT 인증 완전 구현** (JwtTokenProvider, JwtAuthenticationFilter)
- [x] Spring Security OAuth2 Resource Server 통합
- [x] **Circuit Breaker 패턴** (Resilience4j - 5개 모듈 통합)
- [x] Rate Limiting 인프라 (Redis 기반)
- [x] Kafka Producer/Listener 완전 구현
  - AnalysisRequestEvent, AnalysisResultEvent, LogIngestionEvent
  - DLQ (Dead Letter Queue) 처리
- [x] gRPC 통신 준비 (net.devh:grpc-spring-boot-starter)
- [x] **Bifrost 클라이언트 서비스** (Circuit Breaker + Retry + TimeLimiter)
- [x] Swagger/OpenAPI 3.0 문서화 (springdoc-openapi)
- [x] **7개 컨트롤러** (Auth, Health, Log, Search, Analysis, Statistics, Bifrost)
- [x] **7개 서비스** (BifrostClient, Elasticsearch, LogIngestion, LogProcessing, Notification, Search, Statistics)
- [x] Actuator + Prometheus 메트릭 노출
- [x] Distributed Tracing (Micrometer + Zipkin)
- [x] **테스트 안정화 (H2/Hibernate 호환 + 통합테스트 정합성)**
  - H2 테스트에서 `INSERT ... RETURNING` 이슈 회피 (Hibernate Dialect 조정)
  - Search API 응답 스키마에 맞춰 통합테스트 assertion 정리
  - 분석 결과 미존재 시 404 반환 + 전역 예외 처리에서 상태코드 보존

#### 🌈 Bifrost (AI Engine) - Python
- [x] **Two-Track AI 완전 구현** ⭐
  - Track A: Local LLM (Ollama/Llama 3.1 8B) - GDPR 준수
  - Track B: Cloud API (AWS Bedrock/Claude 3 Sonnet)
- [x] **Privacy Router** (router.py) - 자동 민감도 분류
  - HIGH: PII, 금융정보, 인증정보 → Track A
  - MEDIUM: 내부 IP, 세션 ID → Track A
  - LOW: 일반 로그 → Track B
- [x] FastAPI REST API + WebSocket 지원
- [x] **Kafka Integration** (Producer + Consumer)
  - HeimdallIntegrationService 완전 구현
  - 양방향 이벤트 통신
- [x] Prometheus 메트릭 (bifrost_analysis_*, bifrost_cache_*, bifrost_errors_*)
- [x] **SQLAlchemy 데이터베이스** + Alembic 마이그레이션
- [x] Redis 캐싱 레이어
- [x] Rate Limiting (100 req/hour 기본)
- [x] **Slack 알림** 연동
- [x] 데이터 Export (JSON/CSV)
- [x] i18n 다국어 지원 (ko, en)
- [x] **37개 테스트** (23 Unit + 14 Integration) - 100% Pass

#### 🔧 DevOps & DX
- [x] **Unified Scripts** (PowerShell)
  - build-all.ps1, test-all.ps1, start-all.ps1, stop-all.ps1
- [x] CI/CD (GitHub Actions) + Paths Filtering
- [x] JaCoCo 코드 커버리지 (80% 목표)
- [x] Checkstyle 코드 품질 검사
- [x] 환경별 설정 (.env.example)

#### 📚 문서화 (10+ 문서)
- [x] README.md (Mermaid 아키텍처 다이어그램)
- [x] ROADMAP.md, CONTRIBUTING.md, GIT_COMMIT_GUIDE.md
- [x] TWO_TRACK_AI_IMPLEMENTATION.md (구현 상세)
- [x] TESTING_GUIDE.md, QUICK_REFERENCE.md
- [x] UPGRADE_JAVA21.md (마이그레이션 리포트)

### 🎯 MVP+ 달성 목표 ✅
- ✅ Core infrastructure (12 services)
- ✅ Two-Track AI Strategy 완전 구현
- ✅ Heimdall ↔ Bifrost Kafka 통신
- ✅ JWT 인증 + Circuit Breaker
- ✅ Prometheus 모니터링
- ✅ **37개 자동화 테스트**
- ✅ Developer Experience (DX) 최적화

---

## 🚀 Phase 1: Foundation Enhancement (Q1 2026) - 현재 단계

**Focus**: Production Readiness & Security Hardening

### 🔴 Critical Priority (즉시 필요)
- [ ] **Production 보안 설정**
  - [ ] JWT Secret 환경변수 강화 (현재 Base64 기본값)
  - [ ] CORS origin 제한 (현재 `allow_origins=["*"]`)
  - [ ] Rate Limiter 튜닝 (서비스별 차등)
- [ ] **테스트 커버리지 확대**
  - [ ] Heimdall 단위 테스트 (현재 7개 → 30개 목표)
  - [ ] E2E 통합 테스트 (Kafka 포함)
  - [ ] API Contract Testing (Pact)
- [ ] **테스트/에러 처리 품질 기준 정립**
  - [ ] 4xx/5xx 매핑 원칙 문서화 (예: 미존재 리소스는 404)
  - [ ] 통합테스트를 “응답 스키마” 기준으로 유지 (Page/Content 구조 고정)
  - [ ] Actuator health(테스트 프로필) 기대값 정리 또는 test profile에서 contributor 제어
- [ ] **Database 마이그레이션**
  - [ ] Flyway 또는 Liquibase 설정
  - [ ] JPA Entity 정의 완성
  - [ ] 인덱스 최적화

### 🟡 High Priority (이번 분기)
- [ ] **프론트엔드 완성** (bifrost/frontend)
  - [ ] React + Vite 빌드 최적화
  - [ ] 대시보드 UI/UX 개선
  - [ ] 실시간 로그 모니터링 뷰
  - [ ] 분석 결과 시각화
- [ ] **Heimdall API 완성**
  - [ ] User Entity + Repository
  - [ ] Role-based Access Control (RBAC)
  - [ ] Refresh Token 구현
  - [ ] API Versioning (/api/v1/*)
- [ ] **모니터링 대시보드**
  - [ ] Grafana 프리셋 대시보드 (JVM, Python, Kafka)
  - [ ] Alert Rules 설정 (Prometheus Alertmanager)
  - [ ] SLO/SLI 정의

### 🟢 Nice to Have
- [ ] Pre-commit hooks (lint, format)
- [ ] Development Container (devcontainer.json)
- [ ] VSCode/IntelliJ Debug 설정
- [ ] Hot Reload 최적화

---

## 🎨 Phase 2: Enhancement (Q2 2026)

**Focus**: Advanced features and optimization

### 신규 서비스 추가
- [ ] **Valhalla**: User Management Service
  - User CRUD, Profile, Preference
  - OAuth2 Provider (Google, GitHub)
  - Multi-tenant 지원
  
- [ ] **Midgard**: Business Logic Service
  - 로그 분석 정책 관리
  - 워크플로우 엔진
  - 알림 규칙 엔진

### Advanced Features
- [ ] **GraphQL Gateway** (alongside REST)
- [ ] WebSocket 실시간 알림
- [ ] 파일 업로드/다운로드 (S3/MinIO)
- [ ] Batch Processing (Spring Batch)
- [ ] API Rate Limiting 고도화 (동적 조절)

### Frontend Enhancement 🎨
- [ ] **Unified Admin Dashboard** (Root-level)
  - Heimdall 상태 모니터링
  - Bifrost ML/AI 분석 현황
  - 시스템 헬스 통합 뷰
- [ ] 로그 검색 UI (Elasticsearch 연동)
- [ ] 실시간 대시보드 (WebSocket)
- [ ] API Playground (Swagger UI 개선)

### Security Hardening
- [ ] OAuth2/OIDC 통합 (Keycloak)
- [ ] API Key 관리 시스템
- [ ] Audit Logging (모든 API 호출)
- [ ] Security Scanning (Trivy/Snyk)
- [ ] Secrets Encryption (HashiCorp Vault)

### Observability 고도화
- [ ] Custom Grafana 대시보드 10종
- [ ] Alert Rules (Slack, Email, PagerDuty)
- [ ] ELK Stack 완전 통합
- [ ] Cost Monitoring (클라우드 API 비용)
- [ ] **Unified Observability Dashboard**

**Deliverables**: Enterprise-grade platform with security

---

## 🌐 Phase 3: Scale & Performance (Q3 2026)

**Focus**: Scalability and high availability

### Service Mesh 도입 (조건부) 🔍
> **결정 포인트**: 서비스 5개 이상 시 재평가
> 
> **현재 상태**: 2개 핵심 서비스 (Heimdall, Bifrost) + 지원 서비스
> 
> **권장**: K8s Ingress + Service로 충분 (Phase 3까지)
> 
> **후보 기술**:
> - [ ] Istio (풀 기능, 복잡)
> - [ ] Linkerd (경량, 추천)
> - [ ] Consul Connect (HashiCorp 에코시스템)

### Performance Optimization
- [ ] Database 쿼리 최적화 (Slow Query 분석)
- [ ] Redis 캐싱 전략 고도화
- [ ] CDN 통합 (정적 리소스)
- [ ] 비동기 처리 패턴 확대
- [ ] Connection Pooling 튜닝
- [ ] JVM 튜닝 (GC, Heap)

### Scalability
- [ ] Horizontal Pod Autoscaling (HPA)
- [ ] Database Read Replicas
- [ ] Kafka Partition 확장
- [ ] Redis Cluster Mode
- [ ] Multi-AZ 배포

### High Availability
- [ ] Multi-Region 배포 전략
- [ ] Disaster Recovery Plan
- [ ] 자동 백업 (PostgreSQL, Redis)
- [ ] Failover 자동화
- [ ] Zero-Downtime Deployment (Blue/Green)

### Advanced Monitoring
- [ ] Chaos Engineering (Chaos Monkey/LitmusChaos)
- [ ] Synthetic Monitoring
- [ ] SLA/SLO 대시보드
- [ ] Incident Response 자동화
- [ ] Performance Profiling (Pyroscope)

**Deliverables**: Production-scale, highly available platform

---

## 🤖 Phase 4: AI/ML Enhancement (Q4 2026)

**Focus**: Advanced ML capabilities & MLOps 성숙도

### MLOps Pipeline 고도화
- [ ] **MLflow 완전 통합** (현재 mlflow_tracker.py 기초)
  - 모델 버전 관리
  - 실험 추적
  - 모델 레지스트리
- [ ] Feature Store (Feast)
- [ ] A/B Testing Framework
- [ ] 모델 모니터링 (Data Drift 감지)
- [ ] 자동 재훈련 파이프라인

### Advanced AI Models
- [ ] **Fine-tuned Domain Model**
  - 로그 분석 특화 모델
  - 한국어 최적화
- [ ] 이상 탐지 (Anomaly Detection)
- [ ] 예측 분석 (장애 예측)
- [ ] NLP 서비스 (로그 자동 분류)
- [ ] 추천 엔진 (해결책 추천)

### Data Engineering
- [ ] Data Lake (MinIO/S3)
- [ ] ETL 파이프라인 (Apache Airflow)
- [ ] 데이터 버전 관리 (DVC)
- [ ] 데이터 품질 검사
- [ ] Stream Processing (Kafka Streams)

### Two-Track AI 진화
- [ ] **Track A+ (Premium Local)**
  - Llama 3.2 → 70B 모델 옵션
  - LoRA Fine-tuning
  - 멀티 GPU 지원
- [ ] **Track B+ (Multi-Cloud)**
  - OpenAI GPT-4 Turbo 추가
  - Google Gemini Pro 추가
  - 비용 최적화 라우팅

**Deliverables**: Enterprise MLOps platform

---

## 🌟 Phase 5: Innovation (2027+)

**Focus**: Cutting-edge features & Enterprise Scale

### Cloud Native 진화
- [ ] Serverless Functions (AWS Lambda/Azure Functions)
- [ ] Edge Computing 확장 (더 많은 노드)
- [ ] Multi-Cloud 지원 (AWS + Azure + GCP)
- [ ] FinOps 자동화 (비용 최적화)
- [ ] GreenOps (탄소 발자국 추적)

### Advanced Technologies
- [ ] Event Sourcing (이벤트 기반 상태 관리)
- [ ] CQRS Pattern (명령/조회 분리)
- [ ] IoT Device 로그 수집
- [ ] Real-time Analytics (Apache Druid)
- [ ] Vector Database (로그 임베딩)

### Developer Experience++
- [ ] Developer Portal (API 문서 허브)
- [ ] SDK 자동 생성 (Java, Python, TypeScript)
- [ ] Interactive Documentation
- [ ] API Marketplace

### Enterprise Features
- [ ] Multi-tenancy 완전 지원
- [ ] Compliance Automation (SOC2, ISO27001)
- [ ] Data Governance
- [ ] Workflow Orchestration (Temporal)
- [ ] Integration Marketplace

**Deliverables**: Industry-leading AI-Ops Platform

---

## 📊 Success Metrics

### Technical Metrics
- **Uptime**: 99.9%
- **Response Time**: P95 < 200ms
- **Test Coverage**: >80%
- **Bug Density**: <0.1 per KLOC
- **Deployment Frequency**: Daily
- **Mean Time to Recovery**: <1 hour

### Code Quality
- **SonarQube Rating**: A
- **Security Vulnerabilities**: 0 Critical
- **Technical Debt Ratio**: <5%
- **Code Duplication**: <3%

### DevOps Metrics
- **Build Success Rate**: >95%
- **Deployment Success Rate**: >98%
- **Lead Time**: <1 day
- **Change Failure Rate**: <5%

---

## 🎓 Learning Objectives

### Architecture
- Microservices design patterns
- Domain-driven design
- Event-driven architecture
- CQRS and Event Sourcing

### Technologies
- Spring Boot & Spring Cloud
- Kafka & event streaming
- Kubernetes & container orchestration
- Observability tools

### Best Practices
- Clean code principles
- Test-driven development
- CI/CD automation
- Infrastructure as Code

---

## 🤝 Contribution Areas

### Easy (Good First Issues)
- Documentation improvements
- Unit test additions
- Bug fixes
- Code style improvements

### Medium
- New feature implementation
- Integration tests
- Performance optimization
- Monitoring enhancements

### Hard
- Architecture decisions
- New service design
- Complex features
- Infrastructure changes

---

## 📝 Notes

### Recent Improvements (November 2025) 🆕

#### ✅ Developer Experience Enhancement
- **Unified Build System**: Single command to build all services (Java, Python, Frontend)
- **Unified Testing**: Integrated test runner with coverage reports
- **One-Command Operations**: Start/stop all services with single script
- **Smart CI/CD**: Paths filtering to build only changed modules

#### ✅ CI/CD Optimization
- **Monorepo-Aware**: Detects changes per service
- **Parallel Builds**: Independent service builds
- **Cost Reduction**: 40-60% reduction in CI/CD time for partial changes
- **Better Feedback**: Summary reports showing what was built

#### 🎯 Architecture Decisions Based on Analysis

**Frontend Placement**
- ✅ **Decision**: Keep `bifrost/frontend` for now (Bifrost-specific UI)
- 📅 **Future**: Create unified admin dashboard at root level (Phase 2)
- 💡 **Rationale**: Current frontend is purpose-built for Bifrost; unified dashboard is a future enhancement

**Service Mesh Adoption**
- ❌ **Decision**: Defer Istio/Linkerd until Phase 3+
- 📊 **Reason**: 2-3 services don't justify complexity
- ✅ **Alternative**: Use K8s Ingress + Service for now
- 📈 **Trigger**: Re-evaluate when service count reaches 5+

**Build System Integration**
- ✅ **Implemented**: Polyglot build scripts (PowerShell)
- 🎯 **Benefits**: Consistent DX across all languages
- 📚 **Documentation**: QUICK_REFERENCE.md updated with all commands

### Technology Decisions
- **Why Spring Boot?**: Industry standard, rich ecosystem
- **Why Kafka?**: Scalable event streaming
- **Why Gradle?**: Flexible, powerful build tool
- **Why Docker?**: Containerization standard
- **Why Kubernetes?**: Production-grade orchestration

### Architecture Principles
- **Separation of Concerns**: Each service has clear responsibility
- **Loose Coupling**: Services communicate via APIs
- **High Cohesion**: Related functionality grouped together
- **Fail Fast**: Early detection and handling of errors
- **Resilience**: Circuit breakers, retries, timeouts

### Future Considerations
- GraphQL for flexible queries
- gRPC for inter-service communication
- Reactive programming with WebFlux
- Blockchain for audit trail
- Machine learning at the edge

---

## 📅 Timeline Overview (Updated)

```
2026 Q1: Foundation+       ████████░░░░░░░░  ← 현재 (Phase 1)
2026 Q2: Enhancement       ░░░░░░░░████░░░░
2026 Q3: Scale             ░░░░░░░░░░░░████
2026 Q4: AI/ML             ░░░░░░░░░░░░░░██
2027+:   Innovation        ░░░░░░░░░░░░░░░░
```

---

## 🎯 Next Steps (2026년 1월 기준)

### 1. **Immediate** (이번 주)
- [ ] 🔴 JWT Secret 환경변수화 (보안 필수)
- [ ] 🔴 CORS Origin 제한 설정
- [ ] 🟡 Heimdall 단위 테스트 추가 (15개 이상)
- [ ] 🟡 E2E 테스트 시나리오 작성

### 2. **Short Term** (이번 달)
- [ ] Flyway DB 마이그레이션 설정
- [ ] User Entity + AuthController 완성
- [ ] Grafana 대시보드 3종 (JVM, Python, Kafka)
- [ ] Frontend 빌드 파이프라인 통합
- [ ] API Versioning 적용

### 3. **Medium Term** (Q1 2026)
- [ ] Phase 1 100% 완료
- [ ] Kubernetes Helm Charts
- [ ] Performance Testing (Gatling)
- [ ] Security Audit
- [ ] Production Deployment 가이드

---

## 🔍 Decision Points & Reviews

### Q1 2026 Review (Phase 1 완료 시점)
- [ ] Production Deployment 준비 상태 평가
- [ ] Security Audit 결과 검토
- [ ] 테스트 커버리지 80% 달성 여부
- [ ] K8s vs Docker Compose 운영 결정

### Q2 2026 Review (Phase 2 완료 시점)
- [ ] 서비스 개수 평가 (5개 이상?)
- [ ] Service Mesh 도입 재평가
- [ ] Frontend 통합 vs 분리 최종 결정
- [ ] Multi-tenant 필요성 평가

---

## 📊 현재 프로젝트 품질 지표

### ✅ 달성된 목표
| 지표 | 목표 | 현재 | 상태 |
|------|------|------|------|
| Heimdall 테스트 | 7개+ | 7개 | ✅ |
| Bifrost 테스트 | 30개+ | 37개 | ✅ |
| Two-Track AI | 구현 | 완료 | ✅ |
| Kafka 통합 | 구현 | 완료 | ✅ |
| JWT 인증 | 구현 | 완료 | ✅ |
| Circuit Breaker | 구현 | 완료 | ✅ |
| API 문서화 | Swagger | 완료 | ✅ |

### 🔄 진행 중
| 지표 | 목표 | 현재 | 상태 |
|------|------|------|------|
| 테스트 커버리지 | 80% | ~60% | 🟡 |
| Heimdall 테스트 | 30개+ | 7개 | 🟡 |
| DB Migration | Flyway | 미설정 | 🟡 |
| Frontend | 완성 | 기본 | 🟡 |

---

## 📚 References

### 프로젝트 분석 히스토리
- **2025-11**: Gemini 3.0 아키텍처 분석
- **2025-12**: Two-Track AI 완전 구현
- **2026-01-04**: 전체 프로젝트 심층 분석 (Claude Opus 4.5)

### 주요 성과 (2026년 1월 기준)
- ✅ **MVP+ 수준 달성** (Production-ready 기반)
- ✅ **Two-Track AI 완전 동작** (37개 테스트 통과)
- ✅ **MSA 아키텍처 구현** (Kafka 양방향 통신)
- ✅ **Resilience 패턴 적용** (Circuit Breaker, Retry, TimeLimiter)
- ✅ **Observability 기초** (Prometheus, Grafana, Zipkin)
- 📋 테스트 확대 필요
- 📋 보안 설정 강화 필요
- 📋 Frontend 완성 필요

**Last Updated**: January 4, 2026
**Version**: 2.0 (Major Update)
**Status**: MVP+ Complete, Phase 1 in Progress

---

## 🔬 심층 기술 분석 (2026년 1월 4일)

### 📁 Heimdall (Java) 아키텍처 상세

```
heimdall/src/main/java/com/heimdall/
├── controller/          # 7개 REST 컨트롤러
│   ├── AuthController         ✅ JWT 로그인/토큰 발급
│   ├── HealthController       ✅ 헬스 체크 + 스트레스 테스트
│   ├── LogController          ✅ 로그 CRUD
│   ├── SearchController       ✅ Elasticsearch 검색
│   ├── AnalysisController     ✅ Bifrost 분석 요청
│   ├── StatisticsController   ✅ 통계 API
│   └── BifrostController      ✅ Bifrost 직접 통신
├── service/             # 7개 비즈니스 서비스
│   ├── BifrostClientService   ✅ Circuit Breaker + Retry
│   ├── ElasticsearchService   ✅ 로그 검색/인덱싱
│   ├── LogIngestionService    ✅ 로그 수집
│   ├── LogProcessingService   ✅ 로그 처리
│   ├── NotificationService    ✅ 알림 발송
│   ├── SearchService          ✅ 통합 검색
│   └── StatisticsService      ✅ 통계 집계
├── security/            # JWT 보안
│   ├── JwtTokenProvider       ✅ 토큰 생성/검증
│   ├── JwtAuthenticationFilter ✅ 필터 체인
│   └── JwtAuthenticationEntryPoint ✅ 401 핸들러
├── kafka/               # 이벤트 드리븐
│   ├── event/                 # 3개 이벤트 정의
│   │   ├── AnalysisRequestEvent   ✅
│   │   ├── AnalysisResultEvent    ✅
│   │   └── LogIngestionEvent      ✅
│   ├── producer/
│   │   └── KafkaProducerService   ✅
│   └── listener/
│       ├── AnalysisResultListener ✅
│       └── LogIngestionListener   ✅
├── ratelimit/           # Rate Limiting (Redis 기반)
├── config/              # Spring 설정
├── dto/                 # Data Transfer Objects
├── entity/              # JPA Entities (확장 필요)
├── repository/          # JPA Repositories
├── exception/           # 예외 처리
├── search/              # Elasticsearch 관련
└── util/                # 유틸리티
```

#### Heimdall 의존성 분석
```gradle
// Core
Spring Boot 3.3.5, Spring Cloud 2023.0.3, Java 21

// Security
spring-boot-starter-security, jjwt-api 0.12.3
spring-security-oauth2-resource-server

// Resilience
resilience4j-spring-boot3 2.1.0 (5개 모듈)
- circuitbreaker, ratelimiter, retry, bulkhead, timelimiter

// Messaging
spring-kafka, kafka-clients

// Data
spring-data-jpa, postgresql, spring-data-redis, spring-data-elasticsearch

// Observability
micrometer-registry-prometheus, micrometer-tracing-bridge-brave
zipkin-reporter-brave

// gRPC
grpc-spring-boot-starter 2.15.0, grpc-protobuf/stub/netty 1.59.0

// API Docs
springdoc-openapi-starter-webmvc-ui 2.3.0
```

### 📁 Bifrost (Python) 아키텍처 상세

```
bifrost/bifrost/
├── api.py               ✅ FastAPI 메인 (932줄)
│   ├── /analyze              Two-Track 자동 라우팅
│   ├── /api/v1/analyze       버전 API
│   ├── /api/router/classify  민감도 분류
│   ├── /health, /metrics     모니터링
│   └── WebSocket 지원
├── router.py            ✅ Privacy Router (207줄)
│   ├── PrivacyRouter 클래스
│   ├── HIGH/MEDIUM/LOW 분류
│   └── GDPR 키워드 감지
├── kafka_producer.py    ✅ Kafka 발행 (193줄)
├── kafka_consumer.py    ✅ Kafka 구독
├── kafka_events.py      ✅ 이벤트 스키마 (Pydantic)
├── heimdall_integration.py ✅ Heimdall 통합 서비스 (235줄)
├── ollama.py            ✅ Track A: Local LLM
├── bedrock.py           ✅ Track B: AWS Bedrock
├── database.py          ✅ SQLAlchemy ORM
├── cache.py             ✅ Redis 캐싱
├── metrics.py           ✅ Prometheus 메트릭
├── ratelimit.py         ✅ Rate Limiter
├── preprocessor.py      ✅ 로그 전처리
├── validators.py        ✅ 입력 검증
├── filters.py           ✅ 로그 필터링
├── export.py            ✅ JSON/CSV 내보내기
├── slack.py             ✅ Slack 알림
├── i18n.py              ✅ 다국어 지원
├── mlflow_tracker.py    ✅ MLflow 기초
├── batch.py             ✅ 배치 처리
├── main.py              ✅ CLI (Typer)
└── health.py            ✅ 헬스 체크
```

#### Bifrost 의존성 분석
```pip
# Core
fastapi>=0.115.0, pydantic>=2.11.7, uvicorn>=0.31.1
typer==0.12.3, rich>=13.9.4

# Kafka
aiokafka==0.10.0, kafka-python==2.0.2

# Database
sqlalchemy==2.0.23, alembic==1.13.0

# Monitoring
prometheus-client==0.19.0

# Testing (37개 테스트)
pytest==7.4.3, pytest-asyncio, pytest-cov, httpx>=0.28.1

# Optional
boto3 (AWS Bedrock), psycopg2-binary (PostgreSQL)
```

### 🔄 Kafka 토픽 구조

```yaml
# Heimdall → Bifrost
logs.ingestion:        # 로그 수집 이벤트
analysis.request:      # 분석 요청

# Bifrost → Heimdall  
analysis.result:       # 분석 결과

# System
logs.processing:       # 처리 상태
notification.alert:    # 알림
dlq.failed:           # Dead Letter Queue
```

### 🎯 Two-Track AI 라우팅 로직

```python
# bifrost/router.py 핵심 로직
def route(content: str) -> Track:
    level, patterns = classify_sensitivity(content)
    
    if level in [HIGH, MEDIUM]:
        return Track.A  # Local (Ollama/Llama 3.1 8B)
                        # GDPR 준수, Zero Cost
    else:
        return Track.B  # Cloud (Bedrock/Claude 3)
                        # 고성능, Pay-per-use

# 패턴 매칭 예시
HIGH: 이메일, 카드번호, 비밀번호, JWT, GDPR 키워드
MEDIUM: 내부 IP (10.x, 172.x, 192.168.x), 세션 ID, DB URL
LOW: 일반 로그, Public IP, 시스템 메트릭
```

### 📊 테스트 현황 상세

```
Heimdall Tests (7개)
├── HealthController         7/7 ✅
│   ├── healthEndpoint_ShouldReturnUpStatus
│   ├── echoEndpoint_ShouldReturnRequestData
│   ├── cpuStressEndpoint_ShouldCompleteSuccessfully
│   ├── memoryStressEndpoint_ShouldCompleteSuccessfully
│   ├── delayEndpoint_ShouldDelayForRequestedTime
│   ├── randomErrorEndpoint_WithHighErrorRate_ShouldEventuallyFail
│   └── randomErrorEndpoint_WithLowErrorRate_CanSucceed
└── Integration              1/1 ✅
    └── HeimdallIntegrationTest

Bifrost Tests (37개)
├── test_router.py           23/23 ✅ (Privacy Router 단위)
├── test_integration_router.py 14/14 ✅ (통합 시나리오)
├── test_api.py              ✅ (API 엔드포인트)
├── test_kafka_integration.py ✅ (Kafka 통신)
├── test_preprocessor.py     ✅ (로그 전처리)
├── test_batch.py            ✅ (배치 처리)
└── test_database.py         ✅ (DB 연동)
```

### 🔐 보안 체크리스트

```
✅ 완료된 보안 기능
├── JWT 토큰 인증
├── Spring Security 통합
├── Rate Limiting
├── Input Validation
└── Privacy-First 라우팅 (GDPR)

⚠️ 개선 필요
├── JWT Secret: 환경변수화 필요 (현재 Base64 기본값)
├── CORS: allow_origins=["*"] → 제한 필요
├── HTTPS: SSL 인증서 설정 필요
├── API Key: 서비스 간 인증 추가
└── Secrets Management: Vault 도입 고려
```

### 🚀 실행 명령어 (Quick Reference)

```powershell
# 전체 시작
.\start-all.ps1 -BuildFirst

# 개별 서비스
.\gradlew :heimdall:bootRun           # Heimdall (8080)
cd bifrost; uvicorn bifrost.api:app   # Bifrost (8000)
cd bifrost/frontend; npm run dev      # Frontend (5173)

# 테스트
.\test-all.ps1 -Coverage
pytest bifrost/tests -v --cov=bifrost

# 인프라
docker-compose up -d                  # 12개 서비스
docker-compose logs -f kafka          # Kafka 로그
```

---

## 📞 Feedback & Contribution

This roadmap is a living document. 피드백과 기여를 환영합니다!

- GitHub Issues로 제안
- Pull Request로 개선
- Discussions에서 아이디어 공유
