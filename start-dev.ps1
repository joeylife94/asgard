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

# Display service URLs
Write-Host ""
Write-Host "✅ Infrastructure setup complete!" -ForegroundColor Green
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
Write-Host "🚀 Next Steps - Choose your workflow:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Option 1: Quick Start (Recommended)" -ForegroundColor Cyan
Write-Host "    .\start-all.ps1            # Starts everything (Heimdall + Bifrost + Frontend)" -ForegroundColor White
Write-Host ""
Write-Host "  Option 2: Manual Control" -ForegroundColor Cyan
Write-Host "    .\build-all.ps1            # Build all services" -ForegroundColor White
Write-Host "    .\gradlew :heimdall:bootRun  # Start Heimdall" -ForegroundColor White
Write-Host "    cd bifrost; python -m bifrost.main  # Start Bifrost" -ForegroundColor White
Write-Host "    cd bifrost\frontend; npm run dev    # Start Frontend" -ForegroundColor White
Write-Host ""
Write-Host "  Option 3: Testing" -ForegroundColor Cyan
Write-Host "    .\test-all.ps1             # Run all tests" -ForegroundColor White
Write-Host "    .\test-all.ps1 -Coverage   # Run tests with coverage" -ForegroundColor White
Write-Host ""
Write-Host "📚 For more information, see README.md" -ForegroundColor Yellow
