"""
홈 대시보드 페이지
Home Dashboard Page

전체 인사 현황을 한눈에 파악
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date

# 상위 디렉토리의 shared 모듈 import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.database import get_db, get_company_profile
from shared.utils import format_currency


# ============================================================================
# 홈 대시보드 - PRD §5.3
# ============================================================================

def show():
    """홈 대시보드 표시"""
    
    # 타이틀
    st.markdown('<div class="main-title">📊 통합 대시보드</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">전체 인사 현황을 한눈에</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # 상단 메트릭 - PRD §5.3.1
    # ========================================================================
    
    col1, col2, col3, col4 = st.columns(4)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 직원 수 (재직/전체)
        cursor.execute("SELECT COUNT(*) FROM employees WHERE is_active = 1")
        active_emp = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM employees")
        total_emp = cursor.fetchone()[0]
        
        # 특별 관리 직원 (임신/출산/휴직)
        cursor.execute("""
            SELECT COUNT(*) FROM employees 
            WHERE (is_pregnant = 1 OR is_on_leave = 1) AND is_active = 1
        """)
        special_emp = cursor.fetchone()[0]
        
        # 이번 달 근무 로그 수
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
    
    # ========================================================================
    # 회사 정보 - PRD §5.3.2
    # ========================================================================
    
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
    
    # ========================================================================
    # 알림 섹션 - PRD §5.3.3
    # ========================================================================
    
    st.markdown("### 🔔 알림 및 할 일")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 휴직 중인 직원
        cursor.execute("""
            SELECT name, department FROM employees 
            WHERE is_on_leave = 1 AND is_active = 1
        """)
        leave_emps = cursor.fetchall()
        
        # 임신 중인 직원
        cursor.execute("""
            SELECT name, department FROM employees 
            WHERE is_pregnant = 1 AND is_active = 1
        """)
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
    
    # ========================================================================
    # 통합 모듈 안내 - PRD §5.3.4
    # ========================================================================
    
    st.markdown("### 🚀 통합된 자동화 모듈")
    st.info("""
    **✨ v4.0 완전 통합!**
    
    이제 모든 모듈이 하나의 포트(8000)에서 실행됩니다.  
    좌측 사이드바에서 원하는 모듈을 선택하세요:
    
    - **👥 직원 관리**: 모든 직원 정보를 한 곳에서 통합 관리
    - **👶 출산육아**: 재택근무 로그, 지원금 계산, 정부 서식 생성
    - **🏠 재택근무**: 일정 관리, 근무 기록 추적, 월간 리포트
    - **💰 급여관리**: 4대보험 자동 계산, 급여명세서 자동 생성
    
    **🔄 데이터 자동 동기화**: 직원 정보를 한 번만 입력하면 모든 모듈에 자동 반영됩니다!
    """)
    
    st.divider()
    
    # ========================================================================
    # 최근 활동 - PRD §5.3.5
    # ========================================================================
    
    st.markdown("### 📈 최근 활동")
    
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT timestamp, username, action, module, details
                FROM system_logs
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            logs = cursor.fetchall()
        except:
            logs = []
    
    if logs:
        for log in logs:
            timestamp = log[0]
            username = log[1]
            action = log[2]
            module = log[3] or "시스템"
            
            st.text(f"[{timestamp}] {username} - {action} ({module})")
    else:
        st.info("아직 활동 내역이 없습니다.")


# ============================================================================
# 페이지 실행
# ============================================================================

show()
