# 🌈 Bifrost

**The Rainbow Bridge for MLOps** - Production-grade AI-powered log analysis platform

[![CI/CD](https://github.com/joeylife94/bifrost/actions/workflows/ci.yml/badge.svg)](https://github.com/joeylife94/bifrost/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 🎯 Overview

Bifrost는 MLOps 환경을 위한 **프로덕션급 AI 로그 분석 플랫폼**입니다. 로컬(Ollama) 및 클라우드(AWS Bedrock) 두 가지 모드로 작동하며, CLI와 REST API를 모두 지원합니다.

### ✨ Key Features

#### 🏗️ **Multi-Mode Architecture**
- 🏠 **로컬 모드**: Ollama 기반 프라이버시 우선 분석
- ☁️ **클라우드 모드**: AWS Bedrock (Claude 3) 프로덕션 스케일
- 🔄 **하이브리드**: 비용 최적화된 자동 라우팅

#### 🚀 **Production Ready**
- 📊 **REST API**: FastAPI 기반 고성능 API 서버
- 🗄️ **데이터베이스**: SQLAlchemy + PostgreSQL/SQLite
- 📈 **모니터링**: Prometheus + Grafana 통합
- 🔐 **보안**: API 키 관리, Rate limiting
- 🐳 **컨테이너화**: Docker + Kubernetes 배포

#### ⚡ **Performance**
- 🔄 **배치 처리**: 비동기 다중 파일 분석
- 💾 **스마트 캐싱**: 중복 분석 방지
- 🔁 **재시도 로직**: 네트워크 불안정 대응
- 📊 **스트리밍**: 실시간 응답 (WebSocket)

#### 🎨 **Developer Experience**
- 🖥️ **CLI**: Typer 기반 직관적 인터페이스
- 📝 **다양한 포맷**: Markdown, JSON, Plain text
- ⚙️ **유연한 설정**: YAML 파일 + 환경변수
- 🧪 **테스트**: pytest 기반 comprehensive test suite

---

## 🚀 Quick Start

### 1️⃣ Installation

```bash
# Clone repository
git clone https://github.com/joeylife94/bifrost.git
cd bifrost

# Setup (자동)
chmod +x scripts/setup.sh
./scripts/setup.sh

# 또는 수동 설치
pip install -r requirements.txt
pip install -e .
```

### 2️⃣ Ollama Setup (로컬 모드)

```bash
# Ollama 설치: https://ollama.ai
ollama pull mistral
ollama serve
```

### 3️⃣ Usage

#### CLI Mode

```bash
# 단일 파일 분석
bifrost local error.log
bifrost local --stream --verbose app.log

# 파이프 입력
kubectl logs my-pod | bifrost local
docker logs my-container | bifrost cloud

# 배치 처리
bifrost batch ./logs --workers 8

# 출력 포맷
bifrost local --format json app.log > result.json
```

#### API Server Mode

```bash
# 서버 시작
bifrost serve

# 또는 Docker Compose
docker-compose up -d

# 데모 실행
python scripts/demo.py
```

#### API 사용 예시

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "log_content": "2024-10-25 ERROR Database connection failed",
        "source": "local",
        "service_name": "my-app",
        "tags": ["error", "database"]
    }
)

print(response.json()["response"])
```

---

## 📦 Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Users / Applications                │
└──────────────┬──────────────────────┬───────────────┘
               │                      │
         CLI   │              REST API│   WebSocket
               │                      │
        ┌──────▼──────────────────────▼──────┐
        │         Bifrost Core                │
        │  ┌──────────────────────────────┐   │
        │  │  Analysis Engine             │   │
        │  │  - Ollama (Local/GPU)        │   │
        │  │  - Bedrock (Cloud)           │   │
        │  │  - Batch Processor           │   │
        │  └──────────────────────────────┘   │
        │                                      │
        │  ┌──────────────────────────────┐   │
        │  │  Storage Layer               │   │
        │  │  - PostgreSQL                │   │
        │  │  - Redis (Cache/Queue)       │   │
        │  │  - Smart Caching             │   │
        │  └──────────────────────────────┘   │
        │                                      │
        │  ┌──────────────────────────────┐   │
        │  │  Observability               │   │
        │  │  - Prometheus Metrics        │   │
        │  │  - Structured Logging        │   │
        │  └──────────────────────────────┘   │
        └──────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │ Grafana │
                    └─────────┘
```

### 프로젝트 구조

```
bifrost/
├── bifrost/              # 메인 패키지
│   ├── main.py           # CLI 진입점
│   ├── api.py            # FastAPI 서버
│   ├── ollama.py         # Ollama 클라이언트
│   ├── bedrock.py        # AWS Bedrock 클라이언트
│   ├── database.py       # DB 관리
│   ├── models.py         # SQLAlchemy 모델
│   ├── batch.py          # 배치 처리
│   ├── preprocessor.py   # 로그 전처리
│   ├── formatter.py      # 출력 포맷터
│   ├── config.py         # 설정 관리
│   └── metrics.py        # Prometheus 메트릭
├── tests/                # 테스트
├── k8s/                  # Kubernetes manifests
├── monitoring/           # Prometheus/Grafana 설정
├── scripts/              # 유틸리티 스크립트
├── examples/             # 샘플 로그
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## ⚙️ Configuration

### YAML 설정 파일

```bash
# 샘플 생성
bifrost config --init

# 설정 확인
bifrost config --show
```

설정 위치 우선순위:
1. `./bifrost.yaml`
2. `./.bifrost.yaml`
3. `~/.config/bifrost/config.yaml`
4. `~/.bifrost.yaml`

### 환경변수

```bash
export BIFROST_OLLAMA_URL=http://localhost:11434
export BIFROST_OLLAMA_MODEL=llama2
export BIFROST_BEDROCK_REGION=us-west-2
export DATABASE_URL=postgresql://user:pass@localhost/bifrost
```

---

## 🐳 Docker & Kubernetes

### Docker Compose

```bash
# 전체 스택 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f api

# 서비스:
# - api:        localhost:8000
# - prometheus: localhost:9090
# - grafana:    localhost:3000 (admin/admin)
# - postgres:   localhost:5432
# - redis:      localhost:6379
```

### Kubernetes

```bash
# 배포
kubectl apply -f k8s/

# 상태 확인
kubectl get pods -l app=bifrost

# 로그 확인
kubectl logs -f deployment/bifrost-api
```

---

## 📊 Monitoring

### Prometheus Metrics

```bash
# 메트릭 조회
curl http://localhost:8000/metrics/prometheus

# 주요 메트릭:
# - bifrost_analysis_total: 총 분석 수
# - bifrost_analysis_duration_seconds: 분석 소요 시간
# - bifrost_cache_hits_total: 캐시 히트 수
# - bifrost_errors_total: 에러 수
```

### Grafana Dashboard

1. http://localhost:3000 접속
2. admin/admin 로그인
3. Bifrost 대시보드 열기

---

## 🧪 Testing

```bash
# 전체 테스트
pytest

# 커버리지
pytest --cov=bifrost --cov-report=html

# 특정 테스트
pytest tests/test_api.py -v
```

---

## 📈 Roadmap

### ✅ v0.1 - Foundation
- [x] CLI 기본 기능
- [x] Ollama 통합
- [x] 기본 전처리

### ✅ v0.2 - Production Ready (Current)
- [x] FastAPI REST API
- [x] PostgreSQL + SQLAlchemy
- [x] Prometheus 메트릭
- [x] Docker + K8s
- [x] 배치 처리
- [x] AWS Bedrock 지원
- [x] 테스트 suite
- [x] CI/CD 파이프라인

### 🚧 v0.3 - Advanced Features
- [ ] 웹 UI (React/Svelte)
- [ ] MLflow 연동
- [ ] RAG (Retrieval-Augmented Generation)
- [ ] 커스텀 프롬프트 관리
- [ ] Slack/PagerDuty 알림
- [ ] 이상 탐지 (Anomaly Detection)

### 🎯 v0.4 - Enterprise
- [ ] Multi-tenancy
- [ ] RBAC (Role-Based Access Control)
- [ ] Audit logging
- [ ] SLA 모니터링
- [ ] Auto-scaling 최적화
- [ ] Cost optimization

---

## 💡 Use Cases

### 1. Kubernetes 로그 분석
```bash
kubectl logs -f deployment/my-app | bifrost local --stream
```

### 2. CI/CD 파이프라인 통합
```yaml
- name: Analyze build logs
  run: |
    cat build.log | bifrost local --format json > analysis.json
```

### 3. 배치 로그 감사
```bash
bifrost batch /var/log/apps --pattern "*.log" --workers 16
```

### 4. API 통합
```python
# 마이크로서비스에서 실시간 분석
async def analyze_error(error_log):
    response = await client.post(
        "http://bifrost-api:8000/analyze",
        json={"log_content": error_log, "source": "cloud"}
    )
    return response.json()
```

---

## 🤝 Contributing

```bash
# Fork & Clone
git clone https://github.com/YOUR_USERNAME/bifrost.git

# Create branch
git checkout -b feature/amazing-feature

# Run tests
pytest

# Commit & Push
git commit -m "feat: Add amazing feature"
git push origin feature/amazing-feature
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) - Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com/) - Modern API framework
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [Prometheus](https://prometheus.io/) - Monitoring

---

## 📧 Contact

**Joey** - MLOps & Backend Engineer

- GitHub: [@joeylife94](https://github.com/joeylife94)
- Project: [bifrost](https://github.com/joeylife94/bifrost)

---

**Built with 🔨 by vibe coding** | **Powered by 🌈 Bifrost**
