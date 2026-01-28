#!/bin/bash

# 재택근무 관리 시스템 v2.0 (회사 공식 시스템)
# 더블클릭하면 자동으로 실행됩니다

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏢 재택근무 관리 시스템 v2.0"
echo "   Remote Work Management System"
echo "   Powered by Argon2 | Professional Edition"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 시스템을 시작하는 중..."
echo ""

# 디렉토리 이동
cd "$(dirname "$0")"

# 의존성 확인
echo "🔍 시스템 패키지 확인 중..."
if ! python3 -c "import streamlit, argon2, pandas" 2>/dev/null; then
    echo "⚠️  필수 패키지 설치 중..."
    pip3 install -q streamlit argon2-cffi pandas openpyxl
    echo "✅ 패키지 설치 완료"
fi

# Python 확인
echo "✅ 회사 공식 시스템 로딩 완료"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 브라우저가 곧 열립니다!"
echo "📍 주소: http://localhost:8503"
echo ""
echo "🔐 로그인 정보 (최초 사용)"
echo "   관리자 ID: admin"
echo "   비밀번호: admin1234"
echo ""
echo "   일반 직원 ID: songmi"
echo "   비밀번호: songmi1234"
echo ""
echo "💡 기능: 일괄 입력 | 시간 랜덤화 | 증빙 보고서"
echo "⚠️  종료하려면 이 창에서 Ctrl+C를 누르세요"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Streamlit 실행
python3 -m streamlit run app.py --server.port 8503
