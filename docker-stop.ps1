# ==================== HR 자동화 시스템 v4.0 중지 스크립트 ====================
# Windows PowerShell 스크립트
# 실행: .\docker-stop.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  HR 자동화 시스템 v4.0 중지  " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🛑 컨테이너 중지 중..." -ForegroundColor Yellow
docker-compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ 모든 컨테이너가 중지되었습니다." -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ 중지 실패!" -ForegroundColor Red
    Write-Host "   강제 중지를 시도하려면:" -ForegroundColor Yellow
    Write-Host "   docker-compose down --remove-orphans" -ForegroundColor White
    Write-Host ""
}
