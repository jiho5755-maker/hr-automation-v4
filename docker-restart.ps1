# ==================== HR 자동화 시스템 v4.0 재시작 스크립트 ====================
# Windows PowerShell 스크립트
# 실행: .\docker-restart.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  HR 자동화 시스템 v4.0 재시작  " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 1. 중지
Write-Host "[1/2] 기존 컨테이너 중지..." -ForegroundColor Yellow
docker-compose down
Write-Host "✅ 중지 완료" -ForegroundColor Green
Write-Host ""

# 2. 시작
Write-Host "[2/2] 컨테이너 재시작..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "  🎉 재시작 완료!  " -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 http://localhost 에서 확인하세요!" -ForegroundColor Cyan
    Write-Host ""
    
    Start-Sleep -Seconds 3
    Start-Process "http://localhost"
} else {
    Write-Host ""
    Write-Host "❌ 재시작 실패!" -ForegroundColor Red
    Write-Host "   로그를 확인하세요: docker-compose logs" -ForegroundColor Red
}

Write-Host ""
