"""
급여관리 자동화 페이지 (개선 예정)
Payroll Management Page (Work in Progress)

4대보험 자동 계산, 급여명세서 생성, 급여대장 관리
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import date

# 상위 디렉토리의 shared 모듈 import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.database import get_db, get_all_employees, get_employee_by_id
from shared.utils import show_success, show_error, show_info, format_currency
from shared.design import apply_design

# 디자인 적용
apply_design()


# ============================================================================
# 메인 함수
# ============================================================================

def show():
    """급여관리 페이지 메인 함수"""
    
    # 타이틀
    st.markdown('<div class="main-title">💰 급여관리 자동화</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">4대보험 자동 계산, 급여명세서 생성</div>', unsafe_allow_html=True)
    
    # 작업 중 안내
    st.warning("""
    ⚠️ **이 페이지는 현재 개선 작업 중입니다.**
    
    **기존 문제점:**
    - 계산 로직이 명세서에 자동 반영되지 않음
    - 4대보험, 소득세, 연차, 초과근무 계산 개선 필요
    - UI/UX 개선 필요
    
    **개선 계획:**
    - Phase 5에서 별도로 구현 예정
    - 실제 데이터로 철저한 검증 필요
    - 계산 결과 → 명세서 자동 반영 구현
    
    **임시 대안:**
    기존 급여관리 모듈 사용:
    ```bash
    cd 5_급여관리_자동화
    streamlit run app.py --server.port 8505
    ```
    """)
    
    st.divider()
    
    # 기본 UI (템플릿)
    st.markdown("### 📋 급여 관리 (템플릿)")
    
    # 직원 목록
    employees = get_all_employees(active_only=True)
    
    if not employees:
        st.info("등록된 직원이 없습니다. '👥 직원 관리' 메뉴에서 직원을 추가하세요.")
        return
    
    # 직원 선택
    employee_options = {f"{emp['name']} ({emp.get('department', 'N/A')})": emp for emp in employees}
    
    selected_name = st.selectbox(
        "직원 선택",
        options=["직원을 선택하세요..."] + list(employee_options.keys())
    )
    
    if selected_name != "직원을 선택하세요...":
        selected_emp = employee_options[selected_name]
        
        st.success(f"**{selected_emp['name']}** 선택됨")
        
        # 탭으로 기능 구분 (템플릿)
        tab1, tab2, tab3 = st.tabs(["💰 급여 계산", "📄 명세서", "📊 급여대장"])
        
        with tab1:
            st.info("급여 계산 기능은 Phase 5에서 구현됩니다.")
        
        with tab2:
            st.info("명세서 생성 기능은 Phase 5에서 구현됩니다.")
        
        with tab3:
            st.info("급여대장 기능은 Phase 5에서 구현됩니다.")
    
    st.divider()
    
    # 참고 정보
    st.markdown("### 📚 참고 자료")
    
    st.markdown("""
    **Phase 5 구현 시 포함될 기능:**
    
    1. **급여 설정**
       - 기본급, 수당 설정
       - 4대보험 요율 설정
       - 소득세 구간 설정
    
    2. **급여 계산**
       - 기본급 + 수당 계산
       - 4대보험 자동 계산
       - 소득세 자동 계산
       - 초과근무 수당 계산
       - 연차 수당 계산
    
    3. **급여 명세서**
       - 계산 결과 자동 반영 ✨
       - PDF/Excel 다운로드
       - 이메일 발송
    
    4. **급여 대장**
       - 월별 급여 대장 생성
       - 부서별 통계
       - 연간 통계
    """)


# ============================================================================
# 페이지 실행
# ============================================================================

show()
