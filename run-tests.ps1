# Asgard 통합 테스트 실행 스크립트
# 모든 테스트를 순차적으로 실행하고 결과를 보고합니다

Write-Host "🧪 Asgard 통합 테스트 시작" -ForegroundColor Cyan
Write-Host ""

$ErrorCount = 0

# 1. 환경 확인
Write-Host "📋 1. 환경 확인 중..." -ForegroundColor Yellow
Write-Host ""

# Java 확인
try {
    $javaVersion = java -version 2>&1 | Select-Object -First 1
    Write-Host "✅ Java: $javaVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Java가 설치되어 있지 않습니다" -ForegroundColor Red
    $ErrorCount++
}

# Docker 확인
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker가 설치되어 있지 않습니다" -ForegroundColor Red
    $ErrorCount++
}

if ($ErrorCount -gt 0) {
    Write-Host ""
    Write-Host "❌ 필수 도구가 설치되어 있지 않습니다. 종료합니다." -ForegroundColor Red
    exit 1
}

Write-Host ""

# 2. 인프라 시작
Write-Host "🐳 2. Docker 인프라 시작 중..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "⏳ 서비스 준비 대기 (30초)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# 서비스 상태 확인
Write-Host ""
Write-Host "📊 서비스 상태:" -ForegroundColor Yellow
docker-compose ps

Write-Host ""

# 3. Unit Tests
Write-Host "🧪 3. Unit Tests 실행 중..." -ForegroundColor Yellow
Write-Host ""

$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.16.8-hotspot"
$env:Path = "$env:JAVA_HOME\bin;" + $env:Path

$unitTestResult = & .\gradlew.bat :heimdall:test -x checkstyleMain -x checkstyleTest

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Unit Tests 통과" -ForegroundColor Green
} else {
    Write-Host "❌ Unit Tests 실패" -ForegroundColor Red
    $ErrorCount++
}

Write-Host ""

# 4. API 헬스 체크
Write-Host "🏥 4. API 헬스 체크..." -ForegroundColor Yellow
Write-Host ""

# Heimdall이 실행 중이지 않다면 알림
Write-Host "⚠️  Heimdall 애플리케이션이 실행되어야 합니다" -ForegroundColor Yellow
Write-Host "   다른 터미널에서 실행: .\gradlew.bat :heimdall:bootRun" -ForegroundColor Yellow
Write-Host ""

$continue = Read-Host "Heimdall이 실행 중입니까? (Y/N)"

if ($continue -eq "Y" -or $continue -eq "y") {
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/health" -Method Get
        Write-Host "✅ 헬스 체크 성공: $($health.status)" -ForegroundColor Green
        Write-Host "   Service: $($health.service)" -ForegroundColor Gray
        Write-Host "   Version: $($health.version)" -ForegroundColor Gray
    } catch {
        Write-Host "❌ 헬스 체크 실패: $_" -ForegroundColor Red
        $ErrorCount++
    }
    
    Write-Host ""
    
    # 5. 기본 API 테스트
    Write-Host "🔍 5. 기본 API 테스트..." -ForegroundColor Yellow
    Write-Host ""
    
    # Echo 테스트
    try {
        $echoPayload = @{
            message = "test"
            timestamp = Get-Date -Format "o"
        } | ConvertTo-Json
        
        $echo = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/echo" -Method Post -Body $echoPayload -ContentType "application/json"
        Write-Host "✅ Echo API 테스트 성공" -ForegroundColor Green
    } catch {
        Write-Host "❌ Echo API 테스트 실패: $_" -ForegroundColor Red
        $ErrorCount++
    }
    
    # CPU 스트레스 테스트
    try {
        $cpu = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/stress/cpu?iterations=10" -Method Get
        Write-Host "✅ CPU 스트레스 테스트 성공 (Duration: $($cpu.duration_ms)ms)" -ForegroundColor Green
    } catch {
        Write-Host "❌ CPU 스트레스 테스트 실패: $_" -ForegroundColor Red
        $ErrorCount++
    }
    
    Write-Host ""
}

# 최종 리포트
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "📊 테스트 결과 요약" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

if ($ErrorCount -eq 0) {
    Write-Host "✅ 모든 테스트 통과!" -ForegroundColor Green
} else {
    Write-Host "❌ $ErrorCount 개의 테스트 실패" -ForegroundColor Red
}

Write-Host ""
Write-Host "📝 상세 리포트:" -ForegroundColor Yellow
Write-Host "   - Unit Test 리포트: heimdall\build\reports\tests\test\index.html"
Write-Host "   - 커버리지 리포트: heimdall\build\reports\jacoco\test\html\index.html"
Write-Host ""

# K6 테스트 안내
Write-Host "💡 성능 테스트를 실행하려면:" -ForegroundColor Yellow
Write-Host "   k6 run heimdall\src\test\k6\stress-test.js" -ForegroundColor White
Write-Host ""

Write-Host "🛑 인프라를 종료하려면:" -ForegroundColor Yellow
Write-Host "   docker-compose down" -ForegroundColor White
Write-Host ""

if ($ErrorCount -eq 0) {
    exit 0
} else {
    exit 1
}
