# 🌈 Bifrost

**The Rainbow Bridge for MLOps** - AI-powered log analysis CLI

## v0.1 - "미드가르드" (Local & Cloud Ready)

Bifrost는 로컬(Ollama) 및 클라우드(AWS Bedrock) 두 가지 모드로 작동하는 AI 기반 로그 분석 도구입니다.

## ✨ Features

- 🏠 **로컬 모드**: Ollama를 사용한 프라이버시 우선 분석
- ☁️ **클라우드 모드**: AWS Bedrock (Claude 3) 프로덕션 스케일
- � **스트리밍 출력**: 실시간 응답 확인
- ⚙️ **유연한 설정**: YAML 설정 파일 + 환경변수 지원
- 🎨 **다양한 포맷**: Markdown, JSON, Plain text 출력
- 🔧 **로그 전처리**: 크기 제한, 타임스탬프 제거, 자동 정리
- 🔁 **재시도 로직**: 네트워크 불안정 대응

## �🚀 Quick Start

### 1. 설치

```bash
pip install -e .

# AWS Bedrock 사용 시 (선택)
pip install boto3
```

### 2. Ollama 준비 (로컬 모드)

```bash
# Ollama 설치 (https://ollama.ai)
ollama pull mistral
ollama serve
```

### 3. 사용

```bash
# 로컬 모드 (Ollama)
bifrost local error.log
bifrost local --stream app.log

# 클라우드 모드 (AWS Bedrock)
bifrost cloud error.log
bifrost cloud --region us-west-2 app.log

# 파이프 입력
kubectl logs my-pod | bifrost local
docker logs my-container | bifrost cloud

# 출력 포맷 변경
bifrost local --format json app.log
bifrost local --format plain error.log > analysis.txt

# 설정 파일 생성
bifrost config --init
bifrost config --show
```

## 📦 구조

```
bifrost/
├── bifrost/
│   ├── __init__.py
│   ├── main.py          # CLI 진입점
│   ├── ollama.py        # Ollama 클라이언트
│   ├── bedrock.py       # AWS Bedrock 클라이언트
│   ├── config.py        # 설정 관리
│   ├── preprocessor.py  # 로그 전처리
│   └── formatter.py     # 출력 포맷터
├── examples/
│   └── sample.log       # 테스트용 로그
├── requirements.txt
├── setup.py
├── bifrost.yaml.example # 설정 예시
└── README.md
```

## ⚙️ 설정

### 설정 파일 (bifrost.yaml)

```bash
# 샘플 생성
bifrost config --init

# 설정 확인
bifrost config --show
```

설정 파일 위치 (우선순위):
1. `./bifrost.yaml`
2. `./.bifrost.yaml`
3. `~/.config/bifrost/config.yaml`
4. `~/.bifrost.yaml`

### 환경변수

```bash
export BIFROST_OLLAMA_URL=http://localhost:11434
export BIFROST_OLLAMA_MODEL=llama2
export BIFROST_BEDROCK_REGION=us-west-2
export BIFROST_BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
```

## 🎯 Roadmap

- [x] v0.1: Local mode (Ollama)
- [x] v0.1: Cloud mode (AWS Bedrock) - 준비 완료
- [x] v0.1: Config file support
- [x] v0.1: Streaming output
- [x] v0.1: Log preprocessing
- [x] v0.1: Multiple output formats
- [ ] v0.2: 배치 분석 (여러 파일)
- [ ] v0.2: 커스텀 프롬프트
- [ ] v0.3: 웹 UI
- [ ] v0.3: 히스토리 관리

## 📝 Examples

### 샘플 로그 분석

```bash
bifrost local examples/sample.log
```

### Kubernetes 로그

```bash
kubectl logs -f deployment/my-app | bifrost local --stream
```

### Docker 컨테이너 로그

```bash
docker logs my-container 2>&1 | bifrost cloud
```

### CI/CD 파이프라인

```bash
# JSON 출력으로 파싱 가능
bifrost local build.log --format json | jq '.response'
```

## 🔧 개발

```bash
# 개발 모드 설치
pip install -e .

# 의존성 설치
pip install -r requirements.txt
```

---

**Built with 🔨 by vibe coding**
