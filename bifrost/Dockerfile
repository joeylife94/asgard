# ==================== Stage 1: Build ====================
FROM python:3.11-slim as builder

WORKDIR /build

# 의존성 복사
COPY requirements.txt .

# 빌드 의존성 설치
RUN pip install --no-cache-dir --user -r requirements.txt

# ==================== Stage 2: Runtime ====================
FROM python:3.11-slim

WORKDIR /app

# 보안: non-root 유저 생성
RUN groupadd -r bifrost && useradd -r -g bifrost bifrost

# Python 패키지 복사 (builder에서)
COPY --from=builder /root/.local /home/bifrost/.local

# 앱 코드 복사
COPY bifrost/ ./bifrost/
COPY setup.py .
COPY README.md .

# 환경변수 설정
ENV PATH=/home/bifrost/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 권한 설정
RUN chown -R bifrost:bifrost /app

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 유저 전환
USER bifrost

# 포트 노출
EXPOSE 8000

# 엔트리포인트
CMD ["python", "-m", "uvicorn", "bifrost.api:app", "--host", "0.0.0.0", "--port", "8000"]
