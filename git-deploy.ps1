# ==================== HR 자동화 시스템 Git 배포 스크립트 ====================
# Windows PowerShell 스크립트
# 실행: .\git-deploy.ps1

param(
    [switch]$SkipBackup,
    [switch]$Force
)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  HR 자동화 Git 배포  " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 1. Git 상태 확인
Write-Host "[1/6] Git 상태 확인..." -ForegroundColor Yellow
$gitStatus = git status --porcelain 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git 저장소가 아닙니다!" -ForegroundColor Red
    Write-Host "   먼저 Git 저장소를 클론하세요:" -ForegroundColor Yellow
    Write-Host "   git clone <repository-url> ." -ForegroundColor White
    exit 1
}

if ($gitStatus -and -not $Force) {
    Write-Host "⚠️  로컬 변경사항이 있습니다:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    Write-Host "계속하려면 Enter, 취소하려면 Ctrl+C" -ForegroundColor Yellow
    Read-Host
}
Write-Host "✅ Git 저장소 확인 완료" -ForegroundColor Green
Write-Host ""

# 2. 현재 브랜치 확인
Write-Host "[2/6] 현재 브랜치 확인..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
Write-Host "   현재 브랜치: $currentBranch" -ForegroundColor Cyan
Write-Host "✅ 브랜치 확인 완료" -ForegroundColor Green
Write-Host ""

# 3. 백업 (선택사항)
if (-not $SkipBackup) {
    Write-Host "[3/6] 현재 상태 백업..." -ForegroundColor Yellow
    $backupDate = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = "_backups\backup_$backupDate`_before_deploy"
    
    if (-not (Test-Path "_backups")) {
        New-Item -ItemType Directory -Path "_backups" | Out-Null
    }
    
    # 중요 파일만 백업
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    if (Test-Path ".env") { Copy-Item ".env" "$backupDir\.env" }
    if (Test-Path "hr_master.db") { Copy-Item "hr_master.db" "$backupDir\hr_master.db" }
    
    Write-Host "✅ 백업 완료: $backupDir" -ForegroundColor Green
} else {
    Write-Host "[3/6] 백업 건너뜀 (--SkipBackup)" -ForegroundColor Gray
}
Write-Host ""

# 4. 최신 코드 가져오기
Write-Host "[4/6] 최신 코드 가져오기..." -ForegroundColor Yellow
git fetch origin
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git fetch 실패!" -ForegroundColor Red
    exit 1
}

Write-Host "   변경사항 확인 중..." -ForegroundColor Cyan
$behind = git rev-list HEAD..origin/$currentBranch --count
if ($behind -eq 0) {
    Write-Host "✅ 이미 최신 버전입니다!" -ForegroundColor Green
    Write-Host ""
    Write-Host "배포를 종료합니다." -ForegroundColor Yellow
    exit 0
}

Write-Host "   새로운 커밋 $behind 개 발견" -ForegroundColor Cyan
git log HEAD..origin/$currentBranch --oneline
Write-Host ""

# 5. Pull 실행
Write-Host "[5/6] 코드 업데이트..." -ForegroundColor Yellow
git pull origin $currentBranch
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git pull 실패!" -ForegroundColor Red
    Write-Host "   충돌을 해결하고 다시 시도하세요." -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ 코드 업데이트 완료" -ForegroundColor Green
Write-Host ""

# 6. Docker 재배포
Write-Host "[6/6] Docker 재배포..." -ForegroundColor Yellow
Write-Host "   컨테이너 중지 중..." -ForegroundColor Cyan
docker-compose down

Write-Host "   컨테이너 재빌드 및 시작 중..." -ForegroundColor Cyan
docker-compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker 재배포 완료" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "================================" -ForegroundColor Green
    Write-Host "  🎉 배포 완료!  " -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 접속 정보:" -ForegroundColor Cyan
    Write-Host "   http://localhost" -ForegroundColor White
    Write-Host "   http://localhost:8000" -ForegroundColor White
    Write-Host ""
    Write-Host "🔍 상태 확인:" -ForegroundColor Cyan
    Write-Host "   .\docker-status.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 로그 확인:" -ForegroundColor Cyan
    Write-Host "   .\docker-logs.ps1 -Follow" -ForegroundColor White
    Write-Host ""
    
    # 5초 후 브라우저 열기
    Start-Sleep -Seconds 5
    Write-Host "🌐 브라우저를 엽니다..." -ForegroundColor Cyan
    Start-Process "http://localhost"
} else {
    Write-Host "❌ Docker 재배포 실패!" -ForegroundColor Red
    Write-Host "   로그를 확인하세요: docker-compose logs" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
