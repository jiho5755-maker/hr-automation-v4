#!/bin/bash

# 연말정산 자동화 - 웹 UI
# 더블클릭하면 자동으로 실행됩니다

clear
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💰 연말정산 자동화 - PDF 파서"
echo "   국세청 간소화 PDF 자동 추출 (웹 UI)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 시스템을 시작하는 중..."
echo ""

# 디렉토리 이동
cd "$(dirname "$0")"

# 의존성 확인
echo "🔍 패키지 확인 중..."
if ! python3 -c "import streamlit, pdfplumber, pandas" 2>/dev/null; then
    echo "⚠️  필수 패키지 설치 중..."
    pip3 install -q streamlit pdfplumber pandas openpyxl
    echo "✅ 패키지 설치 완료"
fi

echo "✅ 시스템 로딩 완료"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 브라우저가 곧 열립니다!"
echo "📍 주소: http://localhost:8502"
echo ""
echo "💡 기능: PDF 업로드 | 자동 파싱 | 엑셀 다운로드"
echo "⚠️  종료하려면 이 창에서 Ctrl+C를 누르세요"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Streamlit 실행 (포트 8502)
python3 -m streamlit run app.py --server.port 8502
