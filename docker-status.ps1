# ==================== HR 자동화 시스템 v4.0 상태 확인 스크립트 ====================
# Windows PowerShell 스크립트
# 실행: .\docker-status.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  HR 자동화 시스템 상태  " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 1. 컨테이너 상태
Write-Host "📦 컨테이너 상태:" -ForegroundColor Yellow
docker-compose ps
Write-Host ""

# 2. 리소스 사용량
Write-Host "💻 리소스 사용량:" -ForegroundColor Yellow
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
Write-Host ""

# 3. 네트워크 정보
Write-Host "🌐 네트워크 정보:" -ForegroundColor Yellow
docker network ls | Select-String "hr"
Write-Host ""

# 4. 볼륨 정보
Write-Host "💾 볼륨 정보:" -ForegroundColor Yellow
docker volume ls | Select-String "hr"
Write-Host ""

# 5. 접속 URL
Write-Host "🔗 접속 정보:" -ForegroundColor Yellow
Write-Host "   메인 대시보드: http://localhost" -ForegroundColor Green
Write-Host "   직접 접속:     http://localhost:8000" -ForegroundColor Green
Write-Host ""

# 6. 헬스체크
Write-Host "❤️  헬스체크:" -ForegroundColor Yellow
$healthCheck = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing -ErrorAction SilentlyContinue
if ($healthCheck.StatusCode -eq 200) {
    Write-Host "   ✅ 시스템 정상" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  시스템 응답 없음" -ForegroundColor Red
}
Write-Host ""

Write-Host "💡 유용한 명령어:" -ForegroundColor Cyan
Write-Host "   .\docker-logs.ps1        # 로그 확인" -ForegroundColor White
Write-Host "   .\docker-restart.ps1     # 재시작" -ForegroundColor White
Write-Host "   .\docker-stop.ps1        # 중지" -ForegroundColor White
Write-Host ""
