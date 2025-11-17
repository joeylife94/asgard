# Asgard Local Development Shutdown Script
# PowerShell script to stop infrastructure services

Write-Host "🛑 Stopping Asgard Local Development Environment" -ForegroundColor Cyan
Write-Host ""

# Stop Docker Compose services
Write-Host "🐳 Stopping Docker containers..." -ForegroundColor Yellow
docker-compose down

Write-Host ""
Write-Host "✅ All services stopped!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 To remove volumes (data will be lost), run:" -ForegroundColor Yellow
Write-Host "   docker-compose down -v" -ForegroundColor White
Write-Host ""
Write-Host "💡 To start services again, run:" -ForegroundColor Yellow
Write-Host "   ./start-dev.ps1" -ForegroundColor White
