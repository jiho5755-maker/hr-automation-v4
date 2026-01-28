#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 완전한 재시작 스크립트"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. 모든 Streamlit 프로세스 종료
echo "1️⃣ Streamlit 프로세스 종료 중..."
pkill -9 streamlit 2>/dev/null && echo "   ✅ 종료 완료" || echo "   ℹ️  실행 중인 프로세스 없음"
sleep 1

# 2. Python 캐시 삭제
echo ""
echo "2️⃣ Python 캐시 삭제 중..."
cd "/Users/jangjiho/Documents/인사팀_자동화_마스터"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
echo "   ✅ 캐시 삭제 완료"

# 3. Import 테스트
echo ""
echo "3️⃣ Import 테스트 중..."
python3 -c "import sys; sys.path.insert(0, '.'); from shared.utils import show_success, format_currency, get_korean_weekday; print('   ✅ 모든 함수 import 성공!')" 2>&1

# 4. 통합 대시보드 실행
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 통합 대시보드 시작!"
echo "📍 주소: http://localhost:8000"
echo ""
echo "⚠️  브라우저에서:"
echo "   1. 이전 localhost 탭을 모두 닫으세요"
echo "   2. 새 탭에서 http://localhost:8000 접속"
echo ""
echo "⚠️  종료: Ctrl+C"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 5. Streamlit 실행
cd 0_통합_대시보드
python3 -m streamlit run app.py --server.port 8000 --browser.gatherUsageStats false
