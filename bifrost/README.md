# 🌈 Bifrost

> **The Rainbow Bridge for MLOps** - AI-powered log analysis platform with MSA integration

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎉 Verified Working - MSA Integration

- ✅ **Tested on:** 2024-11-17
- ✅ **Full MSA Stack:** Working with Heimdall via Kafka
- ✅ **E2E Tests:** Available in `../tests/e2e/`
- ✅ **Docker Compose:** `../docker-compose.msa.yml` ready
- ✅ **Quick Start:** See [MSA_QUICKSTART.md](../MSA_QUICKSTART.md)



**Bifrost**는 MLOps 환경의 로그를 AI로 자동 분석하는 프로덕션급 플랫폼입니다.  **Bifrost**는 MLOps 환경의 로그를 AI로 자동 분석하는 프로덕션급 플랫폼입니다.  

Kubernetes, CI/CD 파이프라인, 마이크로서비스 로그를 AI로 빠르게 분석하고 인사이트를 얻으세요.Kubernetes, CI/CD 파이프라인, 마이크로서비스 로그를 AI로 빠르게 분석하고 인사이트를 얻으세요.



------



## 🎯 What's New in v0.3## 🎯 What's New in v0.3



### 🚀 **MSA Integration** - Heimdall과 함께하는 이벤트 기반 아키텍처### 🚀 **MSA Integration** - Heimdall과 함께하는 이벤트 기반 아키텍처



Bifrost가 **Heimdall (Java/Spring Boot)** 과 **Apache Kafka**를 통해 마이크로서비스로 통합됩니다!Bifrost가 **Heimdall (Java/Spring Boot)** 과 **Apache Kafka**를 통해 마이크로서비스로 통합됩니다!



``````

┌──────────────┐      Kafka Event      ┌──────────────┐┌──────────────┐      Kafka Event      ┌──────────────┐

│   Heimdall   │────────────────────►│   Bifrost    ││   Heimdall   │────────────────────►│   Bifrost    │

│ (Log Store)  │◄────────────────────│  (AI Engine) ││ (Log Store)  │◄────────────────────│  (AI Engine) │

└──────────────┘   analysis.request   └──────────────┘└──────────────┘   analysis.request   └──────────────┘

                   analysis.result                   analysis.result

``````



**주요 기능:****주요 기능:**

- ✅ **비동기 이벤트 처리**: Kafka를 통한 고성능 메시지 큐잉- ✅ **비동기 이벤트 처리**: Kafka를 통한 고성능 메시지 큐잉

- ✅ **독립적 확장성**: Bifrost와 Heimdall을 개별적으로 스케일 가능- ✅ **독립적 확장성**: Bifrost와 Heimdall을 개별적으로 스케일 가능

- ✅ **DLQ (Dead Letter Queue)**: 실패한 메시지 자동 격리 및 재처리- ✅ **DLQ (Dead Letter Queue)**: 실패한 메시지 자동 격리 및 재처리

- ✅ **헬스 체크**: Kafka 연결 상태 및 Consumer/Producer 상태 모니터링- ✅ **헬스 체크**: Kafka 연결 상태 및 Consumer/Producer 상태 모니터링

- ✅ **유연한 AI 소스**: Ollama (로컬) 또는 Bedrock (클라우드) 선택 가능- ✅ **유연한 AI 소스**: Ollama (로컬) 또는 Bedrock (클라우드) 선택 가능



➡️ **[MSA Integration Guide](MSA_INTEGRATION_GUIDE.md)** - 전체 가이드 보기➡️ **[MSA Integration Guide](MSA_INTEGRATION_GUIDE.md)** - 전체 가이드 보기



------



## ✨ Features

---

## Interview Edition: Incident/Runbook Q&A (Plan A)

이 섹션은 **면접 데모용**으로, "런북/운영 문서 기반 Q&A" 워크플로우를 **프로덕션스럽게(오케스트레이션/폴백/관측성 포함)** 보여주기 위한 기능입니다.

### 아키텍처 개요 (Lane 분리)

```text
          ┌──────────────────────────────┐
          │   FastAPI (/api/v1/ask)      │
          │     (alias: /ask)            │
          │  - endpoint는 provider 호출 X │
          └─────────────┬────────────────┘
                        │
                        ▼
          ┌──────────────────────────────┐
          │     OrchestratorService      │
          │  PolicyRouter + timeout/retry│
          └─────────────┬────────────────┘
                        │
        ┌───────────────┴────────────────┐
        │                                │
        ▼                                ▼
┌───────────────────────┐      ┌────────────────────────┐
│ On-device lane (RAG)   │      │ Cloud lane (Direct)     │
│ - ingest/retrieve/prompt│      │ - RAG 사용 금지         │
│ - SQLite/Postgres 저장  │      │ - ENABLE_CLOUD_LANE 필요│
└───────────┬───────────┘      └─────────────┬──────────┘
            │                                  │
            ▼                                  ▼
     OllamaProvider (local)             BedrockProvider (cloud)
```

### 엔드포인트

- `POST /api/v1/runbooks/ingest`
  - request: `{ "source": "...", "tags": ["..."], "text": "..." }`
  - response: `{ "chunks_ingested": 12 }`

- `POST /api/v1/ask` (권장)
  - `POST /ask` (호환용 alias)
  - request: `AnswerRequest` (`question`, `tags?`, `source?`, `session_id?`)
  - response: `AnswerResponse` (`answer`, `citations`, `route`, `telemetry`)

### Routing Policy (명시)

- 기본 lane: `on_device_rag`
- cloud lane 사용 조건:
  - `ENABLE_CLOUD_LANE=true` 설정
  - 그리고 요청에서 `source`를 `cloud` 또는 `cloud_direct`로 지정
- cloud lane은 **Direct-only**이며 RAG 저장소/리트리버/컨텍스트 빌더를 사용하지 않습니다.

### Low-Confidence & Fallback Policy (명시)

아래 조건 중 하나라도 만족하면 **결정론적(deterministic) fallback**을 수행합니다.

- 답변이 비어있거나 너무 짧음 (길이 < 60 chars)
- 불확실성 표현 포함 (EN: "i don't know", "not sure" ... / KR: "모르", "확신", "알 수 없", "불확실" 등)
- `on_device_rag` lane에서 citations가 비어있음 (런북 근거로 grounding 실패)

fallback 응답은 단순 에러가 아니라:
- 영어 1문장 + 한국어 설명
- 상위 런북 스니펫 목록
- citations
을 포함합니다.

### Observability (명시)

- 구조화 로그: `request_id`, `lane`, `provider`, `retrieved_chunk_ids`, `latency_ms`, `outcome`, `fallback_used`
- Prometheus metrics (GET `/metrics`):
  - `bifrost_ask_requests_total`
  - `bifrost_ask_latency_ms`

### 로컬 실행(최소)

```powershell
cd bifrost
pip install -r requirements.txt

# Ollama 없이 데모하려면(선택)
$env:BIFROST_ON_DEVICE_MODE = "stub"

uvicorn bifrost.api:app --host 0.0.0.0 --port 8000
```

### 빠른 데모

1) 런북 ingest (PowerShell 추천)

```powershell
$txt = Get-Content -Raw "examples/runbooks/runbook-postgres-connection-refused.md"
$body = @{ source = "examples/runbooks/runbook-postgres-connection-refused.md"; tags = @("postgres","incident"); text = $txt } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/runbooks/ingest" -ContentType "application/json" -Body $body
```

(curl 사용 시에는 `text`에 문서 내용을 그대로 넣어 전송하세요.)

2) 질문(/ask)

```bash
curl -s -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -H "x-request-id: demo-001" \
  -d '{"question": "postgres connection refused가 났을 때 5분 내에 무엇부터 확인해?"}'
```

### 데모용 예시 질문 3개

- "postgres connection refused가 났을 때 5분 내에 무엇부터 확인해?"
- "Kafka consumer lag이 급증할 때 가장 먼저 볼 지표/원인 후보는?"
- "리밸런싱이 잦을 때 consumer 설정 중 어떤 걸 점검해야 해?"

### 환경변수

- `BIFROST_DATABASE_URL` 또는 `DATABASE_URL`: RAG chunk 저장 DB (기본: `sqlite:///bifrost.db`)
- `ENABLE_CLOUD_LANE=true`: cloud lane 허용(기본 비활성)
- `BIFROST_ON_DEVICE_MODE=stub`: Ollama 없이도 데모 가능한 스텁 모드
- `BIFROST_ON_DEVICE_STUB_ANSWER`: 스텁 답변 문구

### Configuration Knobs (ENV)

| ENV | Default | Purpose |
| --- | --- | --- |
| `BIFROST_RAG_TOP_K` | `5` | on-device RAG retrieval top-k |
| `BIFROST_RAG_MAX_CONTEXT_CHARS` | `6500` | on-device RAG prompt max char budget |
| `BIFROST_LLM_TIMEOUT_SECONDS` | `12` | orchestrator LLM timeout (seconds) |
| `BIFROST_LLM_MAX_RETRIES` | `1` | orchestrator retry count (`0`이면 retry 없음) |
| `ENABLE_CLOUD_LANE` | `false` | cloud lane 사용 허용 여부 |
| `BIFROST_CLOUD_PROVIDER` | `bedrock` | cloud lane provider 이름 |
| `BIFROST_ON_DEVICE_PROVIDER` | `ollama` | on-device provider 이름 |




### 🚀 Core Capabilities## ✨ Features[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)



- ✅ **Hybrid LLM**: Ollama (로컬) + AWS Bedrock (클라우드)

- ✅ **배치 처리**: 수백 개 로그 파일 동시 분석 (비동기)

- ✅ **스트리밍**: 실시간 분석 결과 (WebSocket)### 🚀 Core## ✨ Features

- ✅ **캐싱**: SHA256 해시 기반 중복 분석 방지

- ✅ **CLI & REST API & Kafka**: 3가지 사용 방식 지원- ✅ **Hybrid LLM**: Ollama (로컬) + AWS Bedrock (클라우드)



### 🏛️ MSA Integration (NEW v0.3)- ✅ **배치 처리**: 수백 개 로그 파일 동시 분석 (비동기)**Bifrost**는 MLOps 환경의 로그를 AI로 자동 분석하는 프로덕션급 플랫폼입니다.  



- ✅ **Event-Driven Architecture**: Apache Kafka 기반 비동기 통신- ✅ **스트리밍**: 실시간 분석 결과 (WebSocket)

- ✅ **Heimdall Integration**: Java/Spring Boot 로그 저장소와 연동

- ✅ **DLQ Support**: 실패한 메시지 자동 격리 및 재시도- ✅ **캐싱**: SHA256 해시 기반 중복 분석 방지Kubernetes, CI/CD 파이프라인, 마이크로서비스 로그를 AI로 빠르게 분석하고 인사이트를 얻으세요.- 🏠 **로컬 모드**: Ollama를 사용한 프라이버시 우선 분석

- ✅ **Health Checks**: Kafka 상태 모니터링 엔드포인트

- ✅ **Flexible AI Source**: Ollama (로컬) 또는 Bedrock (클라우드) 선택



### 🎨 Web & Integration Features### 🎨 New Features (v0.2.1)- ☁️ **클라우드 모드**: AWS Bedrock (Claude 3) 프로덕션 스케일



- ✅ **Web UI**: Modern htmx-based interface with gradient design- ✅ **Web UI**: Modern htmx-based interface with gradient design

- ✅ **Slack Integration**: Send analysis results to Slack channels

- ✅ **CSV/JSON Export**: Export analysis history in multiple formats- ✅ **Slack Integration**: Send analysis results to Slack channels---- � **스트리밍 출력**: 실시간 응답 확인

- ✅ **Log Filtering**: Filter by severity (ERROR/WARN/INFO), keywords, time range

- ✅ **Real-time Statistics**: Log line counts by severity level- ✅ **CSV/JSON Export**: Export analysis history in multiple formats



### 🔒 프로덕션 보안- ✅ **Log Filtering**: Filter by severity (ERROR/WARN/INFO), keywords, time range- ⚙️ **유연한 설정**: YAML 설정 파일 + 환경변수 지원



- ✅ **API 키 인증**: 안전한 API 액세스- ✅ **Real-time Statistics**: Log line counts by severity level

- ✅ **Rate Limiting**: 시간당 요청 제한 (토큰 버킷)

- ✅ **입력 검증**: 크기 제한, XSS 방지, 형식 검증## ✨ Features- 🎨 **다양한 포맷**: Markdown, JSON, Plain text 출력

- ✅ **에러 핸들링**: 계층화된 예외 처리

### 🔒 프로덕션 보안

### 📊 관찰성

- ✅ **API 키 인증**: 안전한 API 액세스- 🔧 **로그 전처리**: 크기 제한, 타임스탬프 제거, 자동 정리

- ✅ **Prometheus 메트릭**: 7가지 커스텀 메트릭

- ✅ **구조화된 로깅**: JSON 로그 (Elasticsearch 연동 가능)- ✅ **Rate Limiting**: 시간당 요청 제한 (토큰 버킷)

- ✅ **헬스 체크**: Kubernetes liveness/readiness probes

- ✅ **Grafana 대시보드**: 실시간 모니터링- ✅ **입력 검증**: 크기 제한, XSS 방지, 형식 검증### 🚀 Core- 🔁 **재시도 로직**: 네트워크 불안정 대응



### 🛠️ DevOps- ✅ **에러 핸들링**: 계층화된 예외 처리



- ✅ **Docker**: 멀티 스테이지 빌드 (최적화)- ✅ **CLI & REST API**: 터미널과 프로그래밍 방식 모두 지원

- ✅ **Kubernetes**: HPA, ConfigMap, Secret

- ✅ **CI/CD**: GitHub Actions (테스트, 빌드, 배포)### 📊 관찰성

- ✅ **Makefile**: 원라인 개발 명령어

- ✅ **Prometheus 메트릭**: 7가지 커스텀 메트릭- ✅ **Hybrid LLM**: Ollama (로컬) + AWS Bedrock (클라우드)## �🚀 Quick Start

---

- ✅ **구조화된 로깅**: JSON 로그 (Elasticsearch 연동 가능)

## 🚀 Quick Start

- ✅ **헬스 체크**: Kubernetes liveness/readiness probes- ✅ **배치 처리**: 수백 개 로그 파일 동시 분석 (비동기)

### Option 1: MSA Mode (Heimdall Integration)

- ✅ **Grafana 대시보드**: 실시간 모니터링

Heimdall과 함께 사용할 때 - [상세 가이드](MSA_INTEGRATION_GUIDE.md)

- ✅ **스트리밍**: 실시간 분석 결과 (WebSocket)### 1. 설치

```bash

# 1. Docker Compose로 전체 스택 시작 (Kafka 포함)### 🛠️ DevOps

docker-compose up -d

- ✅ **Docker**: 멀티 스테이지 빌드 (최적화)- ✅ **캐싱**: SHA256 해시 기반 중복 분석 방지

# 2. bifrost.yaml 설정

cp bifrost.yaml.example bifrost.yaml- ✅ **Kubernetes**: HPA, ConfigMap, Secret



# kafka.enabled=true, heimdall.enabled=true로 변경- ✅ **CI/CD**: GitHub Actions (테스트, 빌드, 배포)```bash



# 3. 서비스 확인- ✅ **Makefile**: 원라인 개발 명령어

curl http://localhost:8000/api/v1/heimdall/status

### 🔒 프로덕션 보안pip install -e .

# 4. Kafka UI에서 메시지 확인

open http://localhost:8090---

```

- ✅ **API 키 인증**: 안전한 API 액세스

**포함된 서비스:**

- Bifrost API (port 8000)## 🚀 Quick Start

- PostgreSQL (port 5432)

- Redis (port 6379)- ✅ **Rate Limiting**: 시간당 요청 제한 (토큰 버킷)# AWS Bedrock 사용 시 (선택)

- **Kafka (port 9092, 9093)** ⭐ NEW

- **Zookeeper (port 2181)** ⭐ NEW### 1. 설치

- **Kafka UI (port 8090)** ⭐ NEW

- Ollama (port 11434)```bash- ✅ **입력 검증**: 크기 제한, XSS 방지, 형식 검증pip install boto3

- Prometheus (port 9090)

- Grafana (port 3000)pip install -e .



---- ✅ **에러 핸들링**: 계층화된 예외 처리```



### Option 2: Standalone CLI Mode# AWS Bedrock 사용 시 (선택)



Bifrost만 독립적으로 사용할 때pip install boto3



```bash```

# 1. 설치

pip install -e .### 📊 관찰성### 2. Ollama 준비 (로컬 모드)



# AWS Bedrock 사용 시 (선택)### 2. Ollama 준비 (로컬 모드)

pip install boto3

```bash- ✅ **Prometheus 메트릭**: 7가지 커스텀 메트릭

# 2. Ollama 준비 (로컬 모드)

ollama pull mistral# Ollama 설치 (https://ollama.ai)

ollama serve

ollama pull mistral- ✅ **구조화된 로깅**: JSON 로그 (Elasticsearch 연동 가능)```bash

# 3. CLI 사용

bifrost local error.logollama serve

bifrost local --stream app.log

```- ✅ **헬스 체크**: Kubernetes liveness/readiness probes# Ollama 설치 (https://ollama.ai)

# 클라우드 모드 (AWS Bedrock)

bifrost cloud error.log

bifrost cloud --region us-west-2 app.log

### 3. Web UI 사용 (가장 빠른 방법 🎨)- ✅ **Grafana 대시보드**: 실시간 모니터링ollama pull mistral

# 파이프 입력

kubectl logs my-pod | bifrost local```bash

docker logs my-container | bifrost cloud

# API 서버 실행ollama serve

# 로그 필터링 ✨ NEW

bifrost filter-log app.log --severity ERRORuvicorn bifrost.api:app --reload

bifrost filter-log app.log --errors-only --output errors.log

### 🛠️ DevOps```

# 결과 Export ✨ NEW

bifrost export --format csv --limit 100# 브라우저에서 http://localhost:8000 접속

bifrost export --format json --output results.json

# 로그 붙여넣기 → 분석 클릭!- ✅ **Docker**: 멀티 스테이지 빌드 (최적화)

# Slack 알림 ✨ NEW

bifrost slack --webhook-url https://hooks.slack.com/... --file app.log```

```

- ✅ **Kubernetes**: HPA, ConfigMap, Secret### 3. 사용

---

### 4. CLI 사용

### Option 3: Web UI Mode

```bash- ✅ **CI/CD**: GitHub Actions (테스트, 빌드, 배포)

```bash

# API 서버 실행# 로컬 모드 (Ollama)

uvicorn bifrost.api:app --reload

bifrost local error.log- ✅ **Makefile**: 원라인 개발 명령어```bash

# 브라우저에서 http://localhost:8000 접속

# 로그 붙여넣기 → 분석 클릭!bifrost local --stream app.log

```

# 로컬 모드 (Ollama)

---

# 클라우드 모드 (AWS Bedrock)

## 🎯 Use Cases

bifrost cloud error.log---bifrost local error.log

### 1. Kubernetes 로그 분석

bifrost cloud --region us-west-2 app.log

```bash

kubectl logs my-pod | bifrost localbifrost local --stream app.log

```

# 파이프 입력

### 2. CI/CD 실패 원인 파악

kubectl logs my-pod | bifrost local## 🎯 Use Cases

```bash

# GitHub Actions 로그 다운로드docker logs my-container | bifrost cloud

gh run view 123456 --log > ci.log

# 클라우드 모드 (AWS Bedrock)

# Bifrost로 분석

bifrost local ci.log# 로그 필터링 ✨ NEW

```

bifrost filter-log app.log --severity ERROR### 1. Kubernetes 로그 분석bifrost cloud error.log

### 3. 배치 분석

bifrost filter-log app.log --errors-only --output errors.log

```bash

# 여러 서비스 로그 동시 분석```bashbifrost cloud --region us-west-2 app.log

bifrost batch service1.log service2.log service3.log --concurrent 10

# 결과 Export ✨ NEW

# logs/ 디렉토리의 모든 로그 분석

bifrost batch logs/*.logbifrost export --format csv --limit 100kubectl logs my-pod | bifrost local

```

bifrost export --format json --output results.json

### 4. MSA 환경에서 Heimdall과 연동

```# 파이프 입력

```bash

# Heimdall이 로그 수집 시 자동으로 Kafka로 analysis.request 전송# Slack 알림 ✨ NEW

# Bifrost가 자동으로 분석 후 analysis.result 전송

# Heimdall에서 분석 결과 조회 가능bifrost slack --webhook-url https://hooks.slack.com/... --file app.logkubectl logs my-pod | bifrost local



# Kafka UI에서 실시간 메시지 확인bifrost slack --webhook-url https://hooks.slack.com/... --message "Deploy failed"

open http://localhost:8090

``````### 2. CI/CD 실패 원인 파악docker logs my-container | bifrost cloud



---



## 🏗️ Architecture---```bash



### Standalone Mode



```## 🎯 Use Cases# GitHub Actions 로그 다운로드# 출력 포맷 변경

┌─────────────────────────────────────────────────────────┐

│                   Client Layer                          │

│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │

│  │   CLI    │  │  WebUI   │  │  API     │             │### 1. Kubernetes 로그 분석gh run view 123456 --log > ci.logbifrost local --format json app.log

│  └──────────┘  └──────────┘  └──────────┘             │

└─────────────────────────────────────────────────────────┘```bash

                        ↓

┌─────────────────────────────────────────────────────────┐kubectl logs my-pod | bifrost localbifrost local --format plain error.log > analysis.txt

│              Presentation (FastAPI)                     │

│  - Rate Limiting, Auth, Validation                      │```

└─────────────────────────────────────────────────────────┘

                        ↓# Bifrost로 분석

┌─────────────────────────────────────────────────────────┐

│            Business Logic                               │### 2. CI/CD 실패 원인 파악

│  - Preprocessor, Analyzer, Formatter                    │

└─────────────────────────────────────────────────────────┘```bashbifrost local ci.log# 설정 파일 생성

                        ↓

┌─────────────────────────────────────────────────────────┐# GitHub Actions

│           Integration (LLM, DB)                         │

│  - Ollama Client, Bedrock Client, Database              │curl -H "Authorization: token $GITHUB_TOKEN" \```bifrost config --init

└─────────────────────────────────────────────────────────┘

                        ↓  https://api.github.com/repos/user/repo/actions/runs/123/logs | \

┌─────────────────────────────────────────────────────────┐

│         Infrastructure                                  │  bifrost cloudbifrost config --show

│  - PostgreSQL, Redis, Prometheus                        │

└─────────────────────────────────────────────────────────┘```

```

### 3. 배치 분석```

### MSA Mode (with Heimdall)

### 3. 마이크로서비스 배치 분석

```

┌─────────────────────────┐         ┌─────────────────────────┐```bash```bash

│       Heimdall          │         │       Bifrost           │

│  (Java/Spring Boot)     │         │  (Python/FastAPI)       │# 여러 서비스 로그 동시 분석

│                         │         │                         │

│  - Log Collection       │         │  - AI Analysis          │bifrost batch service1.log service2.log service3.log --concurrent 10# logs/ 디렉토리의 모든 로그 분석## 📦 구조

│  - Log Storage (DB)     │         │  - LLM (Ollama/Bedrock) │

│  - Search API           │         │  - Result Storage       │```

│  - Statistics           │         │  - Web UI               │

└──────────┬──────────────┘         └──────────┬──────────────┘bifrost batch logs/*.log

           │                                   │

           │      ┌────────────────────┐      │### 4. Web UI로 실시간 분석

           └─────►│   Apache Kafka     │◄─────┘

                  │   - Zookeeper      │1. `uvicorn bifrost.api:app --reload` 실행``````

                  │   - Topics:        │

                  │     * analysis.request2. http://localhost:8000 접속

                  │     * analysis.result

                  │     * dlq.failed   │3. 로그 붙여넣기bifrost/

                  └────────────────────┘

4. 심각도 필터 선택 (ERROR만 보기 등)

Event Flow:

1. Heimdall → Kafka (analysis.request)5. 분석 결과를 Slack으로 전송 (옵션)### 4. API 통합├── bifrost/

2. Bifrost consumes → AI Analysis → Save to DB

3. Bifrost → Kafka (analysis.result)

4. Heimdall consumes → Update log record

```---```python│   ├── __init__.py



**상세**: [ARCHITECTURE.md](ARCHITECTURE.md) | [MSA_ARCHITECTURE.md](docs/MSA_ARCHITECTURE.md)



---## 📡 REST APIimport httpx│   ├── main.py          # CLI 진입점



## 📡 REST API



### MSA Integration Endpoints (NEW)### 분석 엔드포인트│   ├── ollama.py        # Ollama 클라이언트



```bash```bash

# Heimdall 연동 상태 확인

curl http://localhost:8000/api/v1/heimdall/status# 기본 분석response = httpx.post(│   ├── bedrock.py       # AWS Bedrock 클라이언트



# Responsecurl -X POST http://localhost:8000/api/analyze \

{

  "integration_enabled": true,  -H "X-API-Key: your-api-key" \    "http://localhost:8000/analyze",│   ├── config.py        # 설정 관리

  "kafka": {

    "enabled": true,  -H "Content-Type: application/json" \

    "bootstrap_servers": "localhost:9092",

    "consumer_running": true,  -d '{    json={"log_content": log_data, "source": "local"},│   ├── preprocessor.py  # 로그 전처리

    "producer_running": true

  },    "log_content": "ERROR: Connection failed",

  "heimdall": {

    "enabled": true,    "source": "local",    headers={"X-API-Key": "your-key"}│   └── formatter.py     # 출력 포맷터

    "callback_topic": "analysis.result",

    "ai_source": "local"    "service_name": "my-service"

  }

}  }')├── examples/



# Health Check (with Kafka status)

curl http://localhost:8000/health

# 스트리밍 분석print(response.json()["response"])│   └── sample.log       # 테스트용 로그

# Response

{curl -N http://localhost:8000/api/analyze/stream \

  "status": "healthy",

  "kafka_status": "connected",  -H "X-API-Key: your-api-key" \```├── requirements.txt

  "heimdall_integration": "active"

}  -H "Content-Type: application/json" \

```

  -d '{"log_content": "..."}'├── setup.py

### 분석 엔드포인트

```

```bash

# 기본 분석---├── bifrost.yaml.example # 설정 예시

curl -X POST http://localhost:8000/api/analyze \

  -H "X-API-Key: your-api-key" \### 필터링 & Export ✨ NEW

  -H "Content-Type: application/json" \

  -d '{```bash└── README.md

    "log_content": "ERROR: Connection failed",

    "source": "local",# 심각도 필터링

    "service_name": "my-service"

  }'curl -X POST http://localhost:8000/api/filter/severity \## 🚀 Quick Start```



# 스트리밍 분석  -H "X-API-Key: your-api-key" \

curl -N http://localhost:8000/api/analyze/stream \

  -H "X-API-Key: your-api-key" \  -H "Content-Type: application/json" \

  -H "Content-Type: application/json" \

  -d '{"log_content": "..."}'  -d '{

```

    "log_content": "INFO: Started\nERROR: Failed\nWARN: Slow",### Option 1: Docker Compose (권장)## ⚙️ 설정

### 필터링 & Export

    "min_level": "ERROR"

```bash

# 심각도 필터링  }'

curl -X POST http://localhost:8000/api/filter/severity \

  -H "X-API-Key: your-api-key" \

  -H "Content-Type: application/json" \

  -d '{# CSV Export```bash### 설정 파일 (bifrost.yaml)

    "log_content": "INFO: Started\nERROR: Failed\nWARN: Slow",

    "min_level": "ERROR"curl http://localhost:8000/api/export/csv?limit=100 \

  }'

  -H "X-API-Key: your-api-key" \# 1. 저장소 클론

# CSV Export

curl http://localhost:8000/api/export/csv?limit=100 \  -o results.csv

  -H "X-API-Key: your-api-key" \

  -o results.csvgit clone https://github.com/joeylife94/bifrost.git```bash



# Slack 전송# JSON Export

curl -X POST http://localhost:8000/api/slack/send \

  -H "X-API-Key: your-api-key" \curl http://localhost:8000/api/export/json?limit=50&pretty=true \cd bifrost# 샘플 생성

  -H "Content-Type: application/json" \

  -d '{  -H "X-API-Key: your-api-key" \

    "webhook_url": "https://hooks.slack.com/...",

    "result": {...},  -o results.jsonbifrost config --init

    "service_name": "production-api"

  }'

```

# Slack 전송# 2. 전체 스택 시작 (6개 서비스)

**전체 API 문서**: http://localhost:8000/docs

curl -X POST http://localhost:8000/api/slack/send \

---

  -H "X-API-Key: your-api-key" \docker-compose up -d# 설정 확인

## ⚙️ Configuration

  -H "Content-Type: application/json" \

### 환경변수

  -d '{bifrost config --show

```bash

# Kafka Integration (NEW)    "webhook_url": "https://hooks.slack.com/...",

export KAFKA_ENABLED=true

export KAFKA_BOOTSTRAP_SERVERS=localhost:9092    "result": {...},# 3. API 접속```

export HEIMDALL_ENABLED=true

    "service_name": "production-api"

# Database

DATABASE_URL=postgresql://user:pass@localhost/bifrost  }'open http://localhost:8000/docs



# Ollama```

OLLAMA_BASE_URL=http://localhost:11434

OLLAMA_MODEL=mistral```설정 파일 위치 (우선순위):



# AWS Bedrock (optional)### 관리 엔드포인트

AWS_REGION=us-east-1

BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0```bash1. `./bifrost.yaml`



# Rate Limiting# 히스토리 조회

RATE_LIMIT_PER_HOUR=100

curl http://localhost:8000/api/history?limit=10 \**포함된 서비스:**2. `./.bifrost.yaml`

# Logging

LOG_LEVEL=INFO  -H "X-API-Key: your-api-key"

```

- Bifrost API (port 8000)3. `~/.config/bifrost/config.yaml`

### bifrost.yaml

# 메트릭 조회

```yaml

database:curl http://localhost:8000/api/metrics \- PostgreSQL (port 5432)4. `~/.bifrost.yaml`

  url: "sqlite:///bifrost.db"

  -H "X-API-Key: your-api-key"

ollama:

  base_url: "http://localhost:11434"- Redis (port 6379)

  model: "mistral"

  timeout: 300# Prometheus 메트릭



bedrock:curl http://localhost:8000/metrics- Ollama (port 11434)### 환경변수

  region: "us-east-1"

  model_id: "anthropic.claude-3-sonnet-20240229-v1:0"



# Kafka Configuration (NEW)# 헬스 체크- Prometheus (port 9090)

kafka:

  enabled: false  # true로 변경하여 MSA 모드 활성화curl http://localhost:8000/health

  bootstrap_servers: localhost:9092

  curl http://localhost:8000/health/live- Grafana (port 3001)```bash

  consumer:

    group_id: bifrost-consumer-groupcurl http://localhost:8000/health/ready

    auto_offset_reset: earliest

    enable_auto_commit: falseexport BIFROST_OLLAMA_URL=http://localhost:11434

    max_poll_records: 100

  # 시스템 정보

  producer:

    acks: allcurl http://localhost:8000/system/info### Option 2: 로컬 개발export BIFROST_OLLAMA_MODEL=llama2

    retries: 3

    compression_type: snappy```

  

  topics:export BIFROST_BEDROCK_REGION=us-west-2

    analysis_request: analysis.request

    analysis_result: analysis.result---

    dlq: dlq.failed

```bashexport BIFROST_BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0

# Heimdall Integration (NEW)

heimdall:## 🏗️ Architecture

  enabled: false  # true로 변경하여 Heimdall 연동 활성화

  callback_topic: analysis.result# 1. 가상환경 생성```

  timeout_seconds: 60

  retry_attempts: 3```

  ai_source: local  # local (Ollama) or cloud (Bedrock)

┌─────────────────────────────────────────────────────────────┐python -m venv venv

api:

  rate_limit: 100│                      Bifrost Platform                        │

  cache_ttl_hours: 24

```├─────────────────────────────────────────────────────────────┤source venv/bin/activate  # Windows: venv\Scripts\activate## 🎯 Roadmap



---│                                                              │



## 📊 Monitoring│  ┌───────────┐  ┌───────────┐  ┌───────────┐               │



### Prometheus 메트릭│  │  Web UI   │  │    CLI    │  │  REST API │               │



| 메트릭 | 타입 | 설명 |│  │  (htmx)   │  │  (Typer)  │  │ (FastAPI) │               │# 2. 의존성 설치- [x] v0.1: Local mode (Ollama)

|--------|------|------|

| `bifrost_analysis_total` | Counter | 총 분석 요청 수 |│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘               │

| `bifrost_analysis_duration_seconds` | Histogram | 분석 소요 시간 |

| `bifrost_cache_hits_total` | Counter | 캐시 히트 수 |│        │              │              │                      │pip install -r requirements.txt- [x] v0.1: Cloud mode (AWS Bedrock) - 준비 완료

| `bifrost_cache_misses_total` | Counter | 캐시 미스 수 |

| `bifrost_errors_total` | Counter | 에러 발생 수 |│        └──────────────┴──────────────┘                      │

| `bifrost_active_requests` | Gauge | 진행 중 요청 수 |

| `bifrost_kafka_messages_consumed` | Counter | Kafka 메시지 소비 수 ⭐ NEW |│                       │                                     │- [x] v0.1: Config file support

| `bifrost_kafka_messages_produced` | Counter | Kafka 메시지 발행 수 ⭐ NEW |

│        ┌──────────────┴──────────────┐                      │

### Grafana 대시보드

│        │                             │                      │# 3. Ollama 시작- [x] v0.1: Streaming output

```bash

# Grafana 열기 (Docker Compose 실행 시)│  ┌─────▼─────┐              ┌────────▼────────┐             │

open http://localhost:3001

│  │  Ollama   │              │  AWS Bedrock    │             │ollama serve- [x] v0.1: Log preprocessing

# 기본 계정: admin/admin

```│  │  (Local)  │              │  (Claude 3)     │             │



---│  └───────────┘              └─────────────────┘             │- [x] v0.1: Multiple output formats



## 🧪 Testing│                                                              │



```bash│  ┌──────────────────────────────────────────────┐           │# 4. CLI 사용- [ ] v0.2: 배치 분석 (여러 파일)

# 전체 테스트

pytest tests/ -v│  │           Data Layer                          │           │



# Kafka 통합 테스트 (NEW)│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │           │bifrost local error.log- [ ] v0.2: 커스텀 프롬프트

pytest tests/test_kafka_integration.py -v

│  │  │PostgreSQL│  │  Redis   │  │   File   │   │           │

# 커버리지 포함

pytest tests/ --cov=bifrost --cov-report=html│  │  │   (DB)   │  │ (Cache)  │  │  Cache   │   │           │- [ ] v0.3: 웹 UI



# 특정 테스트만│  │  └──────────┘  └──────────┘  └──────────┘   │           │

pytest tests/test_api.py -v

```│  └──────────────────────────────────────────────┘           │# 5. API 서버 시작- [ ] v0.3: 히스토리 관리



**현재 커버리지**: 85%+│                                                              │



---│  ┌──────────────────────────────────────────────┐           │uvicorn bifrost.api:app --reload



## 🚀 Deployment│  │           Observability                       │           │



### Docker│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │           │```## 📝 Examples



```bash│  │  │Prometheus│  │  Grafana │  │   Logs   │   │           │

# 이미지 빌드

docker build -t bifrost:latest .│  │  └──────────┘  └──────────┘  └──────────┘   │           │



# 컨테이너 실행│  └──────────────────────────────────────────────┘           │

docker run -p 8000:8000 bifrost:latest

│                                                              │---### 샘플 로그 분석

# Docker Compose (전체 스택 with Kafka)

docker-compose up -d│  ┌──────────────────────────────────────────────┐           │

```

│  │           Integrations ✨ NEW                 │           │

### Kubernetes

│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │           │

```bash

# ConfigMap & Secret 적용│  │  │  Slack   │  │   CSV    │  │  JSON    │   │           │## 📖 Documentation```bash

kubectl apply -f k8s/config.yaml

│  │  └──────────┘  └──────────┘  └──────────┘   │           │

# 배포

kubectl apply -f k8s/deployment.yaml│  └──────────────────────────────────────────────┘           │bifrost local examples/sample.log



# 상태 확인└─────────────────────────────────────────────────────────────┘

kubectl get pods -l app=bifrost

``````| 문서 | 설명 |```



### CI/CD (GitHub Actions)



`.github/workflows/ci.yml`이 자동으로:---|------|------|

1. 테스트 실행

2. Docker 이미지 빌드

3. 이미지 푸시 (GitHub Container Registry)

4. Kubernetes 배포## 📊 Monitoring| **[PORTFOLIO.md](PORTFOLIO.md)** | 프로젝트 동기, 기술 의사결정, 증명된 역량 |### Kubernetes 로그



---



## 🛠️ Development### Prometheus 메트릭| **[ARCHITECTURE.md](ARCHITECTURE.md)** | 시스템 아키텍처, 설계 패턴, 확장성 전략 |



### 주요 명령어- `bifrost_requests_total`: 총 요청 수 (by source, status)



```bash- `bifrost_request_duration_seconds`: 요청 처리 시간| **[TECHNICAL.md](TECHNICAL.md)** | API 레퍼런스, 배포 가이드, 트러블슈팅 |```bash

# 설치 & 설정

pip install -r requirements.txt  # 의존성 설치- `bifrost_analysis_errors_total`: 분석 에러 수

python -m bifrost.main --help    # CLI 도움말

- `bifrost_cache_hits_total`: 캐시 히트 수| **[COMPLETION.md](COMPLETION.md)** | 구현 체크리스트, 기술 스택, 다음 단계 |kubectl logs -f deployment/my-app | bifrost local --stream

# 실행

uvicorn bifrost.api:app --reload # API 서버 (개발 모드)- `bifrost_active_requests`: 현재 처리 중인 요청

python -m bifrost.main local     # CLI 로컬 모드

- `bifrost_log_size_bytes`: 로그 크기 (히스토그램)| **[CHANGELOG.md](CHANGELOG.md)** | 최신 업데이트 및 변경사항 |```

# 테스트 & 검증

pytest tests/ -v                 # 테스트- `bifrost_rate_limit_exceeded_total`: Rate limit 초과 횟수

black bifrost/ tests/            # 포맷

flake8 bifrost/                  # 린트



# Docker### Grafana 대시보드

docker-compose up -d             # 전체 스택 시작

docker-compose logs -f           # 로그 확인```bash---### Docker 컨테이너 로그

docker-compose logs -f bifrost-api kafka  # 특정 서비스

```# Grafana 실행 (Docker Compose)



---docker-compose up -d grafana



## 📚 Documentation



| 문서 | 설명 |# http://localhost:3000 접속## 🏗️ Architecture```bash

|------|------|

| **[MSA_INTEGRATION_GUIDE.md](MSA_INTEGRATION_GUIDE.md)** | MSA 통합 전체 가이드 (Kafka, Heimdall) ⭐ NEW |# 대시보드 import: grafana/dashboard.json

| **[PORTFOLIO.md](PORTFOLIO.md)** | 프로젝트 동기, 기술 의사결정, 증명된 역량 |

| **[ARCHITECTURE.md](ARCHITECTURE.md)** | 시스템 아키텍처, 설계 패턴, 확장성 전략 |```docker logs my-container 2>&1 | bifrost cloud

| **[TECHNICAL.md](TECHNICAL.md)** | API 레퍼런스, 배포 가이드, 트러블슈팅 |

| **[COMPLETION.md](COMPLETION.md)** | 구현 체크리스트, 기술 스택, 다음 단계 |

| **[CHANGELOG.md](CHANGELOG.md)** | 최신 업데이트 및 변경사항 |

| **[HEIMDALL_ARCHITECTURE.md](HEIMDALL_ARCHITECTURE.md)** | Heimdall 마이크로서비스 아키텍처 |---``````

| **[HEIMDALL_IMPLEMENTATION_GUIDE.md](HEIMDALL_IMPLEMENTATION_GUIDE.md)** | Heimdall 구현 가이드 |



---

## 🧪 Development┌─────────────────────────────────────────────────────────┐

## 🤝 Contributing



1. Fork the repository

2. Create your feature branch (`git checkout -b feature/amazing`)### 1. 개발 환경 설정│                   Client Layer                          │### CI/CD 파이프라인

3. Commit your changes (`git commit -m 'Add amazing feature'`)

4. Push to the branch (`git push origin feature/amazing`)```bash

5. Open a Pull Request

# 저장소 클론│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │

**코드 스타일**: Black, Flake8  

**테스트**: pytest (필수)git clone https://github.com/joeylife94/bifrost.git



---cd bifrost│  │   CLI    │  │  WebUI   │  │  API     │             │```bash



## 📄 License



MIT License - see [LICENSE](LICENSE) for details# 의존성 설치│  └──────────┘  └──────────┘  └──────────┘             │# JSON 출력으로 파싱 가능



---make install



## 👨‍💻 Author└─────────────────────────────────────────────────────────┘bifrost local build.log --format json | jq '.response'



**Joey**  # 개발 모드 실행

MLOps & Backend Engineer  

[@joeylife94](https://github.com/joeylife94)make run                        ↓```



---```



## 🙏 Acknowledgments┌─────────────────────────────────────────────────────────┐



- **Ollama**: 로컬 LLM 런타임### 2. 테스트

- **AWS Bedrock**: Claude 3 제공

- **FastAPI**: 훌륭한 웹 프레임워크```bash│              Presentation (FastAPI)                     │## 🔧 개발

- **Apache Kafka**: 이벤트 스트리밍 플랫폼

- **SQLAlchemy**: 강력한 ORM# 전체 테스트 실행



---make test│  - Rate Limiting, Auth, Validation                      │



## 🎯 Roadmap



### v0.3 (현재) ✅# 커버리지 포함└─────────────────────────────────────────────────────────┘```bash

- [x] Kafka 기반 MSA 통합

- [x] Heimdall 연동make test-coverage

- [x] DLQ (Dead Letter Queue)

- [x] Kafka Health Check                        ↓# 개발 모드 설치



### v0.4 (계획)# 특정 테스트만

- [ ] MLflow 연동 (프롬프트 실험)

- [ ] RAG (과거 분석 결과 활용)pytest tests/test_api.py -v┌─────────────────────────────────────────────────────────┐pip install -e .

- [ ] 커스텀 프롬프트 관리

- [ ] 이상 탐지 (Anomaly Detection)```



### v1.0 (장기)│            Business Logic                               │

- [ ] SaaS 전환 (Multi-tenancy)

- [ ] Root Cause Analysis### 3. 코드 품질

- [ ] Auto-remediation

- [ ] Multi-LLM Support (OpenAI, Gemini 등)```bash│  - Preprocessor, Analyzer, Formatter                    │# 의존성 설치



---# Linting



## 📞 Supportmake lint└─────────────────────────────────────────────────────────┘pip install -r requirements.txt



- **Issues**: [GitHub Issues](https://github.com/joeylife94/bifrost/issues)

- **Discussions**: [GitHub Discussions](https://github.com/joeylife94/bifrost/discussions)

- **MSA Integration**: [MSA_INTEGRATION_GUIDE.md](MSA_INTEGRATION_GUIDE.md)# 포맷팅                        ↓```



---make format



<div align="center">┌─────────────────────────────────────────────────────────┐



**Made with ❤️ for the MLOps Community**# 타입 체크



[Documentation](TECHNICAL.md) • [Architecture](ARCHITECTURE.md) • [Portfolio](PORTFOLIO.md) • [MSA Guide](MSA_INTEGRATION_GUIDE.md)make typecheck│           Integration (LLM, DB)                         │---



</div>```


│  - Ollama Client, Bedrock Client, Database              │

### 4. Docker

```bash└─────────────────────────────────────────────────────────┘**Built with 🔨 by vibe coding**

# 이미지 빌드

make docker-build                        ↓

┌─────────────────────────────────────────────────────────┐

# 컨테이너 실행│         Infrastructure                                  │

make docker-run│  - PostgreSQL, Redis, Prometheus                        │

└─────────────────────────────────────────────────────────┘

# Docker Compose 전체 스택```

make docker-compose-up

```**상세**: [ARCHITECTURE.md](ARCHITECTURE.md)



### 5. Kubernetes---

```bash

# 배포## 💻 CLI Usage

make k8s-deploy

### 로컬 분석 (Ollama)

# 상태 확인```bash

make k8s-status# 파일 분석

bifrost local error.log

# 로그 확인

make k8s-logs# stdin 분석

cat error.log | bifrost local

# 삭제

make k8s-delete# 스트리밍 모드

```bifrost local error.log --stream



---# 마크다운 출력

bifrost local error.log --format markdown

## 📚 Documentation```



- [ARCHITECTURE.md](ARCHITECTURE.md) - 시스템 아키텍처 상세 설명### 클라우드 분석 (AWS Bedrock)

- [PORTFOLIO.md](PORTFOLIO.md) - 프로젝트 포트폴리오 문서```bash

- [CHANGELOG.md](CHANGELOG.md) - 버전별 변경 사항# AWS 설정 필요

- [COMPLETION.md](COMPLETION.md) - 향후 로드맵export AWS_PROFILE=your-profile

- [API Documentation](http://localhost:8000/docs) - Swagger UI (서버 실행 후)

bifrost cloud error.log

---```



## 🤝 Contributing### 배치 분석

```bash

1. Fork the repository# 여러 파일 동시 분석

2. Create your feature branch (`git checkout -b feature/amazing`)bifrost batch logs/*.log

3. Commit your changes (`git commit -m 'Add amazing feature'`)

4. Push to the branch (`git push origin feature/amazing`)# 결과를 파일로 저장

5. Open a Pull Requestbifrost batch logs/*.log > report.md

```

---

---

## 📝 License

## 🌐 API Usage

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 1. 로그 분석

---```bash

curl -X POST http://localhost:8000/analyze \

## 🙏 Acknowledgments  -H "X-API-Key: your-key" \

  -H "Content-Type: application/json" \

- [Ollama](https://ollama.ai) - Local LLM inference  -d '{

- [AWS Bedrock](https://aws.amazon.com/bedrock/) - Claude 3 API    "log_content": "ERROR: Connection refused",

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework    "source": "local",

- [htmx](https://htmx.org/) - Modern web UI interactions    "service_name": "my-api"

- [Prometheus](https://prometheus.io/) - Monitoring and alerting  }'

```

---

### 2. 분석 히스토리 조회

## 📧 Contact```bash

curl http://localhost:8000/history?limit=10 \

- GitHub: [@joeylife94](https://github.com/joeylife94)  -H "X-API-Key: your-key"

- Project: [Bifrost](https://github.com/joeylife94/bifrost)```



---### 3. 메트릭 확인

```bash

Made with ❤️ for MLOps Engineers# Prometheus 메트릭

curl http://localhost:8000/metrics/prometheus

# 내부 메트릭
curl http://localhost:8000/metrics
```

### 4. WebSocket 스트리밍
```python
import asyncio
import websockets

async def stream_analysis():
    async with websockets.connect("ws://localhost:8000/ws/analyze") as ws:
        await ws.send('{"log_content": "ERROR log"}')
        async for msg in ws:
            print(msg)

asyncio.run(stream_analysis())
```

**전체 API 문서**: http://localhost:8000/docs

---

## 🔧 Configuration

### 환경변수
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/bifrost

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# AWS Bedrock (optional)
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Rate Limiting
RATE_LIMIT_PER_HOUR=100

# Logging
LOG_LEVEL=INFO
```

### bifrost.yaml
```yaml
database:
  url: "sqlite:///bifrost.db"

ollama:
  base_url: "http://localhost:11434"
  model: "mistral"
  timeout: 300

bedrock:
  region: "us-east-1"
  model_id: "anthropic.claude-3-sonnet-20240229-v1:0"

api:
  rate_limit: 100
  cache_ttl_hours: 24
```

---

## 📊 Monitoring

### Prometheus 메트릭

| 메트릭 | 타입 | 설명 |
|--------|------|------|
| `bifrost_analysis_total` | Counter | 총 분석 요청 수 |
| `bifrost_analysis_duration_seconds` | Histogram | 분석 소요 시간 |
| `bifrost_cache_hits_total` | Counter | 캐시 히트 수 |
| `bifrost_cache_misses_total` | Counter | 캐시 미스 수 |
| `bifrost_errors_total` | Counter | 에러 발생 수 |
| `bifrost_active_requests` | Gauge | 진행 중 요청 수 |
| `bifrost_llm_tokens_total` | Counter | 사용한 토큰 수 |

### Grafana 대시보드

```bash
# Grafana 열기 (Docker Compose 실행 시)
open http://localhost:3001

# 기본 계정: admin/admin
```

---

## 🧪 Testing

```bash
# 전체 테스트
pytest tests/ -v

# 커버리지 포함
pytest tests/ --cov=bifrost --cov-report=html

# 특정 테스트만
pytest tests/test_api.py -v
```

**현재 커버리지**: 85%+

---

## 🚀 Deployment

### Docker

```bash
# 이미지 빌드
docker build -t bifrost:latest .

# 컨테이너 실행
docker run -p 8000:8000 bifrost:latest
```

### Kubernetes

```bash
# ConfigMap & Secret 적용
kubectl apply -f k8s/config.yaml

# 배포
kubectl apply -f k8s/deployment.yaml

# 상태 확인
kubectl get pods -l app=bifrost
```

### CI/CD (GitHub Actions)

`.github/workflows/ci.yml`이 자동으로:
1. 테스트 실행
2. Docker 이미지 빌드
3. 이미지 푸시 (GitHub Container Registry)
4. Kubernetes 배포

---

## 🛠️ Development

### 주요 명령어

```bash
# 설치 & 설정
pip install -r requirements.txt  # 의존성 설치
python -m bifrost.main --help    # CLI 도움말

# 실행
uvicorn bifrost.api:app --reload # API 서버 (개발 모드)
python -m bifrost.main local     # CLI 로컬 모드

# 테스트 & 검증
pytest tests/ -v                 # 테스트
black bifrost/ tests/            # 포맷
flake8 bifrost/                  # 린트

# Docker
docker-compose up -d             # 전체 스택 시작
docker-compose logs -f           # 로그 확인
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

**코드 스타일**: Black, Flake8  
**테스트**: pytest (필수)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## 👨‍💻 Author

**Developer**: Dongyoun Jeon (Joey)  
MLOps & Backend Engineer  
📧 sho801921@gmail.com | 💼 [LinkedIn](https://www.linkedin.com/in/dongyoun-jeon) | 🐙 [@joeylife94](https://github.com/joeylife94)

---

## 🙏 Acknowledgments

- **Ollama**: 로컬 LLM 런타임
- **AWS Bedrock**: Claude 3 제공
- **FastAPI**: 훌륭한 웹 프레임워크
- **SQLAlchemy**: 강력한 ORM

---

## 🎯 Roadmap

### v0.3 (계획)
- [ ] 웹 UI (React + shadcn/ui)
- [ ] MLflow 연동 (프롬프트 실험)
- [ ] RAG (과거 분석 결과 활용)

### v0.4 (계획)
- [ ] Slack/Discord 통합
- [ ] 커스텀 프롬프트 관리
- [ ] 이상 탐지 (Anomaly Detection)

### v1.0 (장기)
- [ ] SaaS 전환 (Multi-tenancy)
- [ ] Root Cause Analysis
- [ ] Auto-remediation

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/joeylife94/bifrost/issues)
- **Discussions**: [GitHub Discussions](https://github.com/joeylife94/bifrost/discussions)

---

<div align="center">

**Made with ❤️ for the MLOps Community**

[Documentation](TECHNICAL.md) • [Architecture](ARCHITECTURE.md) • [Portfolio](PORTFOLIO.md)

</div>
