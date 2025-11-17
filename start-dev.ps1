# Asgard Local Development Setup Script
# PowerShell script to start infrastructure and build services

Write-Host "🚀 Starting Asgard Local Development Environment" -ForegroundColor Cyan
Write-Host ""

# Check Docker is running
Write-Host "📦 Checking Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Start infrastructure services
Write-Host ""
Write-Host "🐳 Starting infrastructure services (Kafka, Redis, PostgreSQL, etc.)..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to be ready
Write-Host ""
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service health
Write-Host ""
Write-Host "🔍 Checking service health..." -ForegroundColor Yellow
docker-compose ps

# Build Gradle projects
Write-Host ""
Write-Host "🏗️  Building Gradle modules..." -ForegroundColor Yellow
./gradlew clean build -x test

# Display service URLs
Write-Host ""
Write-Host "✅ Setup complete! Services are available at:" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Infrastructure Services:" -ForegroundColor Cyan
Write-Host "  • Kafka UI:          http://localhost:8090" -ForegroundColor White
Write-Host "  • Redis Commander:   http://localhost:8081" -ForegroundColor White
Write-Host "  • PostgreSQL:        localhost:5432" -ForegroundColor White
Write-Host "  • Redis:             localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "📈 Monitoring Stack:" -ForegroundColor Cyan
Write-Host "  • Prometheus:        http://localhost:9090" -ForegroundColor White
Write-Host "  • Grafana:           http://localhost:3000 (admin/admin)" -ForegroundColor White
Write-Host "  • Zipkin:            http://localhost:9411" -ForegroundColor White
Write-Host ""
Write-Host "🚀 To start services:" -ForegroundColor Yellow
Write-Host "  • Heimdall:  ./gradlew :heimdall:bootRun" -ForegroundColor White
Write-Host "  • Bifrost:   cd bifrost; python -m bifrost.main" -ForegroundColor White
Write-Host ""
Write-Host "📚 For more information, see README.md" -ForegroundColor Yellow
