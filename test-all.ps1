# Asgard Unified Test Script
# Runs all tests: Heimdall (Java), Bifrost (Python), and Frontend (React)

param(
    [switch]$Coverage,
    [switch]$SkipIntegration,
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

# Configuration
$TestResults = @{
    Heimdall = @{ Status = "Pending"; Passed = 0; Failed = 0; Time = 0 }
    Bifrost = @{ Status = "Pending"; Passed = 0; Failed = 0; Time = 0 }
    Frontend = @{ Status = "Pending"; Passed = 0; Failed = 0; Time = 0 }
}

# Helper function to run tests
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
        $TestResults[$Name].Status = "✅ Passed"
        Write-Host ""
        Write-Host "✅ $Name tests passed!" -ForegroundColor Green
    }
    catch {
        $TestResults[$Name].Status = "❌ Failed"
        Write-Host ""
        Write-Host "❌ $Name tests failed: $($_.Exception.Message)" -ForegroundColor Red
        # Don't throw - continue with other tests
    }
    finally {
        $TestResults[$Name].Time = [math]::Round(((Get-Date) - $stepStart).TotalSeconds, 2)
    }
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════
# 1️⃣  HEIMDALL TESTS (Java/JUnit)
# ═══════════════════════════════════════════════════════════

if ($Service -eq "all" -or $Service -eq "heimdall") {
    Invoke-TestSuite -Name "Heimdall" -Script {
        Write-Host "Running Heimdall tests (JUnit)..." -ForegroundColor Cyan
        
        $gradleCmd = ".\gradlew.bat"
        $testArgs = @(":heimdall:test")
        
        if ($Coverage) {
            $testArgs += "jacocoTestReport"
            Write-Host "   Code coverage enabled" -ForegroundColor Yellow
        }
        
        if ($SkipIntegration) {
            $testArgs += "-Dtest.excludeTags=integration"
            Write-Host "   Skipping integration tests" -ForegroundColor Yellow
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
        
        # Parse test results
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

# ═══════════════════════════════════════════════════════════
# 2️⃣  BIFROST TESTS (Python/Pytest)
# ═══════════════════════════════════════════════════════════

if ($Service -eq "all" -or $Service -eq "bifrost") {
    Invoke-TestSuite -Name "Bifrost" -Script {
        Write-Host "Running Bifrost tests (Pytest)..." -ForegroundColor Cyan
        
        Push-Location "bifrost"
        try {
            # Activate virtual environment
            if (Test-Path ".venv\Scripts\Activate.ps1") {
                Write-Host "   Activating virtual environment..." -ForegroundColor Gray
                & ".venv\Scripts\Activate.ps1"

                if (Test-Path "requirements.txt") {
                    python -m pip install --upgrade pip setuptools wheel --quiet

                    # Install dependencies if core imports are missing
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

                # Ensure local package import works even if the venv already existed
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

                    # Try full install first
                    python -m pip install -r requirements.txt --quiet
                    if ($LASTEXITCODE -ne 0) {
                        Write-Host "   requirements.txt install failed; retrying without aiokafka (Windows toolchain issue)" -ForegroundColor Yellow
                        $tmpReq = Join-Path $env:TEMP "bifrost-requirements-no-aiokafka.txt"
                        (Get-Content "requirements.txt" | Where-Object { $_ -notmatch '^\s*aiokafka\s*==' }) | Set-Content -Path $tmpReq
                        python -m pip install -r $tmpReq --quiet
                    }

                    # Ensure local package import works
                    python -m pip install -e . --no-deps --quiet
                }
            }
            
            # Ensure pytest is installed
            pip install pytest pytest-cov --quiet
            
            # Build pytest command
            $pytestArgs = @("tests/")
            
            if ($Verbose) {
                $pytestArgs += "-v"
            }
            else {
                $pytestArgs += "-q"
            }
            
            if ($Coverage) {
                $pytestArgs += "--cov=bifrost", "--cov-report=html", "--cov-report=term"
                Write-Host "   Code coverage enabled" -ForegroundColor Yellow
            }
            
            if ($SkipIntegration) {
                $pytestArgs += "-m", "not integration"
                Write-Host "   Skipping integration tests" -ForegroundColor Yellow
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

# ═══════════════════════════════════════════════════════════
# 3️⃣  FRONTEND TESTS (React/Vitest)
# ═══════════════════════════════════════════════════════════

if ($Service -eq "all" -or $Service -eq "frontend") {
    Invoke-TestSuite -Name "Frontend" -Script {
        Write-Host "Running Frontend tests (Vitest)..." -ForegroundColor Cyan
        
        Push-Location "bifrost\frontend"
        try {
            # Check if package.json has test script
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
                Write-Host "   Consider adding Vitest or Jest for frontend testing" -ForegroundColor Gray
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

# ═══════════════════════════════════════════════════════════
# 📊 TEST SUMMARY
# ═══════════════════════════════════════════════════════════

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

# Check if all tests passed
$allPassed = ($TestResults.Values | Where-Object { $_.Status -like "*Failed*" }).Count -eq 0

if ($allPassed) {
    Write-Host "All tests passed successfully!" -ForegroundColor Green
    Write-Host ""
    
    if ($Coverage) {
        Write-Host "Coverage Reports:" -ForegroundColor Yellow
        Write-Host "   • Heimdall: heimdall\build\reports\jacoco\test\html\index.html" -ForegroundColor White
        Write-Host "   • Bifrost:  bifrost\htmlcov\index.html" -ForegroundColor White
        Write-Host ""
    }
    
    exit 0
}
else {
    Write-Host "❌ Some tests failed. Please check the errors above." -ForegroundColor Red
    Write-Host ""
    Write-Host "Quick tips:" -ForegroundColor Yellow
    Write-Host "   • Check test reports for details" -ForegroundColor White
    Write-Host "   • Run specific service: .\test-all.ps1 -Service heimdall" -ForegroundColor White
    Write-Host "   • Skip integration tests: .\test-all.ps1 -SkipIntegration" -ForegroundColor White
    exit 1
}
