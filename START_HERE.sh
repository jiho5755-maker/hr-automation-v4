#!/bin/bash

###############################################################################
# 인사팀 자동화 시스템 v4.0 - 통합 실행 스크립트
# ✨ 완전 통합: 단일 포트(8000)로 모든 모듈 실행
###############################################################################

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏢 인사팀 자동화 통합 시스템 v4.0"
echo "   ✨ 완전 통합: 하나의 포트로 모든 업무 처리"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 프로젝트 디렉토리로 이동
cd "$(dirname "$0")"
PROJECT_ROOT="${PWD}"

echo "🔍 Step 1: 기존 프로세스 정리..."
# 포트 8000 사용 중인 프로세스 종료
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "   ✅ 기존 프로세스 종료 완료" || echo "   ℹ️  실행 중인 프로세스 없음"

# 기존 포트들도 정리 (혹시나 남아있을 수 있음)
for PORT in 8501 8502 8503 8504 8505; do
    lsof -ti:${PORT} | xargs kill -9 2>/dev/null
done

sleep 1

echo ""
echo "🗑️  Step 2: Python 캐시 삭제..."
# __pycache__ 및 .pyc 파일 삭제
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
echo "   ✅ 캐시 삭제 완료"

echo ""
echo "🗄️  Step 3: 데이터베이스 확인..."

# hr_master.db 존재 확인
if [ -f "hr_master.db" ]; then
    echo "   ✅ hr_master.db 존재"
    
    # 직원 수 확인
    EMPLOYEE_COUNT=$(sqlite3 hr_master.db "SELECT COUNT(*) FROM employees WHERE is_active=1" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "   📊 등록된 직원: ${EMPLOYEE_COUNT}명"
    fi
else
    echo "   ⚠️  hr_master.db가 없습니다. 앱 시작 시 자동으로 생성됩니다."
fi

# employees_data.json 마이그레이션 확인
if [ -f "1_출산육아_자동화/employees_data.json" ] && [ "$EMPLOYEE_COUNT" == "0" ]; then
    echo ""
    echo "   ℹ️  employees_data.json 파일이 발견되었습니다."
    echo "   💡 마이그레이션을 실행하려면:"
    echo "      python3 scripts/migrate_json_to_db.py"
    echo ""
    read -p "   지금 마이그레이션을 실행하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 scripts/migrate_json_to_db.py
        echo ""
    fi
fi

echo ""
echo "🔬 Step 4: Import 테스트..."
cd "${PROJECT_ROOT}/0_통합_대시보드"
python3 << 'PYEOF'
import sys
from pathlib import Path

sys.path.append(str(Path.cwd().parent))

try:
    from shared.utils import show_success, format_currency, get_korean_weekday
    from shared.database import get_db, init_master_database
    from shared.auth import authenticate_user
    from shared.design import apply_design
    print("   ✅ 모든 shared 모듈 import 성공!")
except Exception as e:
    print(f"   ❌ Import 실패: {e}")
    exit(1)
PYEOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Import 테스트 실패!"
    echo "   문제가 지속되면 shared/ 폴더를 확인하세요."
    exit 1
fi

# 프로젝트 루트로 복귀
cd "${PROJECT_ROOT}"

echo ""
echo "📦 Step 5: 패키지 확인..."
if ! python3 -c "import streamlit, pandas" 2>/dev/null; then
    echo "   ⚠️  필수 패키지 설치 중..."
    pip3 install -q streamlit pandas openpyxl python-docx pillow
    echo "   ✅ 패키지 설치 완료"
else
    echo "   ✅ 패키지 정상"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 통합 대시보드 시작!"
echo ""
echo "📍 주소: http://localhost:8000"
echo "🔐 로그인: admin / admin1234"
echo ""
echo "✨ v4.0 새로운 기능:"
echo "   ✅ 단일 포트로 모든 모듈 통합 (8501-8505 포트 불필요)"
echo "   ✅ 직원 정보 한 번 입력, 모든 모듈 자동 반영"
echo "   ✅ 사이드바에서 원하는 기능 바로 선택"
echo ""
echo "📂 통합된 모듈:"
echo "   - 👥 직원 관리 (새로 추가!)"
echo "   - 👶 출산육아 자동화"
echo "   - 🏠 재택근무 관리"
echo "   - 💰 급여관리 자동화 (개선 예정)"
echo ""
echo "⚠️  중요:"
echo "   1. 브라우저에서 이전 localhost 탭을 모두 닫으세요"
echo "   2. 새 탭에서 http://localhost:8000 접속하세요"
echo "   3. 강제 새로고침: Cmd+Shift+R"
echo ""
echo "🛑 종료: Ctrl+C"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sleep 2

# Streamlit 실행 (PYTHONPATH와 절대 경로 사용)
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"
cd "${PROJECT_ROOT}/0_통합_대시보드"

# 통합 대시보드 실행 (단일 포트)
python3 -m streamlit run app.py \
    --server.port 8000 \
    --browser.gatherUsageStats false \
    --server.headless true \
    --server.fileWatcherType none
