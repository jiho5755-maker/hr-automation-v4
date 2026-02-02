#!/bin/bash

cd "$(dirname "$0")"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💰 급여관리 자동화"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 주소: http://localhost:8505"
echo ""
echo "✨ 주요 기능:"
echo "  - 급여 자동 계산"
echo "  - 4대보험 자동 계산"
echo "  - 급여명세서 PDF 생성"
echo "  - 급여대장 Excel 생성"
echo ""
echo "🛑 종료: Ctrl+C"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 -m streamlit run app.py --server.port 8505
