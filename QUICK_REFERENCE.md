> **HISTORICAL / NON-AUTHORITATIVE** — This document predates the Asgard v1.0 Proof freeze and is kept for context only. Its statements about status, readiness, scope, or roadmap are not accepted claims. Current state, accepted evidence, and the work-item lifecycle are defined in [`ASGARD_MASTER.md`](ASGARD_MASTER.md).

# Asgard Quick Reference

## 🚀 Quick Commands

### 🎯 Unified Scripts (Recommended)

```powershell
# BUILD all services (Java + Python + Frontend)
.\build-all.ps1                    # Build everything
.\build-all.ps1 -SkipTests         # Skip tests
.\build-all.ps1 -SkipFrontend      # Skip frontend build
.\build-all.ps1 -Clean             # Clean build

# TEST all services
.\test-all.ps1                     # Run all tests
.\test-all.ps1 -Coverage           # With coverage reports
.\test-all.ps1 -Service heimdall   # Test specific service
.\test-all.ps1 -SkipIntegration    # Skip integration tests

# START all services (Infrastructure + Apps)
.\start-all.ps1                    # Start everything
.\start-all.ps1 -BuildFirst        # Build before starting
.\start-all.ps1 -ServicesOnly      # Skip frontend
.\start-all.ps1 -FrontendOnly      # Only frontend

# STOP all services
.\stop-all.ps1                     # Stop everything
.\stop-all.ps1 -RemoveVolumes      # Remove data volumes
.\stop-all.ps1 -Force              # Force kill processes
```

### Infrastructure
```powershell
# Start infrastructure only (Docker Compose)
.\start-dev.ps1
# OR
docker-compose up -d

# Start infrastructure only (Docker Compose)
.\start-dev.ps1

# Stop infrastructure
.\stop-dev.ps1
# OR
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f kafka
```

### Gradle (Manual Control)
```powershell
# Build everything
./gradlew build

# Build without tests
./gradlew build -x test

# Build specific module
./gradlew :heimdall:build

# Clean build
./gradlew clean build

# Run tests
./gradlew test

# Run Heimdall
./gradlew :heimdall:bootRun

# Create bootJar
./gradlew :heimdall:bootJar

# List all tasks
./gradlew tasks

# Dependency tree
./gradlew :heimdall:dependencies
```

### Python (Bifrost - Manual Control)
```powershell
cd bifrost

# Create virtual environment (first time)
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run Bifrost
python -m bifrost.main

# Run tests
pytest tests/ -v
pytest tests/ --cov=bifrost --cov-report=html
```

### Frontend (React - Manual Control)
```powershell
cd bifrost\frontend

# Install dependencies
npm install

# Development server
npm run dev

# Build production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🌐 Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **Applications** | | |
| Heimdall API | http://localhost:8080 | - |
| Bifrost API | http://localhost:8000 | - |
| Frontend Dashboard | http://localhost:5173 | - |
| **Infrastructure** | | |
| Kafka UI | http://localhost:8090 | - |
| Redis Commander | http://localhost:8081 | - |
| **Monitoring** | | |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |
| Zipkin | http://localhost:9411 | - |

## 🔌 Connection Strings

### PostgreSQL
```
Host: localhost
Port: 5432
Database: heimdall
Username: asgard
Password: asgard_password

JDBC: jdbc:postgresql://localhost:5432/heimdall
```

### Redis
```
Host: localhost
Port: 6379
Password: redis_password

URL: redis://:redis_password@localhost:6379
```

### Kafka
```
Bootstrap Servers: localhost:9092
Group ID: asgard-consumer-group
```

## 📁 Important Files

| File | Purpose |
|------|---------|
| `settings.gradle` | Module definitions |
| `build.gradle` | Common configuration |
| `heimdall/build.gradle` | Module-specific config |
| `docker-compose.yml` | Infrastructure services |
| `.env.example` | Environment template |
| `monitoring/prometheus.yml` | Metrics configuration |

## 🛠️ Troubleshooting

### Gradle Issues
```powershell
# Stop Gradle daemon
./gradlew --stop

# Refresh dependencies
./gradlew --refresh-dependencies

# Clear Gradle cache
Remove-Item -Recurse -Force ~/.gradle/caches/
```

### Docker Issues
```powershell
# Remove all containers and volumes
docker-compose down -v

# Restart Docker Desktop
# (Right-click Docker Desktop icon → Restart)

# Check Docker status
docker info

# Prune unused resources
docker system prune -a
```

### Port Conflicts
```powershell
# Find process using port (e.g., 8080)
netstat -ano | findstr :8080

# Kill process by PID
taskkill /PID <PID> /F
```

## 📊 Monitoring

### Check Service Health
```powershell
# All services
docker-compose ps

# Specific service health
docker-compose exec postgres pg_isready -U asgard
docker-compose exec redis redis-cli -a redis_password ping
docker-compose exec kafka kafka-broker-api-versions --bootstrap-server kafka:29092
```

### View Metrics
- Prometheus targets: http://localhost:9090/targets
- Heimdall metrics: http://localhost:8080/actuator/prometheus
- Heimdall health: http://localhost:8080/actuator/health

## 🧪 Testing

```powershell
# Run all tests
./gradlew test

# Run tests for specific module
./gradlew :heimdall:test

# Run tests with coverage
./gradlew test jacocoTestReport

# Run integration tests (if configured)
./gradlew integrationTest
```

## 📦 Building for Production

```powershell
# Create production JAR
./gradlew :heimdall:bootJar

# JAR location
# heimdall/build/libs/heimdall-1.0.0.jar

# Run JAR
java -jar heimdall/build/libs/heimdall-1.0.0.jar

# Build Docker image
cd heimdall
docker build -t asgard/heimdall:1.0.0 .
```

## 🔄 Git Workflow

```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit: Gradle multi-module setup"

# Create feature branch
git checkout -b feature/my-feature

# Commit changes
git add .
git commit -m "Add feature"

# Push to remote
git push origin feature/my-feature
```

## 📚 Documentation

- Main README: `README.md`
- Configuration Summary: `CONFIGURATION_SUMMARY.md`
- Implementation Status: `IMPLEMENTATION_STATUS.md`
- Heimdall Docs: `heimdall/docs/`
- Bifrost Docs: `bifrost/docs/`

---

## 🔌 Bifrost API 엔드포인트 (v0.3.0)

### 🔄 Circuit Breaker
```bash
# 모든 Circuit Breaker 상태 조회
curl http://localhost:8000/api/v1/circuit-breakers

# 특정 CB 조회
curl http://localhost:8000/api/v1/circuit-breakers/{name}

# CB 리셋
curl -X POST http://localhost:8000/api/v1/circuit-breakers/{name}/reset
```

### 💬 피드백 시스템
```bash
# 피드백 제출
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{"request_id": "req-123", "feedback_type": "thumbs_up", "rating": 5}'

# 빠른 피드백 (좋아요/싫어요)
curl -X POST http://localhost:8000/api/v1/feedback/quick \
  -d '{"request_id": "req-123", "is_positive": true}'

# 피드백 통계
curl http://localhost:8000/api/v1/feedback/stats
```

### 🔀 멀티 LLM 라우팅
```bash
# 라우팅 결정 요청
curl -X POST http://localhost:8000/api/v1/routing/decide \
  -H "Content-Type: application/json" \
  -d '{"input_text": "What is the error?", "strategy": "cost_optimized"}'

# 제공자 목록
curl http://localhost:8000/api/v1/routing/providers

# 라우팅 통계
curl http://localhost:8000/api/v1/routing/metrics
```

### 📊 품질 지표 시스템
```bash
# 품질 분석 실행
curl -X POST http://localhost:8000/api/v1/quality/analyze \
  -H "Content-Type: application/json" \
  -d '{"request_id": "req-123", "query": "What is error?", "response": "The error is..."}'

# 품질 통계
curl http://localhost:8000/api/v1/quality/stats

# 품질 트렌드
curl http://localhost:8000/api/v1/quality/trends
```

### 🧪 A/B 테스팅
```bash
# 실험 생성
curl -X POST http://localhost:8000/api/v1/experiments \
  -H "Content-Type: application/json" \
  -d '{"name": "llm-compare", "variants": [{"name": "control", "type": "control"}, {"name": "treatment", "type": "treatment"}]}'

# 실험 시작
curl -X POST http://localhost:8000/api/v1/experiments/{id}/start

# 변형 할당
curl -X POST http://localhost:8000/api/v1/experiments/assign \
  -d '{"experiment_id": "exp-123", "request_id": "req-456"}'

# 결과 분석
curl http://localhost:8000/api/v1/experiments/{id}/results
```

### 💾 스마트 캐싱
```bash
# 캐시에 저장
curl -X POST http://localhost:8000/api/v1/cache/put \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the error?", "response": "The error is a timeout."}'

# 캐시 조회 (시맨틱 매칭 포함)
curl -X POST http://localhost:8000/api/v1/cache/lookup \
  -d '{"query": "What is the problem?", "use_semantic": true}'

# 캐시 통계
curl http://localhost:8000/api/v1/cache/stats

# 만료 항목 정리
curl -X POST http://localhost:8000/api/v1/cache/cleanup
```

---

## 💡 Tips

1. **Always start infrastructure first**: Run `./start-dev.ps1` before starting applications
2. **Check service health**: Use `docker-compose ps` to ensure all services are running
3. **Use Gradle daemon**: Significantly speeds up builds (enabled by default)
4. **Monitor logs**: Keep an eye on `docker-compose logs -f` for issues
5. **Clean build**: If weird issues occur, try `./gradlew clean build`
