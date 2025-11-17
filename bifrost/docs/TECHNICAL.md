# Bifrost Technical Documentation

## 시스템 아키텍처

### 레이어 구조

```
┌─────────────────────────────────────┐
│     Presentation Layer              │
│  - CLI (Typer)                      │
│  - REST API (FastAPI)               │
│  - WebSocket                        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     Business Logic Layer            │
│  - Analysis Engine                  │
│  - Batch Processor                  │
│  - Preprocessor                     │
│  - Formatter                        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     Integration Layer               │
│  - Ollama Client                    │
│  - Bedrock Client                   │
│  - Database ORM                     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     Infrastructure Layer            │
│  - PostgreSQL                       │
│  - Redis                            │
│  - Prometheus                       │
└─────────────────────────────────────┘
```

### 데이터 흐름

1. **입력**: CLI/API → 전처리 → 캐시 확인
2. **처리**: LLM 호출 (Ollama/Bedrock)
3. **저장**: DB 저장 + 메트릭 업데이트
4. **출력**: 포맷팅 → 응답

## API 레퍼런스

### POST /analyze

로그 분석 요청

**Request:**
```json
{
  "log_content": "string",
  "source": "local|cloud",
  "model": "string (optional)",
  "service_name": "string (optional)",
  "environment": "string (optional)",
  "tags": ["string"]
}
```

**Response:**
```json
{
  "id": 123,
  "response": "분석 결과...",
  "duration_seconds": 2.5,
  "model": "mistral",
  "cached": false
}
```

### POST /history

분석 히스토리 조회

**Request:**
```json
{
  "limit": 50,
  "offset": 0,
  "service_name": "string (optional)",
  "model": "string (optional)",
  "status": "string (optional)"
}
```

### GET /metrics

시스템 메트릭 조회

**Query Params:**
- `hours`: 조회 기간 (기본: 24)

**Response:**
```json
{
  "total_analyses": 1234,
  "avg_duration_seconds": 2.5,
  "model_stats": [
    {
      "model": "mistral",
      "count": 800,
      "avg_duration": 2.3
    }
  ]
}
```

## 데이터베이스 스키마

### analysis_results

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| created_at | DATETIME | 생성 시각 |
| source | VARCHAR(50) | local/cloud |
| model | VARCHAR(100) | 모델명 |
| log_content | TEXT | 원본 로그 |
| log_hash | VARCHAR(64) | SHA256 해시 |
| response | TEXT | 분석 결과 |
| duration_seconds | FLOAT | 소요 시간 |
| service_name | VARCHAR(100) | 서비스명 |
| tags | JSON | 태그 배열 |
| status | VARCHAR(20) | completed/failed |

### analysis_metrics

시계열 메트릭 저장

### prompt_templates

프롬프트 버전 관리

### api_keys

API 키 관리 및 rate limiting

## 배포 가이드

### Docker Compose (개발)

```bash
# 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f api

# 정지
docker-compose down
```

### Kubernetes (프로덕션)

```bash
# Secret 생성
kubectl create secret generic bifrost-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=api-key="..."

# 배포
kubectl apply -f k8s/

# 스케일 조정
kubectl scale deployment bifrost-api --replicas=5

# 롤링 업데이트
kubectl set image deployment/bifrost-api api=bifrost:v0.3
```

### 모니터링 설정

1. **Prometheus**: http://localhost:9090
   - Targets 확인: http://localhost:9090/targets

2. **Grafana**: http://localhost:3000
   - Data Source 추가: Prometheus (http://prometheus:9090)
   - Dashboard 가져오기

### 성능 튜닝

#### PostgreSQL

```sql
-- 인덱스 확인
SELECT * FROM pg_indexes WHERE tablename = 'analysis_results';

-- 쿼리 성능
EXPLAIN ANALYZE SELECT * FROM analysis_results WHERE service_name = 'app';
```

#### API 서버

```yaml
# uvicorn workers 조정
workers: 4
worker_class: uvicorn.workers.UvicornWorker
```

## 트러블슈팅

### Ollama 연결 실패

```bash
# Ollama 상태 확인
ollama list

# 재시작
ollama serve
```

### 데이터베이스 마이그레이션

```bash
# Alembic 초기화
alembic init alembic

# 마이그레이션 생성
alembic revision --autogenerate -m "Add new column"

# 적용
alembic upgrade head
```

### 메모리 부족

```bash
# 배치 워커 수 줄이기
bifrost batch ./logs --workers 2

# 로그 크기 제한 조정
# bifrost.yaml에서 max_size_mb 설정
```

## 확장 가이드

### 새 LLM 프로바이더 추가

```python
# bifrost/newprovider.py
class NewProviderClient:
    def analyze(self, prompt: str) -> Dict[str, Any]:
        # 구현
        pass
```

### 커스텀 프롬프트

```python
# DB에 저장
db.save_prompt_template(
    name="kubernetes",
    version="1.0",
    template="K8s 로그를 분석하세요: {log_content}",
)
```

### WebHook 통합

```python
# bifrost/webhook.py
async def send_webhook(result: Dict):
    await httpx.post(
        WEBHOOK_URL,
        json=result,
    )
```
