"""
인사팀 자동화 - 통합 데이터 관리 센터 v4.0
HR Automation - Integrated Data Management Center

📊 데이터 입력: 직원, 회사, 출산육아, 급여 정보 통합 관리
🔄 자동 동기화: 모든 앱에서 입력한 데이터 자동 사용
💡 역할 분리: 대시보드(데이터 입력) + 기능 앱(계산/생성)
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date

# 상위 디렉토리의 shared 모듈 import (최우선 순위)
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database import get_db, get_company_profile, init_master_database
from shared.auth import authenticate_user, init_default_users, add_system_log
from shared.design import apply_design
from shared.utils import show_success, show_error, format_currency, get_korean_weekday


# ============================================================================
# 페이지 설정
# ============================================================================

st.set_page_config(
    page_title="인사팀 자동화 - 데이터 관리 센터",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 모던 그린 미니멀 디자인 적용
apply_design()


# ============================================================================
# 세션 상태 초기화
# ============================================================================

def init_session_state():
    """세션 상태 초기화 - PRD §8.2 State Lifecycle"""
    # SL-1: 로그인 상태
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # SL-2: 사용자 정보
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # SL-3: 선택된 직원 (모든 페이지에서 공유)
    if 'current_employee' not in st.session_state:
        st.session_state.current_employee = None
    
    # SL-9: 현재 페이지
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "대시보드"


# ============================================================================
# 로그인 페이지
# ============================================================================

def show_login_page():
    """로그인 페이지 - PRD §5.1.4"""
    st.markdown('<div class="main-title">📊 인사팀 자동화 - 데이터 관리 센터</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">HR Automation Data Management Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">✨ 통합 데이터 입력 → 모든 앱에서 자동 사용</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 로그인")
        
        with st.form("login_form"):
            username = st.text_input("사용자명", placeholder="admin")
            password = st.text_input("비밀번호", type="password", placeholder="비밀번호 입력")
            submit = st.form_submit_button("로그인", use_container_width=True, type="primary")
            
            if submit:
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        # SL-1, SL-2: 로그인 상태 업데이트
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        
                        # O-9: 시스템 로그 기록
                        add_system_log(username, "로그인", "auth", f"사용자 {username} 로그인 성공")
                        
                        # V-1: User sees
                        show_success(f"환영합니다, {user['username']}님!")
                        st.rerun()
                    else:
                        # V-1: User sees error
                        show_error("로그인 실패: 사용자명 또는 비밀번호가 올바르지 않습니다.")
                else:
                    st.warning("사용자명과 비밀번호를 입력하세요.")
        
        st.divider()
        
        st.info("""
        **💡 테스트 계정**  
        - 관리자: `admin` / `admin1234`  
        - 테스트: `test` / `test1234`
        
        **🆕 v4.0 데이터 관리 센터**  
        ✅ 포트 8000: 모든 데이터 통합 입력  
        ✅ 다른 앱들: 입력된 데이터 자동 사용  
        ✅ 급여 정보 → 급여관리 앱에서 명세서 자동 생성  
        """)


# ============================================================================
# Streamlit 자동 멀티페이지 사용 (pages/ 폴더 자동 인식)
# ============================================================================
# st.Page는 Streamlit 1.32.0에서 미지원
# pages/ 폴더의 파일들이 자동으로 사이드바에 표시됨


# ============================================================================
# 로그아웃 처리
# ============================================================================

def handle_logout():
    """로그아웃 처리 - PRD §3.7 Transition: 로그아웃"""
    if st.session_state.logged_in:
        username = st.session_state.user.get('username', 'unknown') if st.session_state.user else 'unknown'
        
        # O-9: 시스템 로그 기록
        add_system_log(username, "로그아웃", "auth", f"사용자 {username} 로그아웃")
        
        # SL-1~SL-9: 모든 세션 상태 제거
        st.session_state.clear()
        
        show_success("로그아웃되었습니다.")
        st.rerun()


# ============================================================================
# 사이드바
# ============================================================================

def show_sidebar():
    """사이드바 표시"""
    if not st.session_state.logged_in:
        return
    
    with st.sidebar:
        # 사용자 정보
        user = st.session_state.user
        if user:
            st.markdown(f"### 👤 {user['username']}")
            role_emoji = {
                'admin': '👑',
                'hr': '💼',
                'manager': '📊',
                'employee': '👤'
            }.get(user['role'], '👤')
            st.caption(f"{role_emoji} 역할: {user['role']}")
        
        st.divider()
        
        # 선택된 직원 정보 (SL-3)
        if st.session_state.current_employee:
            emp = st.session_state.current_employee
            st.info(f"**선택된 직원**\n\n👤 {emp.get('name', 'N/A')}\n📦 {emp.get('department', 'N/A')}")
        
        st.divider()
        
        # 로그아웃 버튼
        if st.button("🚪 로그아웃", use_container_width=True, type="secondary"):
            handle_logout()
        
        st.divider()
        
        # 현재 시각
        now = datetime.now()
        st.caption(f"🕐 {now.strftime('%Y-%m-%d %H:%M:%S')}")
        st.caption(f"📅 {get_korean_weekday(date.today())}요일")
        
        st.divider()
        
        # 버전 정보
        st.caption("**버전**: v4.0.0 데이터센터")
        st.caption("**포트**: 8000 (데이터 입력)")
        
        st.divider()
        
        # 다른 앱 링크
        st.caption("**🔗 기능 앱:**")
        st.caption("출산육아: :8501")
        st.caption("재택근무: :8503")
        st.caption("급여관리: :8505")


# ============================================================================
# 메인 함수
# ============================================================================

def main():
    """메인 함수 - PRD §5.1"""
    # DB 및 사용자 초기화
    init_master_database()
    init_default_users()
    
    # 세션 상태 초기화
    init_session_state()
    
    # 로그인 체크
    if not st.session_state.logged_in:
        show_login_page()
        return
    
    # 사이드바 표시
    show_sidebar()
    
    # 메인 페이지 (Streamlit이 pages/ 폴더를 자동으로 사이드바에 표시)
    st.markdown('<div class="main-title">📊 인사팀 자동화 - 데이터 관리 센터</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">데이터 입력 및 관리 허브</div>', unsafe_allow_html=True)
    
    st.info("""
    **💡 사용 방법**
    
    좌측 사이드바에서 메뉴를 선택하세요:
    - 📊 홈: 전체 현황
    - 👥 직원 관리: 직원 정보 입력
    - 🏢 회사 정보: 회사 정보 관리
    - 🤰 출산육아 일정: 출산 일정 관리
    - 💰 급여 정보: 급여 설정
    - ⚙️ 설정: 시스템 정보
    """)


# ============================================================================
# 실행
# ============================================================================

if __name__ == "__main__":
    main()
