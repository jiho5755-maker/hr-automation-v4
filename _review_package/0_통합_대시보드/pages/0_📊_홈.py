"""
홈 대시보드 - 통합 관리 센터
전체 현황 및 중요 알림 표시
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date, timedelta

# shared 모듈 import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.database import get_db, get_all_employees, get_company_profile
from shared.design import apply_design
from shared.utils import show_success, show_info

# 디자인 적용
apply_design()


# ============================================================================
# 메인 함수
# ============================================================================

def show():
    """홈 대시보드 표시"""
    
    # 타이틀
    st.markdown('<div class="main-title">🏢 인사팀 자동화 - 통합 관리 센터</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">데이터 입력 및 관리 허브</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # ========================================================================
    # 전체 현황
    # ========================================================================
    
    st.markdown("### 📊 전체 현황")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 🚀 최적화: 한 번의 쿼리로 모든 통계 가져오기
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN is_pregnant = 1 THEN 1 ELSE 0 END) as pregnant,
                (SELECT COUNT(*) FROM work_logs WHERE work_date >= date('now', 'start of month')) as work_logs
            FROM employees
        """)
        
        stats = cursor.fetchone()
        total_count = stats[0]
        active_count = stats[1]
        pregnant_count = stats[2]
        work_log_count = stats[3]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 재직 직원", f"{active_count}명", f"전체 {total_count}명")
    
    with col2:
        st.metric("🤰 임신/출산 관리", f"{pregnant_count}명")
    
    with col3:
        st.metric("🏠 이번 달 근무 로그", f"{work_log_count}건")
    
    with col4:
        # 급여 설정 통계
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM payroll_settings")
                payroll_count = cursor.fetchone()[0]
                st.metric("💰 급여 설정", f"{payroll_count}명")
        except:
            st.metric("💰 급여 설정", "0명")
    
    st.divider()
    
    # ========================================================================
    # 회사 정보
    # ========================================================================
    
    st.markdown("### 🏢 회사 정보")
    
    company = get_company_profile()
    
    if company:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"""
            **회사명**: {company.get('company_name', 'N/A')}  
            **대표자**: {company.get('ceo_name', 'N/A')}
            """)
        
        with col2:
            st.info(f"""
            **업종**: {company.get('industry', 'N/A')}  
            **직원 수**: {company.get('employee_count', 'N/A')}명
            """)
        
        with col3:
            st.info(f"""
            **사업자번호**: {company.get('business_number', 'N/A')}  
            **연매출**: {company.get('annual_revenue', 'N/A')}
            """)
    else:
        st.warning("⚠️ 회사 정보가 등록되지 않았습니다. '🏢 회사 정보 관리' 메뉴에서 등록하세요.")
    
    st.divider()
    
    # ========================================================================
    # 중요 알림
    # ========================================================================
    
    st.markdown("### 🔔 중요 알림")
    
    # 임신 중인 직원
    employees = get_all_employees(active_only=True)
    pregnant_employees = [emp for emp in employees if emp.get('is_pregnant')]
    
    if pregnant_employees:
        st.warning(f"""
        **🤰 임신 중인 직원**: {len(pregnant_employees)}명
        
        {', '.join([emp['name'] for emp in pregnant_employees])}
        
        💡 '🤰 출산육아 날짜 관리'에서 일정을 확인하세요.
        """)
    
    # 급여 미설정 직원
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT e.name FROM employees e
                LEFT JOIN payroll_settings ps ON e.emp_id = ps.emp_id
                WHERE e.is_active = 1 AND ps.emp_id IS NULL
            """)
            unset_payroll = cursor.fetchall()
            
            if unset_payroll:
                st.info(f"""
                **💰 급여 미설정 직원**: {len(unset_payroll)}명
                
                {', '.join([row[0] for row in unset_payroll])}
                
                💡 '💰 급여 정보 관리'에서 급여를 설정하세요.
                """)
        except:
            pass
    
    st.divider()
    
    # ========================================================================
    # 기능 실행 앱 링크
    # ========================================================================
    
    st.markdown("### 🔗 기능 실행 앱")
    
    st.info("""
    **데이터 입력이 완료되었나요?**  
    아래 앱에서 기능을 실행하세요!
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **👶 출산육아 자동화**
        
        📍 http://localhost:8501
        
        - 재택근무 로그 생성
        - 지원금 계산
        - 정부 서식 PDF
        """)
    
    with col2:
        st.markdown("""
        **🏠 재택근무 관리**
        
        📍 http://localhost:8503
        
        - 근무 기록
        - 캘린더
        - 통계 리포트
        """)
    
    with col3:
        st.markdown("""
        **💰 급여관리 자동화**
        
        📍 http://localhost:8505
        
        - 급여 계산
        - 명세서 PDF
        - 급여대장 Excel
        """)
    
    st.divider()
    
    # ========================================================================
    # 빠른 시작 가이드
    # ========================================================================
    
    st.markdown("### 💡 빠른 시작 가이드")
    
    st.success("""
    **1단계: 데이터 입력 (여기, 포트 8000)**
    1. 👥 직원 관리 → 직원 추가
    2. 🏢 회사 정보 관리 → 회사 정보 입력
    3. 🤰 출산육아 날짜 관리 → 출산 예정 직원 일정 입력
    4. 💰 급여 정보 관리 → 직원별 기본 급여 설정
    
    **2단계: 기능 실행 (다른 포트의 앱들)**
    - 출산육아 앱 (8501) → 로그 생성, PDF 생성
    - 재택근무 앱 (8503) → 근무 기록, 리포트
    - 급여관리 앱 (8505) → 급여 계산, 명세서 생성
    """)


# ============================================================================
# 페이지 실행
# ============================================================================

show()
