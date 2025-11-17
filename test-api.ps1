# Heimdall API 테스트 스크립트
# Heimdall이 실행 중일 때 이 스크립트로 API를 테스트할 수 있습니다

Write-Host "🧪 Heimdall API 테스트 시작" -ForegroundColor Cyan
Write-Host ""

$BaseUrl = "http://localhost:8080/api/v1"
$TestsPassed = 0
$TestsFailed = 0

# 테스트 헬퍼 함수
function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [object]$Body = $null
    )
    
    Write-Host "🔍 테스트: $Name" -ForegroundColor Yellow
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            TimeoutSec = 10
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json)
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-RestMethod @params
        Write-Host "✅ 성공" -ForegroundColor Green
        Write-Host "   응답: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
        Write-Host ""
        $script:TestsPassed++
        return $response
    }
    catch {
        Write-Host "❌ 실패: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        $script:TestsFailed++
        return $null
    }
}

# 1. Heimdall 실행 여부 확인
Write-Host "📡 Heimdall 연결 확인 중..." -ForegroundColor Yellow
try {
    $null = Test-NetConnection -ComputerName localhost -Port 8080 -InformationLevel Quiet -WarningAction SilentlyContinue
    Write-Host "✅ Heimdall이 8080 포트에서 실행 중입니다" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Heimdall이 실행되지 않았습니다!" -ForegroundColor Red
    Write-Host "   다음 명령어로 실행하세요:" -ForegroundColor Yellow
    Write-Host "   cd heimdall" -ForegroundColor White
    Write-Host "   .\gradlew.bat bootRun" -ForegroundColor White
    Write-Host ""
    exit 1
}

# 대기 시간
Start-Sleep -Seconds 2

# 2. 헬스 체크
Test-Endpoint -Name "헬스 체크" -Url "$BaseUrl/health"

# 3. Echo API 테스트
$echoPayload = @{
    message = "Hello from PowerShell"
    timestamp = Get-Date -Format "o"
    test = $true
}
Test-Endpoint -Name "Echo API" -Url "$BaseUrl/echo" -Method "POST" -Body $echoPayload

# 4. CPU 스트레스 테스트 (가벼운 부하)
Write-Host "⚡ CPU 스트레스 테스트 (가벼운 부하)" -ForegroundColor Yellow
$cpuResult = Test-Endpoint -Name "CPU 스트레스 (10 iterations)" -Url "$BaseUrl/stress/cpu?iterations=10"
if ($cpuResult) {
    Write-Host "   처리 시간: $($cpuResult.duration_ms)ms" -ForegroundColor Gray
}

# 5. CPU 스트레스 테스트 (중간 부하)
Write-Host "⚡ CPU 스트레스 테스트 (중간 부하)" -ForegroundColor Yellow
$cpuResult = Test-Endpoint -Name "CPU 스트레스 (50 iterations)" -Url "$BaseUrl/stress/cpu?iterations=50"
if ($cpuResult) {
    Write-Host "   처리 시간: $($cpuResult.duration_ms)ms" -ForegroundColor Gray
}

# 6. 메모리 스트레스 테스트
Write-Host "💾 메모리 스트레스 테스트" -ForegroundColor Yellow
$memResult = Test-Endpoint -Name "메모리 스트레스 (500x500)" -Url "$BaseUrl/stress/memory?arraySize=500"
if ($memResult) {
    Write-Host "   메모리 사용: $($memResult.memoryUsed_mb)MB" -ForegroundColor Gray
    Write-Host "   처리 시간: $($memResult.duration_ms)ms" -ForegroundColor Gray
}

# 7. 지연 테스트
Write-Host "⏱️  지연 테스트" -ForegroundColor Yellow
$delayResult = Test-Endpoint -Name "500ms 지연" -Url "$BaseUrl/delay?milliseconds=500"
if ($delayResult) {
    Write-Host "   요청 지연: $($delayResult.requested_delay_ms)ms" -ForegroundColor Gray
    Write-Host "   실제 지연: $($delayResult.actual_delay_ms)ms" -ForegroundColor Gray
}

# 8. 랜덤 에러 테스트 (낮은 확률)
Write-Host "🎲 랜덤 에러 테스트" -ForegroundColor Yellow
Test-Endpoint -Name "랜덤 에러 (10% 확률)" -Url "$BaseUrl/random-error?errorRate=10"

# 9. 연속 요청 테스트 (부하 시뮬레이션)
Write-Host "🔄 연속 요청 테스트 (20회)" -ForegroundColor Yellow
$successCount = 0
$failCount = 0
$totalTime = 0

for ($i = 1; $i -le 20; $i++) {
    try {
        $start = Get-Date
        $result = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get -TimeoutSec 5
        $duration = ((Get-Date) - $start).TotalMilliseconds
        $totalTime += $duration
        $successCount++
        Write-Host "." -NoNewline -ForegroundColor Green
    }
    catch {
        $failCount++
        Write-Host "X" -NoNewline -ForegroundColor Red
    }
}
Write-Host ""
Write-Host "✅ 성공: $successCount / 20" -ForegroundColor Green
Write-Host "❌ 실패: $failCount / 20" -ForegroundColor Red
Write-Host "⏱️  평균 응답시간: $([math]::Round($totalTime / 20, 2))ms" -ForegroundColor Cyan
Write-Host ""

# 10. 동시 요청 테스트 (병렬)
Write-Host "🚀 동시 요청 테스트 (10개 병렬)" -ForegroundColor Yellow
$jobs = @()
for ($i = 1; $i -le 10; $i++) {
    $jobs += Start-Job -ScriptBlock {
        param($url)
        $start = Get-Date
        try {
            $result = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 5
            $duration = ((Get-Date) - $start).TotalMilliseconds
            return @{
                Success = $true
                Duration = $duration
            }
        }
        catch {
            return @{
                Success = $false
                Error = $_.Exception.Message
            }
        }
    } -ArgumentList "$BaseUrl/health"
}

Write-Host "대기 중..." -ForegroundColor Gray
$results = $jobs | Wait-Job | Receive-Job
$jobs | Remove-Job

$parallelSuccess = ($results | Where-Object { $_.Success }).Count
$parallelAvgTime = ($results | Where-Object { $_.Success } | Measure-Object -Property Duration -Average).Average

Write-Host "✅ 성공: $parallelSuccess / 10" -ForegroundColor Green
Write-Host "⏱️  평균 응답시간: $([math]::Round($parallelAvgTime, 2))ms" -ForegroundColor Cyan
Write-Host ""

# 최종 리포트
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "📊 테스트 결과 요약" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ 성공한 테스트: $TestsPassed" -ForegroundColor Green
Write-Host "❌ 실패한 테스트: $TestsFailed" -ForegroundColor Red
Write-Host "📈 성공률: $([math]::Round(($TestsPassed / ($TestsPassed + $TestsFailed)) * 100, 2))%" -ForegroundColor Cyan
Write-Host ""

if ($TestsFailed -eq 0) {
    Write-Host "🎉 모든 테스트가 성공했습니다!" -ForegroundColor Green
} else {
    Write-Host "⚠️  일부 테스트가 실패했습니다" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "💡 다음 단계:" -ForegroundColor Yellow
Write-Host "   1. K6 설치: winget install k6 --source winget" -ForegroundColor White
Write-Host "   2. 스트레스 테스트: k6 run heimdall\src\test\k6\stress-test.js" -ForegroundColor White
Write-Host "   3. 모니터링: http://localhost:9090 (Prometheus)" -ForegroundColor White
Write-Host "   4. 대시보드: http://localhost:3000 (Grafana)" -ForegroundColor White
Write-Host ""
