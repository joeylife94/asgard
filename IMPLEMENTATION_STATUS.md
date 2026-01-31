# Implementation Status (Kafka Control Plane)

Date: 2026-01-31 (Updated)

이 문서는 현재까지 구현된 **Kafka 기반 분석 오케스트레이션(컨트롤 플레인)** 작업의 완료/미완료/특이사항을 정리합니다.

## 목표 (요약)
- Kafka를 컨트롤 플레인으로 사용
  - `analysis.request` → 작업 시작
  - `analysis.result` → 작업 완료
- Heimdall ↔ Bifrost REST 결합 제거(메인 실행 경로에서)
- Job 영속화 + idempotency + DLQ + 수동 redrive 제공
- Docker 기반 E2E 스모크로 "끝까지 돈다"를 증명

## 완료된 것 (Done)
### 아키텍처/플로우
- **Heimdall이 Job을 발급/영속화**하고, 요청을 Kafka(`analysis.request`)로 발행
- **Bifrost는 Kafka 소비자**로 동작하며 `analysis.request`를 받아 처리
  - 처리 시 필요한 로그 입력은 Heimdall REST가 아니라 **Postgres(`log_entries`) 직접 조회**
- Bifrost는 결과를 Kafka(`analysis.result`)로 발행
- Heimdall은 `analysis.result`를 구독하여 **Job 상태를 완료/실패로 전이**

### 신뢰성(운영 기능)
- Job 영속화(analysis_jobs) + 상태 관리
- **Idempotency 기반 중복 요청 방지**(동일 key 재요청 시 기존 job 반환)
- 처리 실패 시 **DLQ 이벤트 발행** 및 실패 기록
- 운영 편의용 **수동 redrive(재처리) API** 제공

### E2E 검증(Compose)
- Docker Compose 기반으로 Kafka 루프가 **end-to-end로 SUCCEEDED**까지 도달하는 스모크가 동작
  - overlay: `docker-compose.e2e.yml`
  - smoke script: `scripts/e2e-smoke.ps1`

### ✅ 운영 수준 Hardening (2026-01-31 완료)

#### 1. DLQ Redrive 권한/감사 강화
- `RedriveAuditLog` 엔티티 추가 - 모든 redrive 작업 기록
- `RedriveAuditService` 서비스 구현
  - 성공/실패/스킵된 redrive 기록
  - 사용자별 redrive 이력 조회
  - Rate limiting 지원 (기본: 시간당 10회)
- API 엔드포인트 확장
  - `POST /api/v1/analysis/jobs/{jobId}/redrive` - reason 파라미터 지원
  - `GET /api/v1/analysis/jobs/{jobId}/redrive/audit` - 특정 Job의 감사 이력
  - `GET /api/v1/analysis/jobs/redrive/audit` - 전체 감사 로그 (관리자용)
- 감사 로그에 기록되는 정보: 수행자, 시간, IP, User-Agent, trace_id, 사유, 결과

#### 2. 메시지 스키마 버전 관리
- `docs/KAFKA_SCHEMA_VERSIONING.md` 문서 작성
  - 현재 스키마 정의 (AnalysisRequestEvent, AnalysisResultEvent, DlqFailedEvent)
  - 버전 번호 규칙 (Minor/Major 변경 기준)
  - Forward/Backward 호환성 가이드라인
  - 마이그레이션 절차 및 롤백 시나리오
  - 향후 Schema Registry 도입 고려사항

#### 3. 중복 결과 수신 방어 (Result Idempotency)
- `LogProcessingService.processAnalysisResult()` 강화
  - Job 상태 기반 중복 체크 (SUCCEEDED 상태면 스킵)
  - AnalysisResult 존재 여부 체크 (requestId 기반)
  - 중복 메트릭 카운터 추가: `ai_job_duplicate_result_total`
- 메트릭 태그로 중복 유형 구분: succeeded, failed, result_exists

#### 4. 메트릭/트레이싱 대시보드 템플릿
- `monitoring/grafana/dashboards/asgard-ai-jobs.json` 생성
- 대시보드 패널 구성:
  - **Overview**: Jobs Requested/Succeeded/Failed/Redriven, Success Rate, Duplicates
  - **Trends**: Job Processing Rate, Latency Distribution (p50/p95/p99)
  - **Kafka & DLQ**: Consumer Lag, Redrive/Duplicate Events
  - **Service Health**: Heimdall/Bifrost Status, Memory Usage, Request Rate

## 특이사항 / 운영 노트 (Notes)
### Kafka producer 압축(snappy) 이슈 대응
- 컨테이너 환경에서 **snappy native 라이브러리 부재**로 producer가 실패할 수 있어,
  - Heimdall Kafka producer compression을 **설정 가능하게 변경**했고 기본값을 `gzip`로 둠
  - (필요 시 `spring.kafka.producer.compression-type`로 변경 가능)

### Ollama 404(E2E 환경) fallback
- E2E에서 Ollama에 모델이 설치되어 있지 않으면 404가 발생할 수 있어,
  - **환경변수로 gated된 fallback**(결정적 텍스트 결과)을 추가해 스모크가 안정적으로 통과하도록 함
  - 운영/실서비스에서는 fallback을 끄고(또는 모델을 사전 pull) 사용하는 것을 권장

### 비차단(noise) 로그
- 일부 환경에서 Eureka 등 외부 의존(예: localhost:8761) 관련 connection refused 로그가 보일 수 있으나,
  - 현재 E2E의 핵심 플로우(Kafka+Postgres)에는 **치명적 영향 없음**

## 남은 것 (Remaining / TODO)
- ~~DLQ redrive에 대한 권한/감사(누가 언제 재처리했는지) 강화~~ ✅ 완료
- ~~메시지 스키마 버전 정책/호환성 가이드(문서화)~~ ✅ 완료
- ~~at-least-once에 따른 **중복 결과 수신** 케이스에 대한 추가 방어~~ ✅ 완료
- ~~메트릭/트레이싱(trace_id) 기반 대시보드 템플릿 정리~~ ✅ 완료
- 실제 모델 기반 E2E(사전 모델 pull 포함) 옵션 추가 (선택)

## 빠른 실행 (E2E)
PowerShell에서:
- `./scripts/e2e-smoke.ps1`

(필요 시) 수동으로 올리려면:
- `docker compose -f docker-compose.yml -f docker-compose.e2e.yml up --build`

## 새로 추가된 파일 (2026-01-31)
```
heimdall/src/main/java/com/heimdall/
├── entity/RedriveAuditLog.java          # 감사 로그 엔티티
├── repository/RedriveAuditLogRepository.java
├── service/RedriveAuditService.java     # 감사 서비스
├── dto/RedriveAuditLogResponse.java     # 응답 DTO
└── dto/RedriveRequest.java              # 요청 DTO

docs/
└── KAFKA_SCHEMA_VERSIONING.md           # 스키마 버전 관리 가이드

monitoring/grafana/dashboards/
└── asgard-ai-jobs.json                  # Grafana 대시보드 템플릿
```

---

## ✅ 확장 기능: Circuit Breaker 패턴 (Bifrost)

Date: 2026-01-31

### 개요
Bifrost의 LLM Provider 호출(On-Device RAG, Cloud Direct)에 **Circuit Breaker 패턴**을 적용하여 
운영 안정성을 크게 향상시켰습니다.

### 구현된 기능

#### 1. Circuit Breaker 모듈 (`bifrost/resilience/`)
- **CircuitBreaker 클래스**: Thread-safe 구현
  - 3가지 상태: `CLOSED` → `OPEN` → `HALF_OPEN`
  - 실패 임계값 도달 시 자동 OPEN (fail-fast)
  - 복구 타임아웃 후 HALF_OPEN으로 전환
  - 성공 임계값 도달 시 CLOSED로 복구
- **CircuitBreakerConfig**: 설정 프리셋 제공
  - `for_llm_provider()` - LLM 호출용 (failure=3, recovery=60s)
  - `for_external_api()` - 외부 API용 (failure=5, recovery=30s)
- **CircuitBreakerRegistry**: 싱글톤 레지스트리로 전역 관리
- **CircuitBreakerStats**: 통계/메트릭 수집

#### 2. OrchestratorService 통합
- 각 레인(on_device_rag, cloud_direct)별 독립적 Circuit Breaker
- 환경변수 기반 설정:
  - `BIFROST_CB_FAILURE_THRESHOLD` (기본: 3)
  - `BIFROST_CB_SUCCESS_THRESHOLD` (기본: 2)
  - `BIFROST_CB_RECOVERY_TIMEOUT` (기본: 60초)
- Circuit OPEN 시 즉시 fallback 응답 반환 (fail-fast)
- Exponential backoff 재시도 (0.5s → 1s → 2s → 4s)

#### 3. 모니터링 API 엔드포인트
- `GET /health` - Circuit Breaker 상태 포함
- `GET /api/v1/circuit-breakers` - 모든 CB 상태/통계 조회
- `GET /api/v1/circuit-breakers/{name}` - 특정 CB 상세 조회
- `POST /api/v1/circuit-breakers/{name}/reset` - 수동 리셋
- `POST /api/v1/circuit-breakers/reset-all` - 전체 리셋

#### 4. 테스트 커버리지 (28개 테스트 통과)
- 상태 전이 테스트 (CLOSED → OPEN → HALF_OPEN → CLOSED)
- 임계값 동작 검증
- Thread-safety 테스트 (동시성)
- Async 지원 테스트
- Decorator/Context Manager 패턴 테스트

### 새로 추가된 파일
```
bifrost/bifrost/resilience/
├── __init__.py                     # 모듈 export
└── circuit_breaker.py              # Circuit Breaker 구현

bifrost/tests/
└── test_circuit_breaker.py         # 테스트 코드 (28개)
```

### 수정된 파일
```
bifrost/bifrost/orchestrator/orchestrator_service.py  # CB 통합
bifrost/bifrost/api.py                                 # CB API 추가
```

---

원하시면, 이 문서에 **정확한 API 엔드포인트/샘플 요청/응답**까지 추가로 정리해 둘 수도 있어요.

---

## ✅ 확장 기능: 피드백 시스템 (Bifrost)

Date: 2026-01-31

### 개요
분석 결과에 대한 사용자 피드백을 수집하고 분석하여 AI 모델 개선에 활용할 수 있는 
**피드백 시스템**을 구현했습니다.

### 구현된 기능

#### 1. 피드백 모델 (`bifrost/feedback/models.py`)
- **Feedback 엔티티**: 피드백 데이터 저장
  - 분석 ID, 사용자 ID, 평점(1-5), 코멘트
  - 태그 (helpful, accurate, clear, wrong, incomplete 등)
  - 제공자/모델/레인 정보
  - 타임스탬프 (생성/수정)
- **FeedbackStats**: 통계 계산
  - 평균 평점, 총 개수, 태그별 분포
  - 평점 분포 (1-5점 각각)

#### 2. 피드백 저장소 (`bifrost/feedback/repository.py`)
- SQLite 기반 영속화
- CRUD 작업 지원
- 필터링 쿼리: 분석 ID, 사용자 ID, 최소 평점, 기간
- 통계 집계 쿼리

#### 3. 피드백 서비스 (`bifrost/feedback/service.py`)
- 피드백 생성/조회/수정/삭제
- 통계 분석 메서드
- 제공자/모델별 통계 집계

#### 4. API 엔드포인트
- `POST /api/v1/feedback` - 피드백 생성
- `GET /api/v1/feedback` - 피드백 목록 조회 (필터링)
- `GET /api/v1/feedback/{feedback_id}` - 특정 피드백 조회
- `PUT /api/v1/feedback/{feedback_id}` - 피드백 수정
- `DELETE /api/v1/feedback/{feedback_id}` - 피드백 삭제
- `GET /api/v1/feedback/stats` - 전체 통계
- `GET /api/v1/feedback/stats/{analysis_id}` - 분석별 통계

#### 5. 테스트 커버리지 (25개 테스트 통과)
- 모델 테스트 (Feedback, FeedbackStats)
- 저장소 CRUD 테스트
- 서비스 로직 테스트
- 통계 계산 테스트

### 새로 추가된 파일
```
bifrost/bifrost/feedback/
├── __init__.py
├── models.py
├── repository.py
└── service.py

bifrost/tests/
└── test_feedback.py (25개)
```

---

## ✅ 확장 기능: 멀티 LLM 동적 라우팅 (Bifrost)

Date: 2026-01-31

### 개요
복수의 LLM 제공자(Ollama, Bedrock 등)를 **지능적으로 라우팅**하는 시스템을 구현했습니다.
비용 최적화, 부하 분산, 성능 기반 라우팅 등 6가지 전략을 지원합니다.

### 구현된 기능

#### 1. 라우팅 모델 (`bifrost/routing/models.py`)
- **RoutingStrategy**: 6가지 전략 Enum
  - `ROUND_ROBIN` - 순차 분배
  - `COST_OPTIMIZED` - 비용 최적화
  - `PERFORMANCE` - 성능 기반
  - `CAPABILITY` - 기능 기반
  - `HYBRID` - 복합 전략
  - `FALLBACK` - 장애 대비 대체
- **ProviderConfig**: 제공자별 설정
  - 비용, 속도, 최대 토큰, 기능, 활성화 상태
- **RoutingDecision**: 라우팅 결정 결과
- **RoutingStats**: 라우팅 통계

#### 2. 비용 최적화기 (`bifrost/routing/cost_optimizer.py`)
- 토큰 기반 비용 계산
- 제공자별 비용 비교
- 예산 제한 라우팅
- 비용 추정 API

#### 3. 부하 분산기 (`bifrost/routing/load_balancer.py`)
- Round-Robin 분배
- Weighted Random 분배
- 최저 부하 기반 분배
- 건강 상태 기반 필터링

#### 4. 라우터 (`bifrost/routing/router.py`)
- **LLMRouter**: 통합 라우터 클래스
  - 전략 기반 라우팅 결정
  - 제공자 건강 상태 관리
  - 장애 감지 및 fallback
  - 통계 수집/분석
- 제공자 기본 설정 프리셋

#### 5. API 엔드포인트
- `GET /api/v1/routing/providers` - 제공자 목록
- `POST /api/v1/routing/route` - 라우팅 결정 요청
- `GET /api/v1/routing/stats` - 라우팅 통계
- `POST /api/v1/routing/providers/{name}/health` - 건강 상태 업데이트
- `PUT /api/v1/routing/strategy` - 전략 변경

#### 6. 테스트 커버리지 (30개 테스트 통과)
- 모델 테스트
- 비용 최적화기 테스트
- 부하 분산기 테스트
- 라우터 통합 테스트
- 전략별 동작 테스트

### 새로 추가된 파일
```
bifrost/bifrost/routing/
├── __init__.py
├── models.py
├── cost_optimizer.py
├── load_balancer.py
└── router.py

bifrost/tests/
└── test_routing.py (30개)
```

---

## ✅ 확장 기능: 분석 품질 지표 시스템 (Bifrost)

Date: 2026-01-31

### 개요
AI 분석 결과의 품질을 **다차원으로 측정하고 추적**하는 시스템을 구현했습니다.
10가지 품질 차원을 분석하여 종합 점수를 산출합니다.

### 구현된 기능

#### 1. 품질 모델 (`bifrost/quality/models.py`)
- **QualityDimension**: 10가지 품질 차원 Enum
  - `RELEVANCE` - 관련성
  - `COMPLETENESS` - 완전성
  - `ACCURACY` - 정확성
  - `CLARITY` - 명확성
  - `SPECIFICITY` - 구체성
  - `ACTIONABILITY` - 실행가능성
  - `CONSISTENCY` - 일관성
  - `DEPTH` - 깊이
  - `TECHNICAL_ACCURACY` - 기술적 정확성
  - `RESPONSE_TIME` - 응답 시간
- **QualityScore**: 차원별 점수 (0.0-1.0)
- **AnalysisQualityReport**: 종합 품질 보고서
- **QualityThresholds**: 품질 기준점

#### 2. 품질 분석기 (`bifrost/quality/analyzer.py`)
- **QualityAnalyzer 클래스**
  - `analyze(question, answer)` - 종합 품질 분석
  - 차원별 개별 분석 메서드
  - 가중치 기반 종합 점수 계산
  - 개선 제안 생성 기능

#### 3. 품질 추적기 (`bifrost/quality/tracker.py`)
- SQLite 기반 품질 보고서 저장
- 분석별/기간별 품질 추적
- 트렌드 분석
- 통계 집계

#### 4. API 엔드포인트
- `POST /api/v1/quality/analyze` - 품질 분석 수행
- `GET /api/v1/quality/reports` - 품질 보고서 목록
- `GET /api/v1/quality/reports/{analysis_id}` - 특정 분석 보고서
- `GET /api/v1/quality/stats` - 품질 통계
- `GET /api/v1/quality/trends` - 품질 트렌드

#### 5. 테스트 커버리지 (31개 테스트 통과)
- 모델 테스트
- 분석기 개별 차원 테스트
- 종합 분석 테스트
- 추적기 저장/조회 테스트
- 통계 계산 테스트

### 새로 추가된 파일
```
bifrost/bifrost/quality/
├── __init__.py
├── models.py
├── analyzer.py
└── tracker.py

bifrost/tests/
└── test_quality.py (31개)
```

---

## ✅ 확장 기능: A/B 테스팅 프레임워크 (Bifrost)

Date: 2026-01-31

### 개요
LLM 제공자, 프롬프트, 파라미터 등을 **과학적으로 비교 테스트**할 수 있는 
A/B 테스팅 프레임워크를 구현했습니다.

### 구현된 기능

#### 1. 실험 모델 (`bifrost/experiment/models.py`)
- **Experiment**: 실험 정의
  - 이름, 설명, 상태
  - 변형(Variant) 목록
  - 트래픽 분배 설정
  - 시작/종료 시간
- **Variant**: 실험 변형
  - `CONTROL` - 대조군 (현재 설정)
  - `TREATMENT` - 실험군 (새 설정)
  - 설정 값 (JSON)
- **ExperimentStatus**: 상태 관리
  - `DRAFT` → `RUNNING` → `PAUSED` → `COMPLETED`
- **VariantMetrics**: 변형별 메트릭
  - 샘플 수, 성공률, 평균 응답시간, 평균 품질
- **StatisticalResult**: 통계적 분석 결과
  - 통계적 유의성, p-value, 신뢰구간
  - 권장 결론

#### 2. 실험 관리자 (`bifrost/experiment/manager.py`)
- **ExperimentManager 클래스**
  - 실험 생성/조회/수정/삭제
  - 실험 시작/일시정지/종료
  - 변형 할당 (`assign_variant`)
  - 결과 기록 (`record_result`)
  - 통계 분석 (`get_results`)
- SQLite 기반 영속화
- 트래픽 분배 알고리즘

#### 3. API 엔드포인트
- `POST /api/v1/experiments` - 실험 생성
- `GET /api/v1/experiments` - 실험 목록
- `GET /api/v1/experiments/{experiment_id}` - 특정 실험 조회
- `PUT /api/v1/experiments/{experiment_id}` - 실험 수정
- `DELETE /api/v1/experiments/{experiment_id}` - 실험 삭제
- `POST /api/v1/experiments/{experiment_id}/start` - 실험 시작
- `POST /api/v1/experiments/{experiment_id}/pause` - 실험 일시정지
- `POST /api/v1/experiments/{experiment_id}/stop` - 실험 종료
- `POST /api/v1/experiments/{experiment_id}/assign` - 변형 할당
- `POST /api/v1/experiments/{experiment_id}/record` - 결과 기록
- `GET /api/v1/experiments/{experiment_id}/results` - 결과 분석

#### 4. 테스트 커버리지 (34개 테스트 통과)
- 모델 테스트
- 실험 생명주기 테스트
- 변형 할당 테스트
- 결과 기록 테스트
- 통계 분석 테스트

### 새로 추가된 파일
```
bifrost/bifrost/experiment/
├── __init__.py
├── models.py
└── manager.py

bifrost/tests/
└── test_experiment.py (34개)
```

---

## ✅ 확장 기능: 스마트 캐싱 시스템 (Bifrost)

Date: 2026-01-31

### 개요
LLM 응답을 **의미적 유사성 기반으로 캐싱**하여 비용을 절감하고 응답 시간을 단축하는
스마트 캐싱 시스템을 구현했습니다.

### 구현된 기능

#### 1. 캐시 모델 (`bifrost/smart_cache/models.py`)
- **CacheEntry**: 캐시 항목
  - 쿼리, 해시, 응답
  - 제공자/모델/레인 정보
  - TTL 및 만료 시간
  - 히트 카운트
  - 압축 지원
  - 품질 점수
- **CacheConfig**: 캐시 설정
  - 최대 항목 수/크기
  - TTL 설정 (기본/최소/최대)
  - 유사도 임계값
  - 제거 전략
  - 캐시 정책
- **CacheStats**: 캐시 통계
  - 총 요청, 히트, 미스
  - 정확 히트 vs 시맨틱 히트
  - 히트율 계산
- **EvictionStrategy**: 제거 전략
  - `LRU` - Least Recently Used
  - `LFU` - Least Frequently Used
  - `FIFO` - First In First Out
  - `TTL` - 시간 기반
  - `SEMANTIC` - 다양성 유지
- **CachePolicy**: 캐시 정책
  - `EXACT` - 정확한 매치만
  - `SEMANTIC` - 의미적 유사성
  - `HYBRID` - 정확 우선, 시맨틱 fallback

#### 2. 시맨틱 매처 (`bifrost/smart_cache/semantic.py`)
- **SemanticMatcher 클래스**
  - 쿼리 정규화
  - 키워드 추출
  - N-gram 기반 유사도 계산
  - Jaccard 유사도
  - 최적 매치 탐색
  - 배치 유사도 계산

#### 3. 캐시 매니저 (`bifrost/smart_cache/cache_manager.py`)
- **SmartCacheManager 클래스** (싱글톤)
  - `get(query)` - 캐시 조회 (정확 → 시맨틱)
  - `put(query, response)` - 캐시 저장 (압축 지원)
  - `invalidate(query)` - 캐시 무효화
  - `clear()` - 전체 삭제
  - `cleanup_expired()` - 만료 항목 정리
  - `get_stats()` - 통계 조회
- SQLite 기반 영속화
- Thread-safe 구현
- 자동 제거 (eviction)

#### 4. API 엔드포인트
- `POST /api/v1/cache/put` - 캐시에 저장
- `POST /api/v1/cache/lookup` - 캐시 조회
- `GET /api/v1/cache/stats` - 캐시 통계
- `GET /api/v1/cache/entries` - 캐시 항목 목록
- `DELETE /api/v1/cache/invalidate` - 캐시 무효화
- `DELETE /api/v1/cache/clear` - 전체 삭제
- `POST /api/v1/cache/cleanup` - 만료 항목 정리

#### 5. 테스트 커버리지 (29개 테스트 통과)
- CacheEntry 모델 테스트
- CacheConfig 설정 테스트
- CacheStats 통계 테스트
- SemanticMatcher 테스트
- SmartCacheManager 통합 테스트
- TTL/제거/압축 테스트

### 새로 추가된 파일
```
bifrost/bifrost/smart_cache/
├── __init__.py
├── models.py
├── semantic.py
└── cache_manager.py

bifrost/tests/
└── test_smart_cache.py (29개)
```

---

## 📊 전체 테스트 현황 (Bifrost)

| 모듈 | 테스트 수 | 상태 |
|------|----------|------|
| Circuit Breaker | 28 | ✅ PASSED |
| Feedback System | 25 | ✅ PASSED |
| Multi-LLM Routing | 30 | ✅ PASSED |
| Quality Metrics | 31 | ✅ PASSED |
| A/B Testing | 34 | ✅ PASSED |
| Smart Caching | 29 | ✅ PASSED |
| **Total** | **177** | ✅ **ALL PASSED** |

---

## 🏗️ 프로젝트 아키텍처 요약

```
┌─────────────────────────────────────────────────────────────────┐
│                        Asgard Platform                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐       Kafka        ┌─────────────────┐    │
│  │    Heimdall     │◄──────────────────►│     Bifrost     │    │
│  │  (Java/Spring)  │                    │   (Python/FA)   │    │
│  │                 │                    │                 │    │
│  │ - Job 관리      │  analysis.request  │ - LLM 분석      │    │
│  │ - Redrive 감사  │  ──────────────►   │ - Circuit Break │    │
│  │ - 결과 Idemp.   │  analysis.result   │ - 피드백 수집   │    │
│  │                 │  ◄──────────────   │ - 품질 분석     │    │
│  └────────┬────────┘                    │ - A/B 테스팅    │    │
│           │                             │ - 스마트 캐싱   │    │
│           │                             │ - 멀티 LLM 라우팅│    │
│           ▼                             └────────┬────────┘    │
│  ┌─────────────────┐                             │             │
│  │   PostgreSQL    │                             ▼             │
│  │  - log_entries  │                    ┌─────────────────┐    │
│  │  - analysis_jobs│                    │  Ollama/Bedrock │    │
│  │  - redrive_audit│                    │   (LLM 제공자)  │    │
│  └─────────────────┘                    └─────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

