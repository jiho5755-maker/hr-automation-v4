#!/bin/bash

# 통합 대시보드 실행 스크립트

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏢 인사팀 자동화 통합 대시보드"
echo "   HR Automation Integrated Dashboard"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 시스템을 시작하는 중..."
echo ""

# 디렉토리 이동
cd "$(dirname "$0")"

# 의존성 확인
echo "🔍 패키지 확인 중..."
if ! python3 -c "import streamlit, pandas" 2>/dev/null; then
    echo "⚠️  필수 패키지 설치 중..."
    pip3 install -q -r requirements.txt
    echo "✅ 패키지 설치 완료"
fi

echo "✅ 시스템 로딩 완료"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 브라우저가 곧 열립니다!"
echo "📍 주소: http://localhost:8000"
echo ""
echo "🔐 로그인 정보:"
echo "   관리자: admin / admin1234"
echo "   테스트: test / test1234"
echo ""
echo "💡 모든 자동화 시스템을 한 곳에서 관리하세요!"
echo "⚠️  종료하려면 이 창에서 Ctrl+C를 누르세요"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Streamlit 실행
python3 -m streamlit run app.py --server.port 8000
