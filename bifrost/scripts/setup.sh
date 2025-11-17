#!/bin/bash

# Bifrost 로컬 개발 환경 셋업 스크립트

set -e

echo "🌈 Bifrost 개발 환경 셋업 시작..."

# 1. Python 가상환경 생성
echo "📦 Python 가상환경 생성..."
python -m venv venv

# 2. 가상환경 활성화
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# 3. 의존성 설치
echo "📥 의존성 설치..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 4. 데이터베이스 초기화
echo "🗄️  데이터베이스 초기화..."
python -c "from bifrost.database import get_database; get_database().init_db()"

# 5. 설정 파일 생성
echo "⚙️  설정 파일 생성..."
if [ ! -f "bifrost.yaml" ]; then
    cp bifrost.yaml.example bifrost.yaml
    echo "✅ bifrost.yaml 생성됨 (필요시 수정하세요)"
fi

# 6. Ollama 체크
echo "🔍 Ollama 확인..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama 설치됨"
    echo "📥 Mistral 모델 다운로드..."
    ollama pull mistral
else
    echo "⚠️  Ollama가 설치되지 않았습니다."
    echo "   설치: https://ollama.ai"
fi

echo ""
echo "🎉 셋업 완료!"
echo ""
echo "다음 명령어로 시작하세요:"
echo "  1. CLI 사용:     bifrost local examples/sample.log"
echo "  2. API 서버:     bifrost serve"
echo "  3. Docker 실행:  docker-compose up"
echo ""
