# 🌈 Bifrost - MSA Architecture Integration Guide

> **AI-Powered Log Analysis Platform with Microservices Architecture**

---

## 🎯 MSA Integration Overview

Bifrost는 **Heimdall**과 **Apache Kafka**를 통해 MSA(Microservices Architecture)로 통합됩니다.

### Architecture

```
┌──────────────┐         Kafka         ┌──────────────┐
│   Heimdall   │◄────────────────────►│   Bifrost    │
│ (Java/Spring)│   Event-Driven       │ (Python/AI)  │
│              │   Communication      │              │
│ - Log Store  │                       │ - AI Analysis│
│ - Search     │                       │ - LLM Models │
│ - Statistics │                       │ - Web UI     │
└──────────────┘                       └──────────────┘
```

### Communication Flow

1. **Heimdall → Bifrost** (분석 요청)
   - Topic: `analysis.request`
   - Heimdall이 로그 수집 시 Bifrost에 AI 분석 요청

2. **Bifrost → Heimdall** (분석 결과)
   - Topic: `analysis.result`
   - Bifrost가 AI 분석 완료 후 결과 전송

---

## 🚀 Quick Start (MSA Mode)

### 1. 전체 스택 실행 (Kafka 포함)

```bash
# Docker Compose로 모든 서비스 시작
docker-compose up -d

# 서비스 확인
docker-compose ps

# 로그 확인
docker-compose logs -f bifrost-api
```

**포함된 서비스:**
- Bifrost API (port 8000)
- PostgreSQL (port 5432)
- Redis (port 6379)
- Ollama (port 11434)
- **Kafka (port 9092, 9093)**
- **Zookeeper (port 2181)**
- **Kafka UI (port 8090)** - 선택적
- Prometheus (port 9090)
- Grafana (port 3000)

### 2. Kafka 설정

**bifrost.yaml 파일 생성:**

```bash
# 샘플 설정 복사
cp bifrost.yaml.example bifrost.yaml
```

**bifrost.yaml 수정:**

```yaml
kafka:
  enabled: true  # Kafka 활성화
  bootstrap_servers: localhost:9092
  
  topics:
    analysis_request: analysis.request
    analysis_result: analysis.result
    dlq: dlq.failed

heimdall:
  enabled: true  # Heimdall 연동 활성화
  ai_source: local  # local (Ollama) or cloud (Bedrock)
```

### 3. API 서버 시작

```bash
# 의존성 설치
pip install -r requirements.txt

# API 서버 실행 (Kafka 활성화)
KAFKA_ENABLED=true HEIMDALL_ENABLED=true uvicorn bifrost.api:app --reload
```

---

## 📡 Kafka Topics

### analysis.request

Heimdall → Bifrost로 전송되는 분석 요청 이벤트

**Schema:**
```json
{
  "request_id": "uuid",
  "timestamp": "2024-11-12T10:30:00Z",
  "log_id": 12345,
  "log_content": "ERROR: Connection timeout...",
  "service_name": "user-service",
  "environment": "production",
  "analysis_type": "error",
  "priority": "HIGH",
  "callback_topic": "analysis.result",
  "correlation_id": "correlation-uuid"
}
```

### analysis.result

Bifrost → Heimdall로 전송되는 분석 결과 이벤트

**Schema:**
```json
{
  "request_id": "uuid",
  "correlation_id": "correlation-uuid",
  "timestamp": "2024-11-12T10:30:15Z",
  "log_id": 12345,
  "analysis_result": {
    "summary": "분석 요약",
    "root_cause": "근본 원인",
    "recommendation": "해결 권장사항",
    "severity": "HIGH",
    "confidence": 0.95
  },
  "bifrost_analysis_id": 789,
  "model": "mistral-7b",
  "duration_seconds": 2.5
}
```

---

## 🔧 Configuration

### 환경변수

```bash
# Kafka 설정
export KAFKA_ENABLED=true
export KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# Heimdall 통합
export HEIMDALL_ENABLED=true

# AI 모델 선택
export BIFROST_OLLAMA_MODEL=mistral
# 또는
export BIFROST_BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
```

### bifrost.yaml (전체 설정)

```yaml
# Ollama (로컬 AI)
ollama:
  url: http://localhost:11434
  model: mistral
  timeout: 120

# Bedrock (클라우드 AI)
bedrock:
  region: us-east-1
  model: anthropic.claude-3-sonnet-20240229-v1:0

# Kafka (MSA Integration)
kafka:
  enabled: false  # true로 변경
  bootstrap_servers: localhost:9092
  
  consumer:
    group_id: bifrost-consumer-group
    auto_offset_reset: earliest
    enable_auto_commit: false
    max_poll_records: 100
  
  producer:
    acks: all
    retries: 3
    compression_type: snappy
  
  topics:
    analysis_request: analysis.request
    analysis_result: analysis.result
    dlq: dlq.failed

# Heimdall Integration
heimdall:
  enabled: false  # true로 변경
  callback_topic: analysis.result
  timeout_seconds: 60
  retry_attempts: 3
  ai_source: local  # local or cloud
```

---

## 🧪 Testing

### 1. Kafka 연결 테스트

```bash
# Kafka 토픽 목록 확인
docker exec bifrost-kafka kafka-topics --list --bootstrap-server localhost:9092

# 토픽 생성 (수동)
docker exec bifrost-kafka kafka-topics --create \
  --topic analysis.request \
  --partitions 3 \
  --replication-factor 1 \
  --bootstrap-server localhost:9092
```

### 2. 메시지 수동 발행

```bash
# analysis.request 토픽으로 테스트 메시지 발행
docker exec -it bifrost-kafka kafka-console-producer \
  --broker-list localhost:9092 \
  --topic analysis.request

# JSON 메시지 입력 (Ctrl+D로 종료)
{
  "request_id": "test-123",
  "log_id": 12345,
  "log_content": "ERROR: Test error",
  "service_name": "test-service",
  "environment": "dev",
  "analysis_type": "error",
  "priority": "NORMAL",
  "callback_topic": "analysis.result",
  "correlation_id": "corr-123"
}
```

### 3. 메시지 수신 확인

```bash
# analysis.result 토픽에서 메시지 읽기
docker exec -it bifrost-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic analysis.result \
  --from-beginning
```

### 4. 통합 테스트 실행

```bash
# Python 테스트
pytest tests/test_kafka_integration.py -v

# 특정 테스트만
pytest tests/test_kafka_integration.py::TestKafkaEvents::test_analysis_request_event_creation -v
```

---

## 📊 Monitoring

### Heimdall 연동 상태 확인

```bash
# API로 상태 확인
curl http://localhost:8000/api/v1/heimdall/status

# 응답 예시
{
  "integration_enabled": true,
  "kafka": {
    "enabled": true,
    "bootstrap_servers": "localhost:9092",
    "consumer_running": true,
    "producer_running": true
  },
  "heimdall": {
    "enabled": true,
    "callback_topic": "analysis.result",
    "ai_source": "local"
  },
  "topics": {
    "analysis_request": "analysis.request",
    "analysis_result": "analysis.result",
    "dlq": "dlq.failed"
  }
}
```

### Kafka UI

브라우저에서 http://localhost:8090 접속

- 토픽 목록 조회
- 메시지 확인
- Consumer Group 모니터링
- Consumer Lag 확인

### Prometheus 메트릭

```bash
# Kafka 관련 메트릭
curl http://localhost:8000/metrics | grep kafka
```

---

## 🔍 Troubleshooting

### Kafka 연결 실패

```bash
# Kafka 상태 확인
docker logs bifrost-kafka

# Zookeeper 상태 확인
docker logs bifrost-zookeeper

# 네트워크 확인
docker network inspect bifrost_bifrost-network
```

### Consumer Lag 발생

```bash
# Consumer Group 상태 확인
docker exec bifrost-kafka kafka-consumer-groups \
  --describe \
  --group bifrost-consumer-group \
  --bootstrap-server localhost:9092

# Lag가 크면 Consumer Concurrency 증가 (config.py)
```

### 메시지 처리 실패 (DLQ)

```bash
# DLQ 토픽에서 실패한 메시지 확인
docker exec -it bifrost-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic dlq.failed \
  --from-beginning
```

---

## 📚 Additional Documentation

- [MSA_ARCHITECTURE.md](docs/MSA_ARCHITECTURE.md) - 전체 MSA 아키텍처
- [BIFROST_INTEGRATION_UPDATES.md](docs/BIFROST_INTEGRATION_UPDATES.md) - 통합 업데이트 가이드
- [HEIMDALL_ARCHITECTURE.md](HEIMDALL_ARCHITECTURE.md) - Heimdall 아키텍처
- [HEIMDALL_IMPLEMENTATION_GUIDE.md](HEIMDALL_IMPLEMENTATION_GUIDE.md) - Heimdall 구현 가이드

---

## 🤝 Contributing

Heimdall 프로젝트와 함께 개발 중입니다. 이슈 및 PR은 GitHub에서 관리합니다.

---

**Version**: 0.3.0 (MSA Integration)  
**Last Updated**: 2024-11-12  
**Made with ❤️ for MLOps Engineers**
