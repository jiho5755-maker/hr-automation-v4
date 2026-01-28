#!/bin/bash

###############################################################################
# Phase 0: 준비 작업 - 백업 및 Git 브랜치 생성
###############################################################################

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 Phase 0: 준비 작업"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$(dirname "$0")"

# 1. 백업 생성
echo "📦 Step 1: 프로젝트 백업 생성..."
BACKUP_DIR="_backups/backup_$(date +%Y%m%d_%H%M%S)_pre_integration"
mkdir -p "$BACKUP_DIR"
cp -r . "$BACKUP_DIR/" 2>/dev/null
echo "   ✅ 백업 완료: $BACKUP_DIR"
echo ""

# 2. Git 브랜치 생성
echo "🌿 Step 2: Git 브랜치 생성..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    CURRENT_BRANCH=$(git branch --show-current)
    echo "   현재 브랜치: $CURRENT_BRANCH"
    
    if [ "$CURRENT_BRANCH" = "feature/hr-integration" ]; then
        echo "   ℹ️  이미 feature/hr-integration 브랜치입니다"
    else
        git checkout -b feature/hr-integration 2>/dev/null && \
            echo "   ✅ feature/hr-integration 브랜치 생성 완료" || \
            echo "   ⚠️  브랜치가 이미 존재합니다. 기존 브랜치로 전환합니다" && \
            git checkout feature/hr-integration
    fi
else
    echo "   ⚠️  Git 저장소가 아닙니다. Git 초기화를 건너뜁니다."
fi
echo ""

# 3. 환경 확인
echo "🔍 Step 3: 개발 환경 확인..."
echo "   Python 버전:"
python3 --version 2>/dev/null || echo "   ❌ Python3가 설치되지 않았습니다"
echo ""
echo "   Streamlit 버전:"
pip3 show streamlit 2>/dev/null | grep Version || echo "   ❌ Streamlit이 설치되지 않았습니다"
echo ""

# 4. 데이터베이스 확인
echo "🗄️  Step 4: 데이터베이스 확인..."
if [ -f "hr_master.db" ]; then
    echo "   ✅ hr_master.db 존재"
    echo "   데이터베이스 크기: $(du -h hr_master.db | cut -f1)"
    
    # 직원 수 확인
    EMPLOYEE_COUNT=$(sqlite3 hr_master.db "SELECT COUNT(*) FROM employees WHERE is_active=1" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "   등록된 직원 수: $EMPLOYEE_COUNT명"
    fi
else
    echo "   ⚠️  hr_master.db가 없습니다. 초기화가 필요합니다."
fi
echo ""

# 5. 요약
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Phase 0 준비 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 다음 단계:"
echo "   1. 생성된 코드 파일들 확인"
echo "   2. Phase 3 마이그레이션 실행 (scripts/migrate_json_to_db.py)"
echo "   3. START_HERE.sh 실행"
echo ""
echo "🚀 이제 Phase 1-4 구현을 시작하세요!"
echo ""
