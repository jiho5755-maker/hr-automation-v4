#!/bin/bash

cd "$(dirname "$0")"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "👶 출산육아 자동화"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 주소: http://localhost:8501"
echo ""
echo "✨ 주요 기능:"
echo "  - 재택근무 증빙 로그 생성"
echo "  - 지원금 시뮬레이터"
echo "  - 정부 서식 PDF 생성"
echo "  - 대체인력 관리"
echo ""
echo "🛑 종료: Ctrl+C"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 -m streamlit run app.py --server.port 8501
