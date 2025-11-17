# 🌈 Bifrost# 🌈 Bifrost



> **The Rainbow Bridge for MLOps** - AI-powered log analysis platform**The Rainbow Bridge for MLOps** - AI-powered log analysis CLI



[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)## v0.1 - "미드가르드" (Local & Cloud Ready)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)Bifrost는 로컬(Ollama) 및 클라우드(AWS Bedrock) 두 가지 모드로 작동하는 AI 기반 로그 분석 도구입니다.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ✨ Features

**Bifrost**는 MLOps 환경의 로그를 AI로 자동 분석하는 프로덕션급 플랫폼입니다.  

Kubernetes, CI/CD 파이프라인, 마이크로서비스 로그를 AI로 빠르게 분석하고 인사이트를 얻으세요.- 🏠 **로컬 모드**: Ollama를 사용한 프라이버시 우선 분석

- ☁️ **클라우드 모드**: AWS Bedrock (Claude 3) 프로덕션 스케일

---- � **스트리밍 출력**: 실시간 응답 확인

- ⚙️ **유연한 설정**: YAML 설정 파일 + 환경변수 지원

## ✨ Features- 🎨 **다양한 포맷**: Markdown, JSON, Plain text 출력

- 🔧 **로그 전처리**: 크기 제한, 타임스탬프 제거, 자동 정리

### 🚀 Core- 🔁 **재시도 로직**: 네트워크 불안정 대응

- ✅ **CLI & REST API**: 터미널과 프로그래밍 방식 모두 지원

- ✅ **Hybrid LLM**: Ollama (로컬) + AWS Bedrock (클라우드)## �🚀 Quick Start

- ✅ **배치 처리**: 수백 개 로그 파일 동시 분석 (비동기)

- ✅ **스트리밍**: 실시간 분석 결과 (WebSocket)### 1. 설치

- ✅ **캐싱**: SHA256 해시 기반 중복 분석 방지

```bash

### 🔒 프로덕션 보안pip install -e .

- ✅ **API 키 인증**: 안전한 API 액세스

- ✅ **Rate Limiting**: 시간당 요청 제한 (토큰 버킷)# AWS Bedrock 사용 시 (선택)

- ✅ **입력 검증**: 크기 제한, XSS 방지, 형식 검증pip install boto3

- ✅ **에러 핸들링**: 계층화된 예외 처리```



### 📊 관찰성### 2. Ollama 준비 (로컬 모드)

- ✅ **Prometheus 메트릭**: 7가지 커스텀 메트릭

- ✅ **구조화된 로깅**: JSON 로그 (Elasticsearch 연동 가능)```bash

- ✅ **헬스 체크**: Kubernetes liveness/readiness probes# Ollama 설치 (https://ollama.ai)

- ✅ **Grafana 대시보드**: 실시간 모니터링ollama pull mistral

ollama serve

### 🛠️ DevOps```

- ✅ **Docker**: 멀티 스테이지 빌드 (최적화)

- ✅ **Kubernetes**: HPA, ConfigMap, Secret### 3. 사용

- ✅ **CI/CD**: GitHub Actions (테스트, 빌드, 배포)

- ✅ **Makefile**: 원라인 개발 명령어```bash

# 로컬 모드 (Ollama)

---bifrost local error.log

bifrost local --stream app.log

## 🎯 Use Cases

# 클라우드 모드 (AWS Bedrock)

### 1. Kubernetes 로그 분석bifrost cloud error.log

```bashbifrost cloud --region us-west-2 app.log

kubectl logs my-pod | bifrost local

```# 파이프 입력

kubectl logs my-pod | bifrost local

### 2. CI/CD 실패 원인 파악docker logs my-container | bifrost cloud

```bash

# GitHub Actions 로그 다운로드# 출력 포맷 변경

gh run view 123456 --log > ci.logbifrost local --format json app.log

bifrost local --format plain error.log > analysis.txt

# Bifrost로 분석

bifrost local ci.log# 설정 파일 생성

```bifrost config --init

bifrost config --show

### 3. 배치 분석```

```bash

# logs/ 디렉토리의 모든 로그 분석## 📦 구조

bifrost batch logs/*.log

``````

bifrost/

### 4. API 통합├── bifrost/

```python│   ├── __init__.py

import httpx│   ├── main.py          # CLI 진입점

│   ├── ollama.py        # Ollama 클라이언트

response = httpx.post(│   ├── bedrock.py       # AWS Bedrock 클라이언트

    "http://localhost:8000/analyze",│   ├── config.py        # 설정 관리

    json={"log_content": log_data, "source": "local"},│   ├── preprocessor.py  # 로그 전처리

    headers={"X-API-Key": "your-key"}│   └── formatter.py     # 출력 포맷터

)├── examples/

print(response.json()["response"])│   └── sample.log       # 테스트용 로그

```├── requirements.txt

├── setup.py

---├── bifrost.yaml.example # 설정 예시

└── README.md

## 🚀 Quick Start```



### Option 1: Docker Compose (권장)## ⚙️ 설정



```bash### 설정 파일 (bifrost.yaml)

# 1. 저장소 클론

git clone https://github.com/joeylife94/bifrost.git```bash

cd bifrost# 샘플 생성

bifrost config --init

# 2. 전체 스택 시작 (6개 서비스)

docker-compose up -d# 설정 확인

bifrost config --show

# 3. API 접속```

open http://localhost:8000/docs

```설정 파일 위치 (우선순위):

1. `./bifrost.yaml`

**포함된 서비스:**2. `./.bifrost.yaml`

- Bifrost API (port 8000)3. `~/.config/bifrost/config.yaml`

- PostgreSQL (port 5432)4. `~/.bifrost.yaml`

- Redis (port 6379)

- Ollama (port 11434)### 환경변수

- Prometheus (port 9090)

- Grafana (port 3001)```bash

export BIFROST_OLLAMA_URL=http://localhost:11434

### Option 2: 로컬 개발export BIFROST_OLLAMA_MODEL=llama2

export BIFROST_BEDROCK_REGION=us-west-2

```bashexport BIFROST_BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0

# 1. 가상환경 생성```

python -m venv venv

source venv/bin/activate  # Windows: venv\Scripts\activate## 🎯 Roadmap



# 2. 의존성 설치- [x] v0.1: Local mode (Ollama)

pip install -r requirements.txt- [x] v0.1: Cloud mode (AWS Bedrock) - 준비 완료

- [x] v0.1: Config file support

# 3. Ollama 시작- [x] v0.1: Streaming output

ollama serve- [x] v0.1: Log preprocessing

- [x] v0.1: Multiple output formats

# 4. CLI 사용- [ ] v0.2: 배치 분석 (여러 파일)

bifrost local error.log- [ ] v0.2: 커스텀 프롬프트

- [ ] v0.3: 웹 UI

# 5. API 서버 시작- [ ] v0.3: 히스토리 관리

uvicorn bifrost.api:app --reload

```## 📝 Examples



---### 샘플 로그 분석



## 📖 Documentation```bash

bifrost local examples/sample.log

| 문서 | 설명 |```

|------|------|

| **[PORTFOLIO.md](PORTFOLIO.md)** | 프로젝트 동기, 기술 의사결정, 증명된 역량 |### Kubernetes 로그

| **[ARCHITECTURE.md](ARCHITECTURE.md)** | 시스템 아키텍처, 설계 패턴, 확장성 전략 |

| **[TECHNICAL.md](TECHNICAL.md)** | API 레퍼런스, 배포 가이드, 트러블슈팅 |```bash

| **[COMPLETION.md](COMPLETION.md)** | 구현 체크리스트, 기술 스택, 다음 단계 |kubectl logs -f deployment/my-app | bifrost local --stream

| **[CHANGELOG.md](CHANGELOG.md)** | 최신 업데이트 및 변경사항 |```



---### Docker 컨테이너 로그



## 🏗️ Architecture```bash

docker logs my-container 2>&1 | bifrost cloud

``````

┌─────────────────────────────────────────────────────────┐

│                   Client Layer                          │### CI/CD 파이프라인

│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │

│  │   CLI    │  │  WebUI   │  │  API     │             │```bash

│  └──────────┘  └──────────┘  └──────────┘             │# JSON 출력으로 파싱 가능

└─────────────────────────────────────────────────────────┘bifrost local build.log --format json | jq '.response'

                        ↓```

┌─────────────────────────────────────────────────────────┐

│              Presentation (FastAPI)                     │## 🔧 개발

│  - Rate Limiting, Auth, Validation                      │

└─────────────────────────────────────────────────────────┘```bash

                        ↓# 개발 모드 설치

┌─────────────────────────────────────────────────────────┐pip install -e .

│            Business Logic                               │

│  - Preprocessor, Analyzer, Formatter                    │# 의존성 설치

└─────────────────────────────────────────────────────────┘pip install -r requirements.txt

                        ↓```

┌─────────────────────────────────────────────────────────┐

│           Integration (LLM, DB)                         │---

│  - Ollama Client, Bedrock Client, Database              │

└─────────────────────────────────────────────────────────┘**Built with 🔨 by vibe coding**

                        ↓
┌─────────────────────────────────────────────────────────┐
│         Infrastructure                                  │
│  - PostgreSQL, Redis, Prometheus                        │
└─────────────────────────────────────────────────────────┘
```

**상세**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 💻 CLI Usage

### 로컬 분석 (Ollama)
```bash
# 파일 분석
bifrost local error.log

# stdin 분석
cat error.log | bifrost local

# 스트리밍 모드
bifrost local error.log --stream

# 마크다운 출력
bifrost local error.log --format markdown
```

### 클라우드 분석 (AWS Bedrock)
```bash
# AWS 설정 필요
export AWS_PROFILE=your-profile

bifrost cloud error.log
```

### 배치 분석
```bash
# 여러 파일 동시 분석
bifrost batch logs/*.log

# 결과를 파일로 저장
bifrost batch logs/*.log > report.md
```

---

## 🌐 API Usage

### 1. 로그 분석
```bash
curl -X POST http://localhost:8000/analyze \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "log_content": "ERROR: Connection refused",
    "source": "local",
    "service_name": "my-api"
  }'
```

### 2. 분석 히스토리 조회
```bash
curl http://localhost:8000/history?limit=10 \
  -H "X-API-Key: your-key"
```

### 3. 메트릭 확인
```bash
# Prometheus 메트릭
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

**Joey**  
MLOps & Backend Engineer  
[@joeylife94](https://github.com/joeylife94)

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
