# Asgard Unified Test Script
# Runs all tests: Heimdall (Java), Bifrost (Python), and Frontend (React)

param(
    [switch]$Coverage,
    [switch]$IncludeIntegration,
    [switch]$Verbose,
    [string]$Service = "all"  # Options: all, heimdall, bifrost, frontend
)

$ErrorActionPreference = "Stop"
$StartTime = Get-Date

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Asgard Unified Test Suite - All Services" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$TestResults = @{
    Heimdall = @{ Status = "Pending"; Passed = 0; Failed = 0; Time = 0 }
    Bifrost = @{ Status = "Pending"; Passed = 0; Failed = 0; Time = 0 }
    Frontend = @{ Status = "Pending"; Passed = 0; Failed = 0; Time = 0 }
}

function Invoke-TestSuite {
    param(
        [string]$Name,
        [scriptblock]$Script
    )

    Write-Host "------------------------------------------------------------" -ForegroundColor Yellow
    Write-Host " Testing: $Name" -ForegroundColor Yellow
    Write-Host "------------------------------------------------------------" -ForegroundColor Yellow
    Write-Host ""

    $stepStart = Get-Date
    try {
        & $Script

        # Only promote a suite to Passed when the suite itself did not set
        # a more truthful terminal state such as "No tests" or "Skipped".
        if ($TestResults[$Name].Status -eq "Pending") {
            $TestResults[$Name].Status = "✅ Passed"
            Write-Host ""
            Write-Host "✅ $Name tests passed!" -ForegroundColor Green
        }
        else {
            Write-Host ""
            Write-Host "$Name completed with status: $($TestResults[$Name].Status)" -ForegroundColor Yellow
        }
    }
    catch {
        $TestResults[$Name].Status = "❌ Failed"
        Write-Host ""
        Write-Host "❌ $Name tests failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    finally {
        $TestResults[$Name].Time = [math]::Round(((Get-Date) - $stepStart).TotalSeconds, 2)
    }
    Write-Host ""
}

# 1. HEIMDALL TESTS (Java/JUnit)
if ($Service -eq "all" -or $Service -eq "heimdall") {
    Invoke-TestSuite -Name "Heimdall" -Script {
        Write-Host "Running Heimdall tests (JUnit)..." -ForegroundColor Cyan

        $gradleCmd = ".\gradlew.bat"
        $testArgs = @(':heimdall:test')

        if ($Coverage) {
            $testArgs += "jacocoTestReport"
            Write-Host "   Code coverage enabled" -ForegroundColor Yellow
        }
        if (-not $IncludeIntegration) {
            $testArgs += "-Dtest.excludeTags=integration"
            Write-Host "   Skipping integration tests (default)" -ForegroundColor Yellow
        }
        if (-not $Verbose) {
            $testArgs += "-q"
        }

        Write-Host "   Command: $gradleCmd $($testArgs -join ' ')" -ForegroundColor Gray
        Write-Host ""
        & $gradleCmd $testArgs
        if ($LASTEXITCODE -ne 0) {
            throw "Heimdall tests failed with exit code $LASTEXITCODE"
        }

        $testResultFile = "heimdall\build\test-results\test\*.xml"
        if (Test-Path $testResultFile) {
            Write-Host "   Test report: heimdall\build\reports\tests\test\index.html" -ForegroundColor Gray
            if ($Coverage) {
                Write-Host "   Coverage report: heimdall\build\reports\jacoco\test\html\index.html" -ForegroundColor Gray
            }
        }
    }
}
else {
    Write-Host "Skipping Heimdall tests (Service: $Service)" -ForegroundColor Yellow
    $TestResults.Heimdall.Status = "⏭️  Skipped"
    Write-Host ""
}

# 2. BIFROST TESTS (Python/Pytest)
if ($Service -eq "all" -or $Service -eq "bifrost") {
    Invoke-TestSuite -Name "Bifrost" -Script {
        Write-Host "Running Bifrost tests (Pytest)..." -ForegroundColor Cyan

        Push-Location "bifrost"
        try {
            if (Test-Path ".venv\Scripts\Activate.ps1") {
                Write-Host "   Activating virtual environment..." -ForegroundColor Gray
                & ".venv\Scripts\Activate.ps1"

                if (Test-Path "requirements.txt") {
                    python -m pip install --upgrade pip setuptools wheel --quiet
                    python -c "import sqlalchemy, multipart" 2>$null
                    if ($LASTEXITCODE -ne 0) {
                        Write-Host "   Installing requirements.txt..." -ForegroundColor Gray
                        python -m pip install -r requirements.txt --quiet
                        if ($LASTEXITCODE -ne 0) {
                            Write-Host "   requirements.txt install failed; retrying without aiokafka (Windows toolchain issue)" -ForegroundColor Yellow
                            $tmpReq = Join-Path $env:TEMP "bifrost-requirements-no-aiokafka.txt"
                            (Get-Content "requirements.txt" | Where-Object { $_ -notmatch '^\s*aiokafka\s*==' }) | Set-Content -Path $tmpReq
                            python -m pip install -r $tmpReq --quiet
                        }
                    }
                }
                python -m pip install -e . --no-deps --quiet
            }
            else {
                Write-Host "   Virtual environment not found; creating .venv..." -ForegroundColor Yellow

                $pythonCmd = $null
                if (Get-Command python -ErrorAction SilentlyContinue) {
                    $pythonCmd = "python"
                }
                elseif (Get-Command py -ErrorAction SilentlyContinue) {
                    $pythonCmd = "py -3"
                }
                else {
                    throw "Python not found. Install Python 3.10+ or ensure 'python'/'py' is on PATH."
                }

                Invoke-Expression "$pythonCmd -m venv .venv"
                & ".venv\Scripts\Activate.ps1"

                if (Test-Path "requirements.txt") {
                    Write-Host "   Installing requirements.txt..." -ForegroundColor Gray
                    python -m pip install --upgrade pip setuptools wheel --quiet
                    python -m pip install -r requirements.txt --quiet
                    if ($LASTEXITCODE -ne 0) {
                        Write-Host "   requirements.txt install failed; retrying without aiokafka (Windows toolchain issue)" -ForegroundColor Yellow
                        $tmpReq = Join-Path $env:TEMP "bifrost-requirements-no-aiokafka.txt"
                        (Get-Content "requirements.txt" | Where-Object { $_ -notmatch '^\s*aiokafka\s*==' }) | Set-Content -Path $tmpReq
                        python -m pip install -r $tmpReq --quiet
                    }
                    python -m pip install -e . --no-deps --quiet
                }
            }

            pip install pytest pytest-cov --quiet

            $pytestArgs = @("tests/")
            if ($Verbose) { $pytestArgs += "-v" } else { $pytestArgs += "-q" }
            if ($Coverage) {
                $pytestArgs += "--cov=bifrost", "--cov-report=html", "--cov-report=term"
                Write-Host "   Code coverage enabled" -ForegroundColor Yellow
            }
            if (-not $IncludeIntegration) {
                $pytestArgs += "-m", "not integration"
                Write-Host "   Skipping integration tests (default)" -ForegroundColor Yellow
            }

            Write-Host "   Command: pytest $($pytestArgs -join ' ')" -ForegroundColor Gray
            Write-Host ""
            pytest $pytestArgs
            if ($LASTEXITCODE -ne 0) {
                throw "Bifrost tests failed with exit code $LASTEXITCODE"
            }

            if ($Coverage -and (Test-Path "htmlcov\index.html")) {
                Write-Host "   Coverage report: bifrost\htmlcov\index.html" -ForegroundColor Gray
            }
        }
        finally {
            Pop-Location
        }
    }
}
else {
    Write-Host "Skipping Bifrost tests (Service: $Service)" -ForegroundColor Yellow
    $TestResults.Bifrost.Status = "⏭️  Skipped"
    Write-Host ""
}

# 3. FRONTEND TESTS (React)
if ($Service -eq "all" -or $Service -eq "frontend") {
    Invoke-TestSuite -Name "Frontend" -Script {
        Write-Host "Running Frontend tests..." -ForegroundColor Cyan

        Push-Location "bifrost\frontend"
        try {
            $packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
            if ($packageJson.scripts.test) {
                Write-Host "   Running npm test..." -ForegroundColor Gray
                npm test -- --run
                if ($LASTEXITCODE -ne 0) {
                    throw "Frontend tests failed with exit code $LASTEXITCODE"
                }
            }
            else {
                Write-Host "   No test script found in package.json" -ForegroundColor Yellow
                Write-Host "   Frontend test coverage is unavailable; this suite is not counted as Passed." -ForegroundColor Yellow
                $TestResults.Frontend.Status = "⏭️  No tests"
            }
        }
        finally {
            Pop-Location
        }
    }
}
else {
    Write-Host "Skipping Frontend tests (Service: $Service)" -ForegroundColor Yellow
    $TestResults.Frontend.Status = "⏭️  Skipped"
    Write-Host ""
}

$TotalTime = [math]::Round(((Get-Date) - $StartTime).TotalSeconds, 2)

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " TEST SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

foreach ($service in $TestResults.Keys) {
    $result = $TestResults[$service]
    $status = $result.Status
    $time = if ($result.Time -gt 0) { "$($result.Time)s" } else { "-" }
    Write-Host ("  {0,-12} {1,-15} ({2})" -f $service, $status, $time)
}

Write-Host ""
Write-Host "  Total Time: $TotalTime seconds" -ForegroundColor Cyan
Write-Host ""

$hasFailures = ($TestResults.Values | Where-Object { $_.Status -like "*Failed*" }).Count -gt 0
$hasNonPass = ($TestResults.Values | Where-Object { $_.Status -notlike "*Passed*" }).Count -gt 0

if ($hasFailures) {
    Write-Host "❌ Some tests failed. Please check the errors above." -ForegroundColor Red
    Write-Host ""
    Write-Host "Quick tips:" -ForegroundColor Yellow
    Write-Host "   • Check test reports for details" -ForegroundColor White
    Write-Host "   • Run specific service: .\test-all.ps1 -Service heimdall" -ForegroundColor White
    Write-Host "   • Run integration tests: .\test-all.ps1 -IncludeIntegration" -ForegroundColor White
    exit 1
}

if ($hasNonPass) {
    Write-Host "Test suites completed without failures, but one or more suites were skipped or have no tests." -ForegroundColor Yellow
}
else {
    Write-Host "All requested test suites passed successfully!" -ForegroundColor Green
}
Write-Host ""

if ($Coverage) {
    Write-Host "Coverage Reports:" -ForegroundColor Yellow
    Write-Host "   • Heimdall: heimdall\build\reports\jacoco\test\html\index.html" -ForegroundColor White
    Write-Host "   • Bifrost:  bifrost\htmlcov\index.html" -ForegroundColor White
    Write-Host ""
}

exit 0
