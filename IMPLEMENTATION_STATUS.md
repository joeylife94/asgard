# Implementation Status (Kafka Control Plane)

Date: 2026-01-06

이 문서는 현재까지 구현된 **Kafka 기반 분석 오케스트레이션(컨트롤 플레인)** 작업의 완료/미완료/특이사항을 정리합니다.

## 목표 (요약)
- Kafka를 컨트롤 플레인으로 사용
  - `analysis.request` → 작업 시작
  - `analysis.result` → 작업 완료
- Heimdall ↔ Bifrost REST 결합 제거(메인 실행 경로에서)
- Job 영속화 + idempotency + DLQ + 수동 redrive 제공
- Docker 기반 E2E 스모크로 “끝까지 돈다”를 증명

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
- 운영 수준 hardening 항목들(선택/권장)
  - DLQ redrive에 대한 권한/감사(누가 언제 재처리했는지) 강화
  - 메시지 스키마 버전 정책/호환성 가이드(문서화)
  - at-least-once에 따른 **중복 결과 수신** 케이스에 대한 추가 방어(필요 시 result idempotency 강화)
  - 메트릭/트레이싱(trace_id) 기반 대시보드 템플릿 정리
  - 실제 모델 기반 E2E(사전 모델 pull 포함) 옵션 추가

## 빠른 실행 (E2E)
PowerShell에서:
- `./scripts/e2e-smoke.ps1`

(필요 시) 수동으로 올리려면:
- `docker compose -f docker-compose.yml -f docker-compose.e2e.yml up --build`

---

원하시면, 이 문서에 **정확한 API 엔드포인트/샘플 요청/응답**까지 추가로 정리해 둘 수도 있어요.
