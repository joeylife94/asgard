# Asgard Complete Environment Start Script
# Starts all services: Infrastructure + Heimdall + Bifrost + Frontend

param(
    [switch]$BuildFirst,
    [switch]$SkipBuild,
    [switch]$FrontendOnly,
    [switch]$ServicesOnly
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    🚀 Asgard Complete Environment Startup                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ═══════════════════════════════════════════════════════════
# PRE-BUILD (Optional)
# ═══════════════════════════════════════════════════════════

if ($BuildFirst -and -not $SkipBuild) {
    Write-Host "🏗️  Building all services first..." -ForegroundColor Yellow
    Write-Host ""
    
    & ".\build-all.ps1" -SkipTests
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build failed. Cannot start services." -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "✅ Build completed. Starting services..." -ForegroundColor Green
    Write-Host ""
    Start-Sleep -Seconds 2
}

# ═══════════════════════════════════════════════════════════
# 1️⃣  CHECK DOCKER
# ═══════════════════════════════════════════════════════════

Write-Host "📦 Checking Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# ═══════════════════════════════════════════════════════════
# 2️⃣  START INFRASTRUCTURE (Docker Compose)
# ═══════════════════════════════════════════════════════════

Write-Host ""
Write-Host "🐳 Starting infrastructure services..." -ForegroundColor Yellow
Write-Host "   • PostgreSQL, Redis, Kafka, Elasticsearch, Prometheus, Grafana, Zipkin" -ForegroundColor Gray
Write-Host ""

docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start infrastructure services" -ForegroundColor Red
    exit 1
}

# Wait for services
Write-Host ""
Write-Host "⏳ Waiting for services to be ready (15 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check health
Write-Host ""
Write-Host "🔍 Service Status:" -ForegroundColor Yellow
docker-compose ps
Write-Host ""

# ═══════════════════════════════════════════════════════════
# 3️⃣  START HEIMDALL (Background)
# ═══════════════════════════════════════════════════════════

if (-not $FrontendOnly) {
    Write-Host ""
    Write-Host "🛡️  Starting Heimdall (API Gateway)..." -ForegroundColor Cyan
    
    # Check if JAR exists
    $jarFile = Get-Item "heimdall\build\libs\heimdall-*.jar" -ErrorAction SilentlyContinue | Select-Object -First 1
    
    if (-not $jarFile) {
        Write-Host "   ⚠️  JAR file not found. Building Heimdall..." -ForegroundColor Yellow
        & ".\gradlew.bat" ":heimdall:bootJar" -q
        $jarFile = Get-Item "heimdall\build\libs\heimdall-*.jar" -ErrorAction SilentlyContinue | Select-Object -First 1
    }
    
    if ($jarFile) {
        Write-Host "   📦 Using: $($jarFile.Name)" -ForegroundColor Gray
        Write-Host "   🚀 Starting in background..." -ForegroundColor Gray
        
        # Start in new window
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { Write-Host '🛡️  Heimdall (API Gateway)' -ForegroundColor Cyan; java -jar '$($jarFile.FullName)' }"
        
        Write-Host "   ✅ Heimdall starting... (http://localhost:8080)" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ Failed to build Heimdall" -ForegroundColor Red
    }
}

# ═══════════════════════════════════════════════════════════
# 4️⃣  START BIFROST (Background)
# ═══════════════════════════════════════════════════════════

if (-not $FrontendOnly) {
    Write-Host ""
    Write-Host "🌉 Starting Bifrost (ML/AI Service)..." -ForegroundColor Cyan
    
    # Check virtual environment
    if (Test-Path "bifrost\.venv\Scripts\Activate.ps1") {
        Write-Host "   🐍 Using virtual environment" -ForegroundColor Gray
        Write-Host "   🚀 Starting in background..." -ForegroundColor Gray
        
        # Start in new window
        $bifrostCmd = "cd bifrost; .\.venv\Scripts\Activate.ps1; python -m bifrost.main"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { Write-Host '🌉 Bifrost (ML/AI Service)' -ForegroundColor Cyan; $bifrostCmd }"
        
        Write-Host "   ✅ Bifrost starting... (http://localhost:8000)" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️  Virtual environment not found. Run 'build-all.ps1' first." -ForegroundColor Yellow
    }
}

# ═══════════════════════════════════════════════════════════
# 5️⃣  START FRONTEND (Background)
# ═══════════════════════════════════════════════════════════

if (-not $ServicesOnly) {
    Write-Host ""
    Write-Host "⚛️  Starting Frontend (React Dashboard)..." -ForegroundColor Cyan
    
    if (Test-Path "bifrost\frontend\package.json") {
        Write-Host "   📦 Using npm dev server" -ForegroundColor Gray
        Write-Host "   🚀 Starting in background..." -ForegroundColor Gray
        
        # Start in new window
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { Write-Host '⚛️  Frontend Dashboard' -ForegroundColor Cyan; cd bifrost\frontend; npm run dev }"
        
        Write-Host "   ✅ Frontend starting... (http://localhost:5173)" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️  Frontend not found" -ForegroundColor Yellow
    }
}

# ═══════════════════════════════════════════════════════════
# 📊 STARTUP COMPLETE
# ═══════════════════════════════════════════════════════════

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✅ ASGARD STARTUP COMPLETE!                   ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "🌐 Application Services:" -ForegroundColor Cyan
Write-Host "  • Heimdall (API Gateway):      http://localhost:8080" -ForegroundColor White
Write-Host "  • Bifrost (ML/AI Service):     http://localhost:8000" -ForegroundColor White
Write-Host "  • Frontend (Dashboard):        http://localhost:5173" -ForegroundColor White
Write-Host ""

Write-Host "📊 Infrastructure Services:" -ForegroundColor Cyan
Write-Host "  • Kafka UI:                    http://localhost:8090" -ForegroundColor White
Write-Host "  • Redis Commander:             http://localhost:8081" -ForegroundColor White
Write-Host "  • PostgreSQL:                  localhost:5432" -ForegroundColor White
Write-Host ""

Write-Host "📈 Monitoring Stack:" -ForegroundColor Cyan
Write-Host "  • Prometheus:                  http://localhost:9090" -ForegroundColor White
Write-Host "  • Grafana:                     http://localhost:3000 (admin/admin)" -ForegroundColor White
Write-Host "  • Zipkin:                      http://localhost:9411" -ForegroundColor White
Write-Host ""

Write-Host "💡 Quick Commands:" -ForegroundColor Yellow
Write-Host "  • Stop all:        .\stop-all.ps1" -ForegroundColor White
Write-Host "  • Run tests:       .\test-all.ps1" -ForegroundColor White
Write-Host "  • Rebuild:         .\build-all.ps1" -ForegroundColor White
Write-Host "  • Check health:    curl http://localhost:8080/actuator/health" -ForegroundColor White
Write-Host ""

Write-Host "📝 Note: Services are starting in background. Check the new terminal windows for logs." -ForegroundColor Gray
Write-Host ""
