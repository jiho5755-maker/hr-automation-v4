# ==================== HR 자동화 시스템 일일 백업 스크립트 ====================
# Windows PowerShell 자동 백업
# 작업 스케줄러에 등록하여 매일 실행

param(
    [int]$RetentionDays = 7
)

$ErrorActionPreference = "Stop"

# 백업 디렉토리
$backupRoot = ".\backups"
$date = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = Join-Path $backupRoot "backup_$date"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  HR 자동화 자동 백업  " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📅 백업 시작: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow
Write-Host ""

try {
    # 1. 백업 디렉토리 생성
    if (-not (Test-Path $backupRoot)) {
        New-Item -ItemType Directory -Path $backupRoot | Out-Null
    }
    New-Item -ItemType Directory -Path $backupDir | Out-Null
    Write-Host "✅ 백업 디렉토리 생성: $backupDir" -ForegroundColor Green
    
    # 2. 데이터베이스 백업
    Write-Host "💾 데이터베이스 백업 중..." -ForegroundColor Yellow
    
    # 컨테이너가 실행 중이면 컨테이너에서 복사
    $containerRunning = docker-compose ps -q dashboard
    if ($containerRunning) {
        # 컨테이너 내부에서 DB 복사
        docker-compose exec -T dashboard cp /app/hr_master.db /app/hr_master_backup.db
        docker cp hr-dashboard:/app/hr_master_backup.db "$backupDir\hr_master.db"
        docker-compose exec -T dashboard rm /app/hr_master_backup.db
    } else {
        # 컨테이너가 중지되어 있으면 직접 복사
        Copy-Item "hr_master.db" "$backupDir\hr_master.db"
        if (Test-Path "hr_master.db-shm") { Copy-Item "hr_master.db-shm" "$backupDir\" }
        if (Test-Path "hr_master.db-wal") { Copy-Item "hr_master.db-wal" "$backupDir\" }
    }
    Write-Host "✅ 데이터베이스 백업 완료" -ForegroundColor Green
    
    # 3. 로그 백업
    Write-Host "📋 로그 백업 중..." -ForegroundColor Yellow
    if (Test-Path "logs") {
        Copy-Item -Recurse "logs" "$backupDir\logs"
        Write-Host "✅ 로그 백업 완료" -ForegroundColor Green
    } else {
        Write-Host "⚠️  로그 디렉토리 없음" -ForegroundColor Yellow
    }
    
    # 4. 환경 설정 백업
    Write-Host "⚙️  환경 설정 백업 중..." -ForegroundColor Yellow
    if (Test-Path ".env") {
        Copy-Item ".env" "$backupDir\.env"
        Write-Host "✅ 환경 설정 백업 완료" -ForegroundColor Green
    }
    
    # 5. docker-compose 설정 백업
    Copy-Item "docker-compose.yml" "$backupDir\docker-compose.yml"
    Copy-Item "nginx\nginx.conf" "$backupDir\nginx.conf"
    Write-Host "✅ Docker 설정 백업 완료" -ForegroundColor Green
    
    # 6. 백업 크기 계산
    $backupSize = (Get-ChildItem -Recurse $backupDir | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host ""
    Write-Host "📦 백업 크기: $([math]::Round($backupSize, 2)) MB" -ForegroundColor Cyan
    
    # 7. 오래된 백업 삭제
    Write-Host ""
    Write-Host "🗑️  오래된 백업 정리 중 (보관 기간: $RetentionDays 일)..." -ForegroundColor Yellow
    $cutoffDate = (Get-Date).AddDays(-$RetentionDays)
    $oldBackups = Get-ChildItem $backupRoot -Directory | Where-Object {
        $_.Name -match "^backup_\d{8}_\d{6}$" -and $_.CreationTime -lt $cutoffDate
    }
    
    if ($oldBackups) {
        $oldBackups | ForEach-Object {
            Remove-Item $_.FullName -Recurse -Force
            Write-Host "   삭제: $($_.Name)" -ForegroundColor Gray
        }
        Write-Host "✅ 오래된 백업 $($oldBackups.Count)개 삭제" -ForegroundColor Green
    } else {
        Write-Host "   삭제할 백업 없음" -ForegroundColor Gray
    }
    
    # 8. 완료
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "  ✅ 백업 완료!  " -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📁 백업 위치: $backupDir" -ForegroundColor Cyan
    Write-Host "📅 완료 시각: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
    Write-Host ""
    
    # 9. 백업 로그 기록
    $logEntry = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        backup_dir = $backupDir
        backup_size_mb = [math]::Round($backupSize, 2)
        retention_days = $RetentionDays
        deleted_count = if ($oldBackups) { $oldBackups.Count } else { 0 }
        status = "success"
    }
    
    $logFile = Join-Path $backupRoot "backup_history.json"
    $history = @()
    if (Test-Path $logFile) {
        $history = Get-Content $logFile -Raw | ConvertFrom-Json
    }
    $history += $logEntry
    $history | ConvertTo-Json | Set-Content $logFile
    
    exit 0
    
} catch {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Red
    Write-Host "  ❌ 백업 실패!  " -ForegroundColor Red
    Write-Host "================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "오류: $_" -ForegroundColor Red
    Write-Host ""
    
    # 실패 로그 기록
    $logEntry = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        error = $_.Exception.Message
        status = "failed"
    }
    
    $logFile = Join-Path $backupRoot "backup_history.json"
    $history = @()
    if (Test-Path $logFile) {
        $history = Get-Content $logFile -Raw | ConvertFrom-Json
    }
    $history += $logEntry
    $history | ConvertTo-Json | Set-Content $logFile
    
    exit 1
}
