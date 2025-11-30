# Asgard Complete Environment Stop Script
# Stops all services: Infrastructure + Heimdall + Bifrost + Frontend

param(
    [switch]$RemoveVolumes,
    [switch]$Force
)

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      🛑 Asgard Complete Environment Shutdown               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ═══════════════════════════════════════════════════════════
# 1️⃣  STOP JAVA PROCESSES (Heimdall)
# ═══════════════════════════════════════════════════════════

Write-Host "🛡️  Stopping Heimdall processes..." -ForegroundColor Yellow

$heimdallProcesses = Get-Process -Name "java" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*heimdall*"
}

if ($heimdallProcesses) {
    foreach ($process in $heimdallProcesses) {
        Write-Host "   Stopping PID: $($process.Id)" -ForegroundColor Gray
        if ($Force) {
            Stop-Process -Id $process.Id -Force
        }
        else {
            Stop-Process -Id $process.Id
        }
    }
    Write-Host "✅ Heimdall stopped" -ForegroundColor Green
}
else {
    Write-Host "   ℹ️  No Heimdall processes found" -ForegroundColor Gray
}

# ═══════════════════════════════════════════════════════════
# 2️⃣  STOP PYTHON PROCESSES (Bifrost)
# ═══════════════════════════════════════════════════════════

Write-Host ""
Write-Host "🌉 Stopping Bifrost processes..." -ForegroundColor Yellow

$bifrostProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*bifrost*"
}

if ($bifrostProcesses) {
    foreach ($process in $bifrostProcesses) {
        Write-Host "   Stopping PID: $($process.Id)" -ForegroundColor Gray
        if ($Force) {
            Stop-Process -Id $process.Id -Force
        }
        else {
            Stop-Process -Id $process.Id
        }
    }
    Write-Host "✅ Bifrost stopped" -ForegroundColor Green
}
else {
    Write-Host "   ℹ️  No Bifrost processes found" -ForegroundColor Gray
}

# ═══════════════════════════════════════════════════════════
# 3️⃣  STOP NODE PROCESSES (Frontend)
# ═══════════════════════════════════════════════════════════

Write-Host ""
Write-Host "⚛️  Stopping Frontend processes..." -ForegroundColor Yellow

$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*vite*" -or $_.CommandLine -like "*bifrost*"
}

if ($nodeProcesses) {
    foreach ($process in $nodeProcesses) {
        Write-Host "   Stopping PID: $($process.Id)" -ForegroundColor Gray
        if ($Force) {
            Stop-Process -Id $process.Id -Force
        }
        else {
            Stop-Process -Id $process.Id
        }
    }
    Write-Host "✅ Frontend stopped" -ForegroundColor Green
}
else {
    Write-Host "   ℹ️  No Frontend processes found" -ForegroundColor Gray
}

# ═══════════════════════════════════════════════════════════
# 4️⃣  STOP DOCKER CONTAINERS
# ═══════════════════════════════════════════════════════════

Write-Host ""
Write-Host "🐳 Stopping Docker containers..." -ForegroundColor Yellow

if ($RemoveVolumes) {
    Write-Host "   ⚠️  Removing volumes (data will be lost)..." -ForegroundColor Yellow
    docker-compose down -v
}
else {
    docker-compose down
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker containers stopped" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Some containers may not have stopped properly" -ForegroundColor Yellow
}

# ═══════════════════════════════════════════════════════════
# 5️⃣  CLEANUP BACKGROUND POWERSHELL WINDOWS
# ═══════════════════════════════════════════════════════════

Write-Host ""
Write-Host "🧹 Cleaning up background processes..." -ForegroundColor Yellow

# Close PowerShell windows that were started by start-all.ps1
$currentPid = $PID
Get-Process -Name "powershell" -ErrorAction SilentlyContinue | Where-Object {
    $_.Id -ne $currentPid -and $_.MainWindowTitle -match "Heimdall|Bifrost|Frontend"
} | ForEach-Object {
    Write-Host "   Closing window: $($_.MainWindowTitle)" -ForegroundColor Gray
    Stop-Process -Id $_.Id -ErrorAction SilentlyContinue
}

# ═══════════════════════════════════════════════════════════
# 📊 SHUTDOWN COMPLETE
# ═══════════════════════════════════════════════════════════

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✅ ASGARD SHUTDOWN COMPLETE!                  ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

if ($RemoveVolumes) {
    Write-Host "⚠️  All data has been removed (volumes deleted)" -ForegroundColor Yellow
}
else {
    Write-Host "ℹ️  Data preserved in Docker volumes" -ForegroundColor Cyan
    Write-Host "   To remove volumes: .\stop-all.ps1 -RemoveVolumes" -ForegroundColor Gray
}

Write-Host ""
Write-Host "💡 To restart services:" -ForegroundColor Yellow
Write-Host "   .\start-all.ps1" -ForegroundColor White
Write-Host ""
