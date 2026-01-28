# ==================== HR 자동화 시스템 v4.0 시작 스크립트 ====================
# Windows PowerShell 스크립트
# 실행: .\docker-start.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  HR 자동화 시스템 v4.0 시작  " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 1. Docker 실행 확인
Write-Host "[1/5] Docker 실행 상태 확인..." -ForegroundColor Yellow
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "❌ Docker가 실행되고 있지 않습니다!" -ForegroundColor Red
    Write-Host "   Docker Desktop을 시작하고 다시 실행하세요." -ForegroundColor Red
    pause
    exit 1
}
Write-Host "✅ Docker 정상 실행 중" -ForegroundColor Green
Write-Host ""

# 2. .env 파일 확인
Write-Host "[2/5] 환경 설정 확인..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env 파일이 없습니다. env.example.txt를 복사합니다..." -ForegroundColor Yellow
    Copy-Item "env.example.txt" ".env"
    Write-Host "✅ .env 파일 생성 완료" -ForegroundColor Green
    Write-Host "   📝 .env 파일을 열어 설정을 확인하세요!" -ForegroundColor Cyan
} else {
    Write-Host "✅ .env 파일 존재" -ForegroundColor Green
}
Write-Host ""

# 3. 데이터베이스 초기화 확인
Write-Host "[3/5] 데이터베이스 확인..." -ForegroundColor Yellow
if (-not (Test-Path "hr_master.db")) {
    Write-Host "⚠️  hr_master.db가 없습니다. 초기화합니다..." -ForegroundColor Yellow
    python scripts/init_system.py
    Write-Host "✅ 데이터베이스 초기화 완료" -ForegroundColor Green
} else {
    Write-Host "✅ 데이터베이스 존재" -ForegroundColor Green
}
Write-Host ""

# 4. logs 디렉토리 생성
Write-Host "[4/5] 로그 디렉토리 생성..." -ForegroundColor Yellow
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}
Write-Host "✅ 로그 디렉토리 준비 완료" -ForegroundColor Green
Write-Host ""

# 5. Docker Compose 실행
Write-Host "[5/5] Docker 컨테이너 시작..." -ForegroundColor Yellow
Write-Host "   빌드 중... (최초 실행시 5-10분 소요)" -ForegroundColor Cyan
docker-compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "  🎉 시작 완료!  " -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 접속 정보:" -ForegroundColor Cyan
    Write-Host "   - 메인 대시보드: http://localhost" -ForegroundColor White
    Write-Host "   - 또는: http://localhost:8000" -ForegroundColor White
    Write-Host ""
    Write-Host "🔍 상태 확인:" -ForegroundColor Cyan
    Write-Host "   docker-compose ps" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 로그 확인:" -ForegroundColor Cyan
    Write-Host "   docker-compose logs -f" -ForegroundColor White
    Write-Host ""
    Write-Host "⏹️  중지:" -ForegroundColor Cyan
    Write-Host "   .\docker-stop.ps1" -ForegroundColor White
    Write-Host ""
    
    # 브라우저 자동 열기
    Start-Sleep -Seconds 5
    Write-Host "🌐 브라우저를 엽니다..." -ForegroundColor Cyan
    Start-Process "http://localhost"
} else {
    Write-Host ""
    Write-Host "❌ 시작 실패!" -ForegroundColor Red
    Write-Host "   로그를 확인하세요: docker-compose logs" -ForegroundColor Red
}

Write-Host ""
