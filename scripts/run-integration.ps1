# Helper to run integration tests locally (brings up docker-compose services)

param(
    [switch]$Detach
)

$ErrorActionPreference = "Stop"

Write-Host "Starting required services via docker-compose..." -ForegroundColor Cyan
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is not installed or not on PATH. Install Docker Desktop or ensure 'docker' is available."
}

# Use top-level docker-compose if present
$composeFile = "docker-compose.yml"
if (-not (Test-Path $composeFile)) {
    Write-Host "No top-level docker-compose.yml found; trying bifrost/docker-compose.yml" -ForegroundColor Yellow
    $composeFile = "bifrost\docker-compose.yml"
}

if (-not (Test-Path $composeFile)) {
    throw "No docker-compose file found to start integration services."
}

if ($Detach) {
    docker compose -f $composeFile up -d
}
else {
    docker compose -f $composeFile up -d
}

Write-Host "Running integration tests (Pytest -m integration)..." -ForegroundColor Cyan
Push-Location "bifrost"
try {
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        & ".venv\Scripts\Activate.ps1"
    }
    else {
        python -m venv .venv
        & ".venv\Scripts\Activate.ps1"
        python -m pip install --upgrade pip setuptools wheel
        python -m pip install -r requirements.txt || true
        python -m pip install -e . --no-deps
    }

    python -m pytest -q -m integration
}
finally {
    Pop-Location
}

Write-Host "Integration run complete. Services left running (use 'docker compose -f $composeFile down' to stop)." -ForegroundColor Green
