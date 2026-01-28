"""
인사팀 자동화 통합 대시보드 v4.0
HR Automation Integrated Dashboard

✨ 완전 통합: 단일 포트(8000)에서 모든 모듈 실행
🔄 실시간 동기화: 직원 정보 한 번 입력, 모든 모듈 자동 반영
💰 급여 자동화: 계산 결과 → 명세서 자동 반영
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
    page_title="인사팀 자동화 통합 시스템 v4.0",
    page_icon="🏢",
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
    st.markdown('<div class="main-title">🏢 인사팀 자동화 통합 시스템 v4.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">HR Automation Integrated System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">✨ 완전 통합: 하나의 포트로 모든 업무 처리</div>', unsafe_allow_html=True)
    
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
        
        **🆕 v4.0 새로운 기능**  
        ✅ 단일 포트(8000)로 모든 모듈 통합  
        ✅ 직원 정보 한 번 입력, 자동 동기화  
        ✅ 급여 계산 → 명세서 자동 반영  
        """)


# ============================================================================
# 페이지 정의 - PRD §5.1
# ============================================================================

# 기존 Streamlit 멀티페이지 방식 사용 (st.Page 없이)
# pages/ 폴더의 파일명이 자동으로 사이드바 메뉴가 됨


# ============================================================================
# 홈 대시보드
# ============================================================================

def show_home_dashboard():
    """홈 대시보드 표시"""
    
    # 타이틀
    st.markdown('<div class="main-title">📊 통합 대시보드</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">전체 인사 현황을 한눈에</div>', unsafe_allow_html=True)
    
    # 상단 메트릭
    col1, col2, col3, col4 = st.columns(4)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 직원 수 (재직/전체)
        cursor.execute("SELECT COUNT(*) FROM employees WHERE is_active = 1")
        active_emp = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM employees")
        total_emp = cursor.fetchone()[0]
        
        # 특별 관리 직원
        cursor.execute("""
            SELECT COUNT(*) FROM employees 
            WHERE (is_pregnant = 1 OR is_on_leave = 1) AND is_active = 1
        """)
        special_emp = cursor.fetchone()[0]
        
        # 근무 로그
        cursor.execute("""
            SELECT COUNT(*) FROM work_logs 
            WHERE work_date >= date('now', '-30 days')
        """)
        log_count = cursor.fetchone()[0]
        
        # 예상 지원금
        try:
            cursor.execute("""
                SELECT SUM(expected_amount) FROM applications 
                WHERE status != '반려'
            """)
            expected = cursor.fetchone()[0] or 0
            cursor.execute("SELECT COUNT(*) FROM applications")
            app_count = cursor.fetchone()[0]
        except:
            expected = 0
            app_count = 0
    
    with col1:
        st.metric("👥 등록 직원", f"{active_emp}명", delta=f"전체 {total_emp}명")
    with col2:
        st.metric("🤰 특별 관리", f"{special_emp}명", delta="임신/출산/휴직")
    with col3:
        st.metric("🏠 이번 달 근무 로그", f"{log_count}건")
    with col4:
        st.metric("💰 예상 지원금", format_currency(expected), delta=f"{app_count}건 신청")
    
    st.divider()
    
    # 회사 정보
    company = get_company_profile()
    if company:
        st.markdown("### 🏢 회사 정보")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**회사명**: {company.get('company_name', 'N/A')}")
            st.write(f"**대표자**: {company.get('ceo_name', 'N/A')}")
        with col2:
            st.write(f"**사업자번호**: {company.get('business_number', 'N/A')}")
            st.write(f"**업종**: {company.get('business_type', 'N/A')}")
        with col3:
            st.write(f"**직원 수**: {company.get('employee_count', 0)}명")
            st.write(f"**연매출**: {format_currency(company.get('annual_revenue', 0))}")
        st.divider()
    
    # 알림
    st.markdown("### 🔔 알림 및 할 일")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, department FROM employees WHERE is_on_leave = 1 AND is_active = 1")
        leave_emps = cursor.fetchall()
        cursor.execute("SELECT name, department FROM employees WHERE is_pregnant = 1 AND is_active = 1")
        pregnant_emps = cursor.fetchall()
    
    col1, col2 = st.columns(2)
    with col1:
        if pregnant_emps:
            st.info(f"🤰 **임신 중인 직원**: {len(pregnant_emps)}명")
            for emp in pregnant_emps:
                st.write(f"- {emp[0]} ({emp[1]})")
        else:
            st.success("✅ 현재 임신 중인 직원 없음")
    with col2:
        if leave_emps:
            st.warning(f"🏖️ **휴직 중인 직원**: {len(leave_emps)}명")
            for emp in leave_emps:
                st.write(f"- {emp[0]} ({emp[1]})")
        else:
            st.success("✅ 현재 휴직 중인 직원 없음")
    
    st.divider()
    
    # 안내
    st.markdown("### 🚀 통합된 자동화 모듈")
    st.info("""
    **✨ v4.0 완전 통합!**
    
    좌측 사이드바에서 원하는 모듈을 선택하세요:
    - **👥 직원 관리**: 모든 직원 정보를 한 곳에서 통합 관리
    - **👶 출산육아**: 재택근무 로그, 지원금 계산, 정부 서식 생성
    - **🏠 재택근무**: 일정 관리, 근무 기록 추적, 월간 리포트
    - **💰 급여관리**: 4대보험 자동 계산, 급여명세서 자동 생성
    
    **🔄 데이터 자동 동기화**: 직원 정보를 한 번만 입력하면 모든 모듈에 자동 반영됩니다!
    """)


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
    st.caption("**버전**: v4.0.0 통합")
    st.caption("**포트**: 8000 (단일)")


# ============================================================================
# 메인 함수
# ============================================================================

def main():
    """메인 함수 - 기존 Streamlit 멀티페이지 방식"""
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
    
    # 메인 컨텐츠 - 홈 대시보드 표시
    # (pages/ 폴더의 다른 페이지들은 Streamlit이 자동으로 사이드바에 추가함)
    show_home_dashboard()


# ============================================================================
# 실행
# ============================================================================

if __name__ == "__main__":
    main()
