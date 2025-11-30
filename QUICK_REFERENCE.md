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
- Heimdall Docs: `heimdall/docs/`
- Bifrost Docs: `bifrost/docs/`

## 💡 Tips

1. **Always start infrastructure first**: Run `./start-dev.ps1` before starting applications
2. **Check service health**: Use `docker-compose ps` to ensure all services are running
3. **Use Gradle daemon**: Significantly speeds up builds (enabled by default)
4. **Monitor logs**: Keep an eye on `docker-compose logs -f` for issues
5. **Clean build**: If weird issues occur, try `./gradlew clean build`
