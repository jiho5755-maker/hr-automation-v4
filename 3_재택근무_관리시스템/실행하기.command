#!/bin/bash

cd "$(dirname "$0")"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏠 재택근무 관리 시스템"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 주소: http://localhost:8503"
echo ""
echo "✨ 주요 기능:"
echo "  - 직원별 근무 기록"
echo "  - 월별 캘린더"
echo "  - 통계 및 리포트"
echo ""
echo "🛑 종료: Ctrl+C"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 -m streamlit run app.py --server.port 8503
