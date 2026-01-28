FROM python:3.11-slim

# 작업 디렉토리
WORKDIR /app

# 시스템 패키지 설치 (한글 폰트 + 유틸리티)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    fonts-nanum \
    fontconfig \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -fv

# Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 로그 디렉토리 생성
RUN mkdir -p /app/logs

# 데이터베이스 디렉토리 권한 설정
RUN mkdir -p /app/data && chmod 777 /app/data

# 포트 노출
EXPOSE 8000

# 헬스체크 (40초 시작 대기)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/_stcore/health || exit 1

# Streamlit 실행 (최적화된 설정)
CMD ["streamlit", "run", "app.py", \
     "--server.port=8000", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none", \
     "--server.runOnSave=false", \
     "--browser.gatherUsageStats=false", \
     "--server.maxUploadSize=200"]
