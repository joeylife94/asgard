# Asgard Unified Build Script
# Builds all services: Heimdall (Java), Bifrost (Python), and Frontend (React)

param(
    [switch]$SkipTests,
    [switch]$SkipFrontend,
    [switch]$Clean,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$StartTime = Get-Date

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      🏗️  Asgard Unified Build - All Services              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Configuration
$BuildResults = @{
    Heimdall = @{ Status = "Pending"; Time = 0 }
    Bifrost = @{ Status = "Pending"; Time = 0 }
    Frontend = @{ Status = "Pending"; Time = 0 }
}

# Helper function to measure execution time
function Invoke-BuildStep {
    param(
        [string]$Name,
        [scriptblock]$Script
    )
    
    Write-Host "┌─────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
    Write-Host "│  Building: $Name" -ForegroundColor Yellow
    Write-Host "└─────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
    Write-Host ""
    
    $stepStart = Get-Date
    try {
        & $Script
        $BuildResults[$Name].Status = "✅ Success"
        Write-Host ""
        Write-Host "✅ $Name build completed successfully!" -ForegroundColor Green
    }
    catch {
        $BuildResults[$Name].Status = "❌ Failed"
        Write-Host ""
        Write-Host "❌ $Name build failed: $($_.Exception.Message)" -ForegroundColor Red
        throw
    }
    finally {
        $BuildResults[$Name].Time = [math]::Round(((Get-Date) - $stepStart).TotalSeconds, 2)
    }
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════
# 1️⃣  HEIMDALL (Java/Spring Boot)
# ═══════════════════════════════════════════════════════════

Invoke-BuildStep -Name "Heimdall" -Script {
    Write-Host "🔧 Building Heimdall (Spring Boot)..." -ForegroundColor Cyan
    
    # Check Java
    try {
        $javaVersion = java -version 2>&1 | Select-Object -First 1
        Write-Host "   Java: $javaVersion" -ForegroundColor Gray
    }
    catch {
        throw "Java not found. Please install JDK 17 or higher."
    }
    
    # Build command
    $gradleCmd = ".\gradlew.bat"
    $buildArgs = @(":heimdall:clean", ":heimdall:build")
    
    if ($SkipTests) {
        $buildArgs += "-x", "test"
        Write-Host "   ⚠️  Skipping tests" -ForegroundColor Yellow
    }
    
    if (-not $Verbose) {
        $buildArgs += "-q"
    }
    
    Write-Host "   Command: $gradleCmd $($buildArgs -join ' ')" -ForegroundColor Gray
    Write-Host ""
    
    & $gradleCmd $buildArgs
    
    if ($LASTEXITCODE -ne 0) {
        throw "Gradle build failed with exit code $LASTEXITCODE"
    }
    
    # Check output
    $jarFile = Get-Item "heimdall\build\libs\*.jar" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($jarFile) {
        Write-Host "   📦 Artifact: $($jarFile.Name) ($([math]::Round($jarFile.Length/1MB, 2)) MB)" -ForegroundColor Gray
    }
}

# ═══════════════════════════════════════════════════════════
# 2️⃣  BIFROST (Python/FastAPI)
# ═══════════════════════════════════════════════════════════

Invoke-BuildStep -Name "Bifrost" -Script {
    Write-Host "🐍 Building Bifrost (Python)..." -ForegroundColor Cyan
    
    Push-Location "bifrost"
    try {
        # Check Python
        try {
            $pythonVersion = python --version 2>&1
            Write-Host "   Python: $pythonVersion" -ForegroundColor Gray
        }
        catch {
            throw "Python not found. Please install Python 3.9 or higher."
        }
        
        # Create virtual environment if not exists
        if (-not (Test-Path ".venv")) {
            Write-Host "   📦 Creating virtual environment..." -ForegroundColor Yellow
            python -m venv .venv
        }
        
        # Activate virtual environment
        Write-Host "   🔄 Activating virtual environment..." -ForegroundColor Gray
        & ".venv\Scripts\Activate.ps1"
        
        # Upgrade pip
        Write-Host "   📥 Upgrading pip..." -ForegroundColor Gray
        python -m pip install --upgrade pip --quiet
        
        # Install dependencies
        Write-Host "   📥 Installing dependencies..." -ForegroundColor Cyan
        pip install -r requirements.txt --quiet
        
        # Install in editable mode
        Write-Host "   📦 Installing Bifrost package..." -ForegroundColor Gray
        pip install -e . --quiet
        
        # Run tests if not skipped
        if (-not $SkipTests) {
            Write-Host ""
            Write-Host "   🧪 Running tests..." -ForegroundColor Cyan
            if (Test-Path "tests") {
                pytest tests/ -v --tb=short
                if ($LASTEXITCODE -ne 0) {
                    throw "Pytest failed with exit code $LASTEXITCODE"
                }
            }
            else {
                Write-Host "   ⚠️  No tests directory found" -ForegroundColor Yellow
            }
        }
        
        Write-Host "   ✅ Bifrost dependencies installed" -ForegroundColor Gray
    }
    finally {
        Pop-Location
    }
}

# ═══════════════════════════════════════════════════════════
# 3️⃣  FRONTEND (React/Vite)
# ═══════════════════════════════════════════════════════════

if (-not $SkipFrontend) {
    Invoke-BuildStep -Name "Frontend" -Script {
        Write-Host "⚛️  Building Frontend (React)..." -ForegroundColor Cyan
        
        Push-Location "bifrost\frontend"
        try {
            # Check Node.js
            try {
                $nodeVersion = node --version 2>&1
                Write-Host "   Node.js: $nodeVersion" -ForegroundColor Gray
            }
            catch {
                throw "Node.js not found. Please install Node.js 18 or higher."
            }
            
            # Install dependencies
            Write-Host "   📥 Installing npm dependencies..." -ForegroundColor Cyan
            npm install --silent
            
            if ($LASTEXITCODE -ne 0) {
                throw "npm install failed with exit code $LASTEXITCODE"
            }
            
            # Build production bundle
            Write-Host "   🏗️  Building production bundle..." -ForegroundColor Cyan
            npm run build
            
            if ($LASTEXITCODE -ne 0) {
                throw "npm build failed with exit code $LASTEXITCODE"
            }
            
            # Check output
            if (Test-Path "dist") {
                $distSize = (Get-ChildItem "dist" -Recurse | Measure-Object -Property Length -Sum).Sum
                Write-Host "   📦 Build output: dist/ ($([math]::Round($distSize/1MB, 2)) MB)" -ForegroundColor Gray
            }
        }
        finally {
            Pop-Location
        }
    }
}
else {
    Write-Host "⏭️  Skipping Frontend build (--SkipFrontend flag)" -ForegroundColor Yellow
    $BuildResults.Frontend.Status = "⏭️  Skipped"
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════
# 📊 BUILD SUMMARY
# ═══════════════════════════════════════════════════════════

$TotalTime = [math]::Round(((Get-Date) - $StartTime).TotalSeconds, 2)

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                   📊 BUILD SUMMARY                         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

foreach ($service in $BuildResults.Keys) {
    $result = $BuildResults[$service]
    $status = $result.Status
    $time = if ($result.Time -gt 0) { "$($result.Time)s" } else { "-" }
    Write-Host ("  {0,-12} {1,-15} ({2})" -f $service, $status, $time)
}

Write-Host ""
Write-Host "  Total Time: $TotalTime seconds" -ForegroundColor Cyan
Write-Host ""

# Check if all builds succeeded
$allSucceeded = ($BuildResults.Values | Where-Object { $_.Status -like "*Failed*" }).Count -eq 0

if ($allSucceeded) {
    Write-Host "✅ All builds completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Next steps:" -ForegroundColor Yellow
    Write-Host "   1. Start infrastructure: .\start-dev.ps1" -ForegroundColor White
    Write-Host "   2. Run Heimdall: .\gradlew :heimdall:bootRun" -ForegroundColor White
    Write-Host "   3. Run Bifrost: cd bifrost; .venv\Scripts\Activate.ps1; python -m bifrost.main" -ForegroundColor White
    Write-Host "   4. Run Frontend: cd bifrost\frontend; npm run dev" -ForegroundColor White
    exit 0
}
else {
    Write-Host "❌ Some builds failed. Please check the errors above." -ForegroundColor Red
    exit 1
}
