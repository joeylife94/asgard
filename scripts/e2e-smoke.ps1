param(
    [int]$MaxWaitSeconds = 90,
    [int]$PollSeconds = 2
)

$ErrorActionPreference = "Stop"

function Wait-HttpOk {
    param(
        [string]$Url,
        [int]$TimeoutSeconds
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) {
                return
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    throw "Timed out waiting for $Url"
}

Write-Host "\n============================================================" -ForegroundColor Cyan
Write-Host " Asgard E2E Smoke (Kafka control plane)" -ForegroundColor Cyan
Write-Host "============================================================\n" -ForegroundColor Cyan

Write-Host "[1/4] Starting infra + services via docker-compose..." -ForegroundColor Yellow
Set-Location (Split-Path $PSScriptRoot -Parent)

docker-compose -f docker-compose.yml -f docker-compose.e2e.yml up -d --build
if ($LASTEXITCODE -ne 0) { throw "docker-compose up failed" }

Write-Host "[2/4] Waiting for Heimdall/Bifrost to become reachable..." -ForegroundColor Yellow
Wait-HttpOk -Url "http://localhost:8080/actuator/health" -TimeoutSeconds $MaxWaitSeconds
Wait-HttpOk -Url "http://localhost:8001/health" -TimeoutSeconds $MaxWaitSeconds

Write-Host "[3/4] Authenticating to Heimdall..." -ForegroundColor Yellow
$loginBody = @{ username = "admin"; password = "admin123" } | ConvertTo-Json
$loginResp = Invoke-RestMethod -Method Post -Uri "http://localhost:8080/api/v1/auth/login" -ContentType "application/json" -Body $loginBody
if (-not $loginResp.token) { throw "Login succeeded but token missing" }
$token = $loginResp.token

Write-Host "[4/4] Ingest log -> request analysis -> poll job status..." -ForegroundColor Yellow

$logBody = @{
    source = "e2e"
    serviceName = "e2e-service"
    environment = "test"
    severity = "ERROR"
    logContent = "[ERROR] 2026-01-05 E2E smoke test: database connection timeout\njava.sql.SQLTransientConnectionException: HikariPool-1 - Connection is not available"
    metadata = @{ scenario = "e2e-smoke"; runAt = (Get-Date).ToString("o") }
} | ConvertTo-Json -Depth 5

$ingestHeaders = @{ Authorization = "Bearer $token"; "X-API-Key" = "e2e" }
$ingestResp = Invoke-RestMethod -Method Post -Uri "http://localhost:8080/api/v1/logs" -ContentType "application/json" -Headers $ingestHeaders -Body $logBody
if (-not $ingestResp.logId) { throw "Log ingestion response missing logId" }
$logId = [int64]$ingestResp.logId

$analysisHeaders = @{ Authorization = "Bearer $token"; "Idempotency-Key" = "e2e-idem-$logId"; "X-API-Key" = "e2e" }
$analysisResp = Invoke-RestMethod -Method Post -Uri "http://localhost:8080/api/v1/logs/$logId/analysis" -ContentType "application/json" -Headers $analysisHeaders -Body "{}"
if (-not $analysisResp.jobId) { throw "Analysis request missing jobId" }
$jobId = $analysisResp.jobId

$deadline = (Get-Date).AddSeconds($MaxWaitSeconds)
while ((Get-Date) -lt $deadline) {
    $job = Invoke-RestMethod -Method Get -Uri "http://localhost:8080/api/v1/analysis/jobs/$jobId" -Headers @{ Authorization = "Bearer $token"; "X-API-Key" = "e2e" }

    $status = $job.status
    if ($status -in @("SUCCEEDED", "FAILED")) {
        Write-Host "\nJob status: $status" -ForegroundColor Cyan
        if ($status -eq "FAILED") {
            $job | ConvertTo-Json -Depth 10 | Write-Host
            throw "E2E job failed"
        }

        Write-Host "\n✅ E2E smoke passed (job succeeded)." -ForegroundColor Green
        exit 0
    }

    Start-Sleep -Seconds $PollSeconds
}

throw "Timed out waiting for job completion: $jobId"