# ==================== HR 자동화 시스템 v4.0 로그 확인 스크립트 ====================
# Windows PowerShell 스크립트
# 실행: .\docker-logs.ps1

param(
    [string]$Service = "all",
    [int]$Lines = 100,
    [switch]$Follow
)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  HR 자동화 로그 확인  " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

if ($Service -eq "all") {
    Write-Host "📋 전체 서비스 로그 (최근 $Lines 줄):" -ForegroundColor Yellow
    Write-Host ""
    
    if ($Follow) {
        docker-compose logs -f --tail=$Lines
    } else {
        docker-compose logs --tail=$Lines
    }
} else {
    Write-Host "📋 $Service 서비스 로그 (최근 $Lines 줄):" -ForegroundColor Yellow
    Write-Host ""
    
    if ($Follow) {
        docker-compose logs -f --tail=$Lines $Service
    } else {
        docker-compose logs --tail=$Lines $Service
    }
}

Write-Host ""
Write-Host "💡 사용 예시:" -ForegroundColor Cyan
Write-Host "   .\docker-logs.ps1                    # 전체 로그 (최근 100줄)" -ForegroundColor White
Write-Host "   .\docker-logs.ps1 -Follow            # 실시간 로그" -ForegroundColor White
Write-Host "   .\docker-logs.ps1 -Service dashboard # 대시보드만" -ForegroundColor White
Write-Host "   .\docker-logs.ps1 -Lines 500         # 최근 500줄" -ForegroundColor White
Write-Host ""
