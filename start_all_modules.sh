#!/bin/bash

###############################################################################
# 전체 모듈 실행 스크립트 (안정성 우선)
# 각 모듈을 독립적인 포트로 실행하여 크래시 격리
###############################################################################

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏢 인사팀 자동화 시스템 - 전체 모듈 실행"
echo "   (안정성 우선: 개별 포트 방식)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 프로젝트 루트로 이동
cd "$(dirname "$0")"
PROJECT_ROOT="${PWD}"

# 기존 프로세스 정리
echo "🔍 Step 1: 기존 프로세스 정리..."
for PORT in 8000 8501 8502 8503 8504 8505; do
    lsof -ti:${PORT} | xargs kill -9 2>/dev/null
done
sleep 1
echo "   ✅ 프로세스 정리 완료"
echo ""

# Python 캐시 삭제
echo "🗑️  Step 2: Python 캐시 삭제..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
echo "   ✅ 캐시 삭제 완료"
echo ""

# 환경 변수 설정
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

# 로그 디렉토리 생성
mkdir -p logs

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 모듈 실행 중..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. 통합 대시보드
echo "📊 1/4 통합 대시보드 시작 (포트 8000)..."
cd "${PROJECT_ROOT}/0_통합_대시보드"
nohup python3 -m streamlit run app.py --server.port 8000 --browser.gatherUsageStats false > "${PROJECT_ROOT}/logs/dashboard.log" 2>&1 &
echo "   ✅ PID: $!"
sleep 2

# 2. 출산육아 자동화
echo "👶 2/4 출산육아 자동화 시작 (포트 8501)..."
cd "${PROJECT_ROOT}/1_출산육아_자동화"
nohup python3 -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false > "${PROJECT_ROOT}/logs/maternity.log" 2>&1 &
echo "   ✅ PID: $!"
sleep 2

# 3. 재택근무 관리
echo "🏠 3/4 재택근무 관리 시작 (포트 8503)..."
cd "${PROJECT_ROOT}/3_재택근무_관리시스템"
nohup python3 -m streamlit run app.py --server.port 8503 --browser.gatherUsageStats false > "${PROJECT_ROOT}/logs/remote_work.log" 2>&1 &
echo "   ✅ PID: $!"
sleep 2

# 4. 급여관리 자동화
echo "💰 4/4 급여관리 자동화 시작 (포트 8505)..."
cd "${PROJECT_ROOT}/5_급여관리_자동화"
nohup python3 -m streamlit run app.py --server.port 8505 --browser.gatherUsageStats false > "${PROJECT_ROOT}/logs/payroll.log" 2>&1 &
echo "   ✅ PID: $!"
sleep 2

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 모든 모듈 실행 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 접속 주소:"
echo "   - 통합 대시보드:   http://localhost:8000"
echo "   - 출산육아 자동화: http://localhost:8501"
echo "   - 재택근무 관리:   http://localhost:8503"
echo "   - 급여관리 자동화: http://localhost:8505"
echo ""
echo "📊 로그 파일 위치:"
echo "   ${PROJECT_ROOT}/logs/"
echo ""
echo "🛑 전체 종료:"
echo "   ./stop_all_modules.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 상태 확인
sleep 3
echo "🔍 실행 상태 확인:"
for PORT in 8000 8501 8503 8505; do
    if lsof -i:${PORT} > /dev/null 2>&1; then
        echo "   ✅ 포트 ${PORT}: 실행 중"
    else
        echo "   ❌ 포트 ${PORT}: 실행 실패"
    fi
done
echo ""
