#!/bin/bash

# 출산·육아기 행정 업무 자동화 툴
# 더블클릭하면 자동으로 실행됩니다

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "👶 출산·육아기 행정 업무 자동화 툴"
echo "   2026년 개정 노동법 기준"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 시스템을 시작하는 중..."
echo ""

# 디렉토리 이동
cd "$(dirname "$0")"

# 의존성 확인
echo "🔍 패키지 확인 중..."
if ! python3 -c "import streamlit, pandas, openpyxl, docx, reportlab" 2>/dev/null; then
    echo "⚠️  필수 패키지 설치 중..."
    pip3 install -q -r requirements.txt
    echo "✅ 패키지 설치 완료"
fi

echo "✅ 시스템 로딩 완료"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 브라우저가 곧 열립니다!"
echo "📍 주소: http://localhost:8501"
echo ""
echo "💡 기능: 재택근무 로그 | 지원금 계산 | 정부 서식"
echo "⚠️  종료하려면 이 창에서 Ctrl+C를 누르세요"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Streamlit 실행
python3 -m streamlit run app.py --server.port 8501
