"""
출산육아 자동화 페이지 (안정성 개선 버전)
Maternity & Childcare Automation Page

별도 포트 실행 권장
"""

import streamlit as st
import sys
from pathlib import Path

# 상위 디렉토리의 shared 모듈 import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.design import apply_design

# 디자인 적용
apply_design()


def show():
    """출산육아 페이지 메인 함수"""
    
    # 타이틀
    st.markdown('<div class="main-title">👶 출산·육아 자동화</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">재택근무 로그, 지원금 계산, 정부 서식 자동 생성</div>', unsafe_allow_html=True)
    
    # 안정성 개선 안내
    st.warning("""
    ⚠️ **안정성 개선을 위해 별도 실행 권장**
    
    출산육아 모듈은 복잡한 PDF/DOCX 처리로 인해 통합 환경에서 크래시가 발생할 수 있습니다.
    
    **해결 방법:** 아래 명령어로 별도 포트에서 안정적으로 실행하세요.
    """)
    
    st.divider()
    
    # 별도 실행 안내
    st.markdown("### 🚀 출산육아 모듈 별도 실행")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 터미널에서 실행:")
        st.code("""cd /Users/jangjiho/Documents/인사팀_자동화_마스터/1_출산육아_자동화
streamlit run app.py --server.port 8501""", language="bash")
        
        st.info("""
        **실행 후 브라우저에서:**  
        👉 **http://localhost:8501**
        
        ✅ 통합 DB를 사용하므로 '👥 직원 관리'에서 추가한 직원 정보가 자동으로 동기화됩니다!
        """)
    
    with col2:
        st.markdown("#### 주요 기능:")
        st.markdown("""
        - 📝 **재택근무 로그 생성**  
          스마트 업무일지 자동 작성
        
        - 💰 **지원금 자동 계산**  
          출산/육아 지원금 예상 금액
        
        - 📄 **정부 서식 생성**  
          PDF/DOCX 자동 생성
        
        - 📊 **대체인력 관리**  
          인수인계 일정 관리
        """)
    
    st.divider()
    
    # 홈서버 배포 안내
    st.markdown("### 🏠 홈서버 배포 권장 방안")
    
    st.success("""
    **더 안정적인 운영을 위한 방법:**
    
    현재 홈서버를 구축하고 계시다면, 아래 방법을 권장드립니다:
    
    #### 1️⃣ Docker Compose 방식 (권장)
    - 각 모듈을 독립적인 컨테이너로 실행
    - 안정성과 확장성 향상
    - 자동 재시작 및 로그 관리
    
    #### 2️⃣ Nginx 리버스 프록시
    - 단일 도메인/포트로 모든 모듈 접근
    - 예: `yourdomain.com/maternity` → 포트 8501
    - 예: `yourdomain.com/payroll` → 포트 8505
    
    #### 3️⃣ 개별 포트 실행
    - 각 모듈을 별도 포트로 안정적으로 실행
    - 크래시 시 다른 모듈에 영향 없음
    """)
    
    with st.expander("📖 Docker Compose 설정 예시 보기"):
        st.code("""# docker-compose.yml
version: '3.8'

services:
  dashboard:
    build: ./0_통합_대시보드
    ports:
      - "8000:8501"
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./hr_master.db:/app/hr_master.db
      - ./shared:/app/shared

  maternity:
    build: ./1_출산육아_자동화
    ports:
      - "8501:8501"
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./hr_master.db:/app/hr_master.db
      - ./shared:/app/shared

  remote_work:
    build: ./3_재택근무_관리시스템
    ports:
      - "8503:8501"
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./hr_master.db:/app/hr_master.db
      - ./shared:/app/shared

  payroll:
    build: ./5_급여관리_자동화
    ports:
      - "8505:8501"
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./hr_master.db:/app/hr_master.db
      - ./shared:/app/shared

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - dashboard
      - maternity
      - remote_work
      - payroll
""", language="yaml")
    
    with st.expander("📖 Nginx 설정 예시 보기"):
        st.code("""# nginx/nginx.conf
http {
    upstream dashboard {
        server dashboard:8501;
    }
    
    upstream maternity {
        server maternity:8501;
    }
    
    server {
        listen 80;
        
        location / {
            proxy_pass http://dashboard;
            proxy_set_header Host $host;
        }
        
        location /maternity/ {
            proxy_pass http://maternity/;
            proxy_set_header Host $host;
        }
        
        # 기타 모듈...
    }
}
""", language="nginx")
    
    st.divider()
    
    # 지원 안내
    st.markdown("### 💬 도움이 필요하신가요?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **📚 문서 참고:**
        - `docker-compose.yml` (프로젝트 루트)
        - `nginx/nginx.conf`
        - `README_DEPLOY.md`
        """)
    
    with col2:
        st.success("""
        **🚀 빠른 시작:**
        1. 출산육아 모듈 별도 실행 (위 명령어)
        2. 홈서버 배포 계획 수립
        3. Docker Compose 설정 (선택)
        """)


# 페이지 실행
show()
