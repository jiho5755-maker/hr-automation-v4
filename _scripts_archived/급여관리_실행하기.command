#!/bin/bash

# 현재 스크립트의 디렉토리로 이동
cd "$(dirname "$0")"

echo "======================================"
echo "💰 급여관리 자동화 시작"
echo "======================================"
echo ""

# Python 가상환경 확인
if [ -d "../venv" ]; then
    echo "✅ 가상환경 발견"
    source ../venv/bin/activate
elif [ -d "venv" ]; then
    echo "✅ 가상환경 발견"
    source venv/bin/activate
else
    echo "⚠️  가상환경이 없습니다. 전역 Python 사용"
fi

# 필요한 패키지 설치 확인
echo "📦 패키지 확인 중..."
pip install -q -r requirements.txt

# 데이터베이스 초기화
echo "🗄️  데이터베이스 초기화 중..."
python -c "from database import init_payroll_tables; init_payroll_tables(); print('✅ 데이터베이스 초기화 완료')"

echo ""
echo "======================================"
echo "🚀 급여관리 자동화 실행 중..."
echo "======================================"
echo ""
echo "📍 접속 주소: http://localhost:8505"
echo ""
echo "💡 종료하려면 Ctrl+C를 누르세요"
echo ""

# Streamlit 앱 실행
streamlit run app.py --server.port 8505 --server.headless true

# 실행 후
echo ""
echo "======================================"
echo "👋 급여관리 자동화 종료"
echo "======================================"
