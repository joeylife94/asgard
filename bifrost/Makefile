"""Makefile - 개발 편의성"""

# ==================== 변수 ====================
.PHONY: help install dev test lint format clean docker run migrate db-init

PYTHON := python3
PIP := pip3
DOCKER := docker
DOCKER_COMPOSE := docker-compose

# ==================== 기본 명령어 ====================
help: ## 도움말 표시
	@echo "Bifrost - MLOps Log Analyzer"
	@echo ""
	@echo "사용 가능한 명령어:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ==================== 설치 & 환경 ====================
install: ## 프로덕션 의존성 설치
	$(PIP) install -r requirements.txt

dev: ## 개발 의존성 설치
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-asyncio pytest-cov black flake8 mypy

venv: ## 가상환경 생성
	$(PYTHON) -m venv venv
	@echo "Run: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"

# ==================== 테스트 & 검증 ====================
test: ## 테스트 실행
	pytest tests/ -v

test-cov: ## 테스트 + 커버리지
	pytest tests/ --cov=bifrost --cov-report=html --cov-report=term

lint: ## 코드 린트 (flake8)
	flake8 bifrost/ --max-line-length=120 --ignore=E501,W503

format: ## 코드 포맷 (black)
	black bifrost/ tests/

typecheck: ## 타입 체크 (mypy)
	mypy bifrost/ --ignore-missing-imports

check: lint typecheck test ## 전체 검증 (lint + typecheck + test)

# ==================== 실행 ====================
run-cli: ## CLI 실행 (로컬 모드)
	$(PYTHON) -m bifrost.main local --help

run-api: ## API 서버 실행
	uvicorn bifrost.api:app --reload --host 0.0.0.0 --port 8000

run-batch: ## 배치 분석 (예시)
	$(PYTHON) -m bifrost.main batch logs/*.log

# ==================== Docker ====================
docker-build: ## Docker 이미지 빌드
	$(DOCKER) build -t bifrost:latest .

docker-run: ## Docker 컨테이너 실행
	$(DOCKER) run -p 8000:8000 bifrost:latest

docker-up: ## docker-compose 시작
	$(DOCKER_COMPOSE) up -d

docker-down: ## docker-compose 중지
	$(DOCKER_COMPOSE) down

docker-logs: ## docker-compose 로그
	$(DOCKER_COMPOSE) logs -f

docker-clean: ## Docker 리소스 정리
	$(DOCKER_COMPOSE) down -v
	$(DOCKER) system prune -f

# ==================== 데이터베이스 ====================
db-init: ## DB 초기화
	$(PYTHON) -c "from bifrost.database import Database; from bifrost.models import Base; from bifrost.config import Config; db = Database(Config().get('database.url', 'sqlite:///bifrost.db')); Base.metadata.create_all(db.engine)"

db-migrate: ## DB 마이그레이션 (Alembic - 향후)
	@echo "Alembic migration not yet implemented"

db-seed: ## 샘플 데이터 삽입
	$(PYTHON) scripts/seed_data.py

# ==================== 모니터링 ====================
metrics: ## Prometheus 메트릭 확인
	@curl -s http://localhost:8000/metrics/prometheus || echo "API가 실행 중이 아닙니다"

grafana: ## Grafana 대시보드 열기
	@echo "Opening Grafana at http://localhost:3001"
	@open http://localhost:3001 || xdg-open http://localhost:3001 || start http://localhost:3001

prometheus: ## Prometheus UI 열기
	@echo "Opening Prometheus at http://localhost:9090"
	@open http://localhost:9090 || xdg-open http://localhost:9090 || start http://localhost:9090

# ==================== 정리 ====================
clean: ## 캐시 파일 정리
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov/ dist/ build/

clean-cache: ## 분석 캐시 정리
	rm -rf .cache/

clean-all: clean clean-cache docker-clean ## 모든 것 정리

# ==================== 배포 ====================
deploy-k8s: ## Kubernetes 배포
	kubectl apply -f k8s/config.yaml
	kubectl apply -f k8s/deployment.yaml

deploy-rollback: ## Kubernetes 롤백
	kubectl rollout undo deployment/bifrost

deploy-status: ## Kubernetes 배포 상태
	kubectl rollout status deployment/bifrost

# ==================== CI/CD ====================
ci: check ## CI 파이프라인 시뮬레이션
	@echo "✅ CI 파이프라인 완료"

release: ## GitHub Release 태그
	@echo "Current version: 0.2.0"
	@read -p "Enter new version: " version; \
	git tag -a v$$version -m "Release v$$version"; \
	git push origin v$$version

# ==================== 문서 ====================
docs: ## 문서 생성 (향후)
	@echo "Documentation generation not yet implemented"

api-docs: ## API 문서 열기
	@echo "Opening API docs at http://localhost:8000/docs"
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs || start http://localhost:8000/docs

# ==================== 개발 워크플로우 ====================
dev-setup: venv install dev db-init ## 개발 환경 완전 설정
	@echo "✅ 개발 환경 설정 완료!"
	@echo "다음 명령어를 실행하세요:"
	@echo "  1. source venv/bin/activate (가상환경 활성화)"
	@echo "  2. make run-api (API 서버 시작)"

quick-start: docker-up ## 빠른 시작 (Docker)
	@echo "✅ Bifrost 시작 완료!"
	@echo "  - API: http://localhost:8000/docs"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "  - Grafana: http://localhost:3001 (admin/admin)"
