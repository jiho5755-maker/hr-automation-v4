#!/bin/bash

cd "$(dirname "$0")"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏢 통합 대시보드 (직원 관리)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 주소: http://localhost:8000"
echo "🔐 로그인: admin / admin1234"
echo ""
echo "⭐ 직원 관리 메뉴에서 직원을 추가하세요!"
echo ""
echo "🛑 종료: Ctrl+C"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

streamlit run app.py --server.port 8000
