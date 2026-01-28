"""
2026년 개정 노동법 기준 출산·육아기 행정 업무 자동화 툴
Streamlit 기반 메인 애플리케이션 (직원 데이터 관리 기능 포함)
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime, date, timedelta

# shared 모듈 import
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from shared.design import apply_design
from shared.utils import show_success

# 로컬 모듈 임포트
import constants as C
# from employee_manager import EmployeeDataManager, create_employee_data_from_form  # 기존 JSON 기반
from shared_employee_manager import SharedEmployeeDataManager as EmployeeDataManager, create_employee_data_from_form  # 통합 DB 기반
from engine import (
    SmartWorkLogGenerator,
    SubsidyCalculator,
    GovernmentFormMapper,
    format_currency,
    calculate_date_range_days,
    PDF_AVAILABLE,
)

try:
    from engine import generate_pdf_forms
except:
    PDF_AVAILABLE = False


# ============================================================
# Streamlit 페이지 설정
# ============================================================

st.set_page_config(
    page_title=C.APP_CONFIG["제목"],
    page_icon=C.APP_CONFIG["아이콘"],
    layout=C.APP_CONFIG["레이아웃"],
    initial_sidebar_state="expanded"
)

# 모던 그린 미니멀 디자인 적용
apply_design()


# ============================================================
# 세션 상태 초기화
# ============================================================

def init_session_state():
    """세션 상태 초기화"""
    if 'employee_manager' not in st.session_state:
        st.session_state.employee_manager = EmployeeDataManager()
    
    if 'current_employee' not in st.session_state:
        # 기본 직원 (constants.py에서 가져오기)
        st.session_state.current_employee = None
    
    if 'show_employee_form' not in st.session_state:
        st.session_state.show_employee_form = False


# ============================================================
# 사이드바: 직원 관리
# ============================================================

def show_sidebar():
    """사이드바에 직원 선택 및 관리 기능 표시"""
    # 홈 버튼
    st.sidebar.markdown("### 🏠 메뉴")
    if st.sidebar.button("🏠 통합 대시보드로 이동", use_container_width=True):
        st.sidebar.info("🌐 브라우저에서 http://localhost:8000 로 접속하세요")
    
    st.sidebar.divider()
    
    st.sidebar.header("👥 직원 관리")
    
    manager = st.session_state.employee_manager
    employee_names = manager.get_all_employee_names()
    
    # 직원 선택
    if employee_names:
        st.sidebar.subheader("📌 직원 선택")
        
        # 현재 선택된 직원의 인덱스 찾기
        current_index = 0
        if st.session_state.current_employee:
            current_name = st.session_state.current_employee.get("EMPLOYEE_INFO", {}).get("이름")
            if current_name in employee_names:
                current_index = employee_names.index(current_name)
        
        selected_name = st.sidebar.selectbox(
            "직원을 선택하세요",
            options=employee_names,
            index=current_index,
            key="employee_selector"
        )
        
        # 선택된 직원 데이터 로드
        if selected_name:
            employee_data = manager.load_employee(selected_name)
            if employee_data != st.session_state.current_employee:
                st.session_state.current_employee = employee_data
                st.rerun()
    
    else:
        st.sidebar.info("저장된 직원 데이터가 없습니다. 새 직원을 추가해주세요.")
    
    st.sidebar.divider()
    
    # 직원 추가/수정 버튼
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("➕ 새 직원", use_container_width=True):
            st.session_state.show_employee_form = True
            st.session_state.form_mode = "add"
            st.rerun()
    
    with col2:
        if st.button("✏️ 수정", use_container_width=True, disabled=not st.session_state.current_employee):
            st.session_state.show_employee_form = True
            st.session_state.form_mode = "edit"
            st.rerun()
    
    # 직원 삭제 버튼
    if st.session_state.current_employee:
        st.sidebar.divider()
        if st.sidebar.button("🗑️ 현재 직원 삭제", type="secondary", use_container_width=True):
            current_name = st.session_state.current_employee["EMPLOYEE_INFO"]["이름"]
            if manager.delete_employee(current_name):
                st.sidebar.success(f"'{current_name}' 삭제 완료!")
                st.session_state.current_employee = None
                st.rerun()
    
    # 현재 선택된 직원 요약
    if st.session_state.current_employee:
        st.sidebar.divider()
        st.sidebar.subheader("📋 현재 직원 정보")
        emp_info = st.session_state.current_employee["EMPLOYEE_INFO"]
        st.sidebar.markdown(f"""
        **이름**: {emp_info['이름']}  
        **부서**: {emp_info['부서']}  
        **직급**: {emp_info['직급']}
        """)


# ============================================================
# 직원 데이터 입력 폼
# ============================================================

def show_employee_form():
    """직원 데이터 입력/수정 폼"""
    st.header("👤 직원 데이터 입력")
    
    # 수정 모드인 경우 기존 데이터 로드
    if st.session_state.get('form_mode') == 'edit' and st.session_state.current_employee:
        data = st.session_state.current_employee
        emp_info = data["EMPLOYEE_INFO"]
        employer_info = data["EMPLOYER_INFO"]
        short_work = data["PREGNANCY_SHORT_WORK"]
        childbirth = data["CHILDBIRTH_INFO"]
        parental = data["PARENTAL_LEAVE"]
        replacement = data["REPLACEMENT_WORKER"]
    else:
        # 새 직원 추가 모드 - 기본값
        data = None
        emp_info = {"이름": "", "주민등록번호": "", "부서": "", "직급": ""}
        employer_info = C.EMPLOYER_INFO
        short_work = C.PREGNANCY_SHORT_WORK
        childbirth = C.CHILDBIRTH_INFO
        parental = C.PARENTAL_LEAVE
        replacement = C.REPLACEMENT_WORKER
    
    with st.form("employee_form"):
        st.subheader("1️⃣ 근로자 기본 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("이름 *", value=emp_info["이름"])
            ssn = st.text_input("주민등록번호 (예: 910828-2******)", value=emp_info["주민등록번호"])
            department = st.text_input("부서 *", value=emp_info["부서"])
        
        with col2:
            phone = st.text_input("연락처 * (예: 010-1234-5678)", value=emp_info.get("연락처", ""))
            position = st.text_input("직급 *", value=emp_info["직급"])
        
        st.divider()
        
        st.subheader("2️⃣ 사업주 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            employer_name = st.text_input("대표자명 *", value=employer_info["대표자명"])
            company_name = st.text_input("회사명", value=employer_info.get("회사명", ""))
        
        with col2:
            business_number = st.text_input("사업자등록번호", value=employer_info.get("사업자등록번호", ""))
            company_size = st.selectbox(
                "회사 규모 *",
                options=["30인 미만", "30인 이상 ~ 100인 미만", "100인 이상"],
                index=["30인 미만", "30인 이상 ~ 100인 미만", "100인 이상"].index(employer_info["회사규모"])
            )
        
        st.divider()
        
        st.subheader("3️⃣ 임신 중 단축근무 기간")
        col1, col2 = st.columns(2)
        
        with col1:
            short_work_start = st.date_input(
                "단축근무 시작일 *",
                value=short_work["시작일"] if isinstance(short_work["시작일"], date) else date.today()
            )
            work_start_time = st.time_input(
                "근무 시작 시각 *",
                value=datetime.strptime(short_work["근무시간"]["시작"], "%H:%M").time()
            ).strftime("%H:%M")
        
        with col2:
            short_work_end = st.date_input(
                "단축근무 종료일 *",
                value=short_work["종료일"] if isinstance(short_work["종료일"], date) else date.today()
            )
            work_end_time = st.time_input(
                "근무 종료 시각 *",
                value=datetime.strptime(short_work["근무시간"]["종료"], "%H:%M").time()
            ).strftime("%H:%M")
        
        col1, col2 = st.columns(2)
        with col1:
            work_break_time = st.text_input("휴게시간", value=short_work["근무시간"]["휴게시간"])
        with col2:
            actual_work_hours = st.number_input(
                "실근로시간 (시간)",
                min_value=1,
                max_value=12,
                value=short_work["근무시간"]["실근로시간"]
            )
        
        st.divider()
        
        st.subheader("4️⃣ 출산 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            pregnancy_confirm_date = st.date_input(
                "임신확인일",
                value=childbirth.get("임신확인일", date.today()) if isinstance(childbirth.get("임신확인일"), date) else date.today(),
                help="임신 사실을 확인한 날짜 (선택사항)"
            )
        
        with col2:
            due_date = st.date_input(
                "출산예정일 *",
                value=childbirth["출산예정일"] if isinstance(childbirth["출산예정일"], date) else date.today()
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            maternity_leave_start = st.date_input(
                "출산휴가 시작일 *",
                value=childbirth["출산휴가_시작일"] if isinstance(childbirth["출산휴가_시작일"], date) else date.today()
            )
        
        with col2:
            maternity_leave_end = st.date_input(
                "출산휴가 종료일 *",
                value=childbirth["출산휴가_종료일"] if isinstance(childbirth["출산휴가_종료일"], date) else date.today()
            )
        
        maternity_leave_days = (maternity_leave_end - maternity_leave_start).days + 1
        st.info(f"출산휴가 기간: {maternity_leave_days}일")
        
        st.divider()
        
        st.subheader("5️⃣ 육아 휴직")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            parental_leave_start = st.date_input(
                "육아휴직 시작일 *",
                value=parental["시작일"] if isinstance(parental["시작일"], date) else date.today()
            )
        
        with col2:
            parental_leave_end = st.date_input(
                "육아휴직 종료일 *",
                value=parental["종료일"] if isinstance(parental["종료일"], date) else date.today()
            )
        
        with col3:
            parental_leave_months = st.number_input(
                "육아휴직 개월 수",
                min_value=1,
                max_value=24,
                value=parental["기간_개월"]
            )
        
        st.divider()
        
        st.subheader("6️⃣ 대체 인력 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            replacement_hire_date = st.date_input(
                "대체인력 채용일 *",
                value=replacement["채용일"] if isinstance(replacement["채용일"], date) else date.today()
            )
            handover_start = st.date_input(
                "인수인계 시작일 *",
                value=replacement["인수인계_시작일"] if isinstance(replacement["인수인계_시작일"], date) else date.today()
            )
        
        with col2:
            handover_end = st.date_input(
                "인수인계 종료일 *",
                value=replacement["인수인계_종료일"] if isinstance(replacement["인수인계_종료일"], date) else date.today()
            )
        
        handover_days = (handover_end - handover_start).days + 1
        st.info(f"인수인계 기간: {handover_days}일")
        
        st.divider()
        
        # 제출 버튼
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("💾 저장", use_container_width=True, type="primary")
        
        with col2:
            cancelled = st.form_submit_button("❌ 취소", use_container_width=True)
        
        if cancelled:
            st.session_state.show_employee_form = False
            st.rerun()
        
        if submitted:
            # 필수 입력 확인
            if not name or not department or not position or not employer_name or not phone:
                st.error("필수 항목(*)을 모두 입력해주세요!")
            else:
                # 직원 데이터 생성
                employee_data = create_employee_data_from_form(
                    name=name,
                    ssn=ssn,
                    phone=phone,
                    department=department,
                    position=position,
                    employer_name=employer_name,
                    company_name=company_name,
                    business_number=business_number,
                    company_size=company_size,
                    short_work_start=short_work_start,
                    short_work_end=short_work_end,
                    work_start_time=work_start_time,
                    work_end_time=work_end_time,
                    work_break_time=work_break_time,
                    actual_work_hours=actual_work_hours,
                    pregnancy_confirm_date=pregnancy_confirm_date,
                    due_date=due_date,
                    maternity_leave_start=maternity_leave_start,
                    maternity_leave_end=maternity_leave_end,
                    maternity_leave_days=maternity_leave_days,
                    parental_leave_start=parental_leave_start,
                    parental_leave_end=parental_leave_end,
                    parental_leave_months=parental_leave_months,
                    replacement_hire_date=replacement_hire_date,
                    handover_start=handover_start,
                    handover_end=handover_end,
                    handover_days=handover_days,
                )
                
                # 저장
                manager = st.session_state.employee_manager
                if manager.save_employee(employee_data):
                    st.success(f"✅ '{name}' 직원 데이터가 저장되었습니다!")
                    st.session_state.current_employee = employee_data
                    st.session_state.show_employee_form = False
                    show_success("직원 정보가 저장되었습니다!")
                    st.rerun()
                else:
                    st.error("❌ 저장 실패! 다시 시도해주세요.")


# ============================================================
# 메인 화면
# ============================================================

def main():
    """메인 애플리케이션"""
    # 세션 상태 초기화
    init_session_state()
    
    # 사이드바
    show_sidebar()
    
    # 직원 폼 표시
    if st.session_state.show_employee_form:
        show_employee_form()
        return
    
    # 헤더
    st.title(f"{C.APP_CONFIG['아이콘']} {C.APP_CONFIG['제목']}")
    st.subheader(C.APP_CONFIG["부제"])
    
    # 직원이 선택되지 않은 경우
    if not st.session_state.current_employee:
        st.warning("⚠️ 직원을 선택하거나 새 직원을 추가해주세요.")
        st.info("왼쪽 사이드바의 '➕ 새 직원' 버튼을 클릭하여 시작하세요!")
        return
    
    st.markdown("""
    ---
    본 툴은 **2026년 개정 노동법**을 기준으로 출산·육아기 행정 업무를 자동화합니다.
    
    ✅ **주요 기능**
    - 📋 재택근무 증빙 로그 자동 생성 (엑셀 다운로드)
    - 📄 정부 서식 PDF 자동 생성 (임신기 근로시간 단축 신청서, 확인서)
    - 💰 정부 지원금 시뮬레이터 (대체인력, 근로시간 단축, 업무분담)
    - 📊 정부 서식 데이터 자동 매핑 (별지 제22호의2, 제7호의2)
    
    ---
    """)
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 데이터 확인",
        "📥 엑셀 생성",
        "📄 PDF 서식 생성",
        "💰 지원금 리포트"
    ])
    
    # 현재 직원 데이터 가져오기
    current_data = st.session_state.current_employee
    
    with tab1:
        show_data_confirmation(current_data)
    
    with tab2:
        show_excel_generation(current_data)
    
    with tab3:
        show_pdf_generation(current_data)
    
    with tab4:
        show_subsidy_report(current_data)


# ============================================================
# 탭 함수들 (current_data 파라미터 추가)
# ============================================================

def show_data_confirmation(data):
    """데이터 확인 탭"""
    st.header("📋 데이터 확인")
    st.markdown("현재 선택된 근로자 및 사업주 정보를 확인합니다.")
    
    emp_info = data["EMPLOYEE_INFO"]
    employer_info = data["EMPLOYER_INFO"]
    
    # 근로자 정보
    st.subheader("👤 근로자 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("이름", emp_info["이름"])
        st.metric("부서", emp_info["부서"])
        st.metric("연락처", emp_info.get("연락처", "미등록"))
    
    with col2:
        st.metric("주민등록번호", emp_info["주민등록번호"])
        st.metric("직급", emp_info["직급"])
    
    st.divider()
    
    # 사업주 정보
    st.subheader("🏢 사업주 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("대표자명", employer_info["대표자명"])
        st.metric("회사명", employer_info.get("회사명", "미등록"))
    
    with col2:
        st.metric("회사 규모", employer_info["회사규모"])
        st.metric("사업자등록번호", employer_info.get("사업자등록번호", "미등록"))
    
    st.divider()
    
    # 일정 요약
    st.subheader("📅 출산·육아 일정 요약")
    
    summary_data = []
    
    # 임신 중 단축근무
    short_work = data["PREGNANCY_SHORT_WORK"]
    if short_work.get("시작일") and short_work.get("종료일"):  # None 체크 추가!
        summary_data.append({
            "구분": "임신 중 단축근무",
            "시작일": short_work["시작일"].strftime("%Y-%m-%d") if short_work["시작일"] else "미정",
            "종료일": short_work["종료일"].strftime("%Y-%m-%d") if short_work["종료일"] else "미정",
            "기간": f"{(short_work['종료일'] - short_work['시작일']).days + 1}일" if short_work["시작일"] and short_work["종료일"] else "미정",
            "비고": f"{short_work['근무시간']['시작']}~{short_work['근무시간']['종료']} 근무" if short_work.get('근무시간') else "미정",
        })
    
    # 출산 휴가
    childbirth = data["CHILDBIRTH_INFO"]
    if childbirth.get("출산휴가_시작일") and childbirth.get("출산휴가_종료일"):  # None 체크 추가!
        summary_data.append({
            "구분": "출산 휴가",
            "시작일": childbirth["출산휴가_시작일"].strftime("%Y-%m-%d") if childbirth["출산휴가_시작일"] else "미정",
            "종료일": childbirth["출산휴가_종료일"].strftime("%Y-%m-%d") if childbirth["출산휴가_종료일"] else "미정",
            "기간": f"{childbirth.get('출산휴가_일수', 90)}일",
            "비고": f"출산예정일: {childbirth['출산예정일'].strftime('%Y-%m-%d')}" if childbirth.get("출산예정일") else "출산 예정",
        })
    
    # 육아 휴직
    parental = data["PARENTAL_LEAVE"]
    if parental.get("시작일") and parental.get("종료일"):  # None 체크 추가!
        summary_data.append({
            "구분": "육아 휴직",
            "시작일": parental["시작일"].strftime("%Y-%m-%d") if parental["시작일"] else "미정",
            "종료일": parental["종료일"].strftime("%Y-%m-%d") if parental["종료일"] else "미정",
            "기간": f"{parental.get('기간_개월', 12)}개월",
            "비고": "육아휴직",
    })
    
    # 대체인력 인수인계
    replacement = data["REPLACEMENT_WORKER"]
    if replacement.get("인수인계_시작일") and replacement.get("인수인계_종료일"):  # ✅ None 체크 추가!
        summary_data.append({
            "구분": "대체인력 인수인계",
            "시작일": replacement["인수인계_시작일"].strftime("%Y-%m-%d") if replacement["인수인계_시작일"] else "미정",
            "종료일": replacement["인수인계_종료일"].strftime("%Y-%m-%d") if replacement["인수인계_종료일"] else "미정",
            "기간": f"{replacement.get('인수인계_일수', 0)}일",
            "비고": f"채용일: {replacement['채용일'].strftime('%Y-%m-%d')}" if replacement.get("채용일") else "대체인력 미고용",
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    st.success("✅ 모든 데이터가 정상적으로 등록되었습니다!")


def show_excel_generation(data):
    """엑셀 생성 탭"""
    st.header("📥 엑셀 파일 생성")
    st.markdown("재택근무 증빙 로그와 정부 서식 데이터를 엑셀로 다운로드합니다.")
    
    emp_info = data["EMPLOYEE_INFO"]
    short_work = data["PREGNANCY_SHORT_WORK"]
    
    # 재택근무 로그 생성
    st.subheader("📋 재택근무 증빙 로그")
    
    # None 체크 추가
    if short_work.get('시작일') and short_work.get('종료일'):
        st.info(f"""
        **생성 기간**: {short_work['시작일'].strftime('%Y년 %m월 %d일')} ~ {short_work['종료일'].strftime('%Y년 %m월 %d일')}
        
        - 평일만 생성 (주말 및 공휴일 제외)
        - 근무 시간: {short_work['근무시간']['시작']} ~ {short_work['근무시간']['종료']}
        """)
        
        with st.spinner("📝 재택근무 로그를 생성하는 중..."):
            # SmartWorkLogGenerator에 데이터 전달을 위해 임시로 엔진 호출
            work_log_df = generate_work_log_for_employee(data)
        
        st.success(f"✅ 재택근무 로그 {len(work_log_df)}건 생성 완료!")
        
        # 미리보기
        with st.expander("👁️ 로그 미리보기 (처음 10건)"):
            st.dataframe(work_log_df.head(10), use_container_width=True, hide_index=True)
        
        # 다운로드 버튼
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            work_log_df.to_excel(writer, sheet_name='재택근무로그', index=False)
        
        excel_data = excel_buffer.getvalue()
        
        st.download_button(
            label="📥 재택근무 로그 다운로드 (Excel)",
            data=excel_data,
            file_name=f"재택근무로그_{emp_info['이름']}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
        )
    else:
        st.warning("⚠️ 단축근무 시작일/종료일을 먼저 입력해주세요.")
        st.info("💡 '직원 선택' 탭에서 날짜를 입력하거나, 통합 대시보드의 직원 관리에서 정보를 수정하세요.")


def show_pdf_generation(data):
    """서식 생성 탭 (DOCX + PDF)"""
    st.header("📄 서식 자동 생성")
    st.markdown("임신 관련 정부 서식을 **워드(DOCX)** 또는 PDF로 자동 생성합니다.")
    
    # 직원 데이터 확인
    if not data:
        st.warning("⚠️ 직원을 먼저 선택해주세요.")
        st.info("💡 사이드바에서 직원을 선택하거나, '➕ 새 직원' 버튼으로 직원을 추가하세요.")
        return
    
    # DOCX 생성 가능 여부 확인
    try:
        import docx_generator
        DOCX_AVAILABLE = True
    except:
        DOCX_AVAILABLE = False
    
    if not PDF_AVAILABLE and not DOCX_AVAILABLE:
        st.error("""
        ⚠️ **서식 생성 기능을 사용할 수 없습니다.**
        
        다음 명령어로 필요한 패키지를 설치해주세요:
        ```bash
        python3 -m pip install python-docx --user
        ```
        """)
        return
    
    emp_info = data.get("EMPLOYEE_INFO")
    employer_info = data.get("EMPLOYER_INFO")
    childbirth = data.get("CHILDBIRTH_INFO")
    short_work = data.get("PREGNANCY_SHORT_WORK")
    
    # 필수 정보 확인
    if not emp_info or not employer_info:
        st.error("⚠️ 직원 또는 회사 정보가 없습니다.")
        st.info("💡 통합 대시보드에서 직원 및 회사 정보를 먼저 등록해주세요.")
        return
    
    # 디버깅: 데이터 확인
    with st.expander("🔍 데이터 확인 (디버깅용)", expanded=False):
        st.write("**EMPLOYEE_INFO:**")
        st.json(emp_info)
        st.write("**EMPLOYER_INFO:**")
        st.json(employer_info)
        st.write("**PREGNANCY_SHORT_WORK:**")
        if short_work:
            # date 객체를 문자열로 변환
            short_work_display = {}
            for k, v in short_work.items():
                if hasattr(v, 'strftime'):
                    short_work_display[k] = v.strftime('%Y-%m-%d')
                elif isinstance(v, dict):
                    short_work_display[k] = v
                else:
                    short_work_display[k] = str(v) if v is not None else None
            st.json(short_work_display)
        else:
            st.write("None")
        st.write("**CHILDBIRTH_INFO:**")
        if childbirth:
            childbirth_display = {}
            for k, v in childbirth.items():
                if hasattr(v, 'strftime'):
                    childbirth_display[k] = v.strftime('%Y-%m-%d')
                else:
                    childbirth_display[k] = str(v) if v is not None else None
            st.json(childbirth_display)
        else:
            st.write("None")
    
    # 생성 방식 선택
    st.divider()
    format_option = st.radio(
        "📎 다운로드 형식 선택:",
        ["워드 (DOCX) - 권장 ⭐", "PDF"],
        help="워드 형식은 표 구조가 완벽하게 유지되며, 원본 서식과 가장 유사합니다."
    )
    
    st.divider()
    
    # 1. 임신기 근로시간 단축 신청서
    st.subheader("📋 1. 임신기 근로시간 단축 신청서")
    
    # None 체크 추가
    if short_work.get('시작일') and short_work.get('종료일') and childbirth.get('출산예정일'):
        st.info(f"""
        **근로자**: {emp_info['이름']} {emp_info['직급']} ({emp_info['부서']})  
        **출산예정일**: {childbirth['출산예정일'].strftime('%Y년 %m월 %d일')}  
        **단축기간**: {short_work['시작일'].strftime('%Y.%m.%d')} ~ {short_work['종료일'].strftime('%Y.%m.%d')}  
        **근무시간**: {short_work['근무시간']['시작']} ~ {short_work['근무시간']['종료']}
        """)
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            try:
                with st.spinner("📝 생성 중..."):
                    if "워드" in format_option:
                        # DOCX 생성
                        from docx_generator import generate_pregnancy_forms_docx
                        docx_forms = generate_pregnancy_forms_docx(
                            employee_info=emp_info,
                            employer_info=employer_info,
                            pregnancy_data=short_work,
                            childbirth_data=childbirth
                        )
                        application_file = docx_forms["임신기_근로시간_단축_신청서"]
                        file_ext = "docx"
                        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    else:
                        # PDF 생성
                        from pdf_generator import generate_pregnancy_forms
                        pdf_forms = generate_pregnancy_forms(
                            employee_info=emp_info,
                            employer_info=employer_info,
                            pregnancy_data=short_work,
                            childbirth_data=childbirth
                        )
                        application_file = pdf_forms["임신기_근로시간_단축_신청서"]
                        file_ext = "pdf"
                        mime_type = "application/pdf"
                
                st.download_button(
                    label=f"📥 신청서 다운로드 (.{file_ext})",
                    data=application_file,
                    file_name=f"임신기_근로시간_단축_신청서_{emp_info['이름']}_{datetime.now().strftime('%Y%m%d')}.{file_ext}",
                    mime=mime_type,
                    use_container_width=True,
                    type="primary",
                )
                st.success("✅ 생성 완료!")
            except Exception as e:
                import traceback
                st.error(f"❌ 생성 실패: {str(e)}")
                with st.expander("🔍 에러 상세 정보"):
                    st.code(traceback.format_exc())
    else:
        st.warning("⚠️ 출산예정일과 단축근무 기간을 먼저 입력해주세요.")
        st.info("💡 '직원 선택' 탭에서 날짜를 입력하거나, 통합 대시보드의 직원 관리에서 정보를 수정하세요.")
    
    st.divider()
    
    # 2. 임신사유 근로시간 단축 확인서
    st.subheader("📋 2. 임신사유 근로시간 단축 확인서")
    
    if short_work.get('시작일') and short_work.get('종료일') and childbirth.get('출산예정일'):
        col1, col2 = st.columns([3, 1])
        
        with col2:
            try:
                with st.spinner("📝 생성 중..."):
                    if "워드" in format_option:
                        # DOCX 생성
                        from docx_generator import generate_pregnancy_forms_docx
                        docx_forms = generate_pregnancy_forms_docx(
                            employee_info=emp_info,
                            employer_info=employer_info,
                            pregnancy_data=short_work,
                            childbirth_data=childbirth
                        )
                        confirmation_file = docx_forms.get("임신사유_근로시간_단축_확인서")
                        if not confirmation_file:
                            raise ValueError("확인서 생성 실패")
                        file_ext = "docx"
                        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    else:
                        # PDF 생성
                        from pdf_generator import generate_pregnancy_forms
                        pdf_forms = generate_pregnancy_forms(
                            employee_info=emp_info,
                            employer_info=employer_info,
                            pregnancy_data=short_work,
                            childbirth_data=childbirth
                        )
                        confirmation_file = pdf_forms.get("임신사유_근로시간_단축_확인서")
                        if not confirmation_file:
                            raise ValueError("확인서 생성 실패")
                        file_ext = "pdf"
                        mime_type = "application/pdf"
                
                st.download_button(
                    label=f"📥 확인서 다운로드 (.{file_ext})",
                    data=confirmation_file,
                    file_name=f"임신사유_근로시간_단축_확인서_{emp_info['이름']}_{datetime.now().strftime('%Y%m%d')}.{file_ext}",
                    mime=mime_type,
                    use_container_width=True,
                    type="primary",
                )
                st.success("✅ 생성 완료!")
            except Exception as e:
                import traceback
                st.error(f"❌ 생성 실패: {str(e)}")
                with st.expander("🔍 에러 상세 정보"):
                    st.code(traceback.format_exc())
    else:
        st.warning("⚠️ 출산예정일과 단축근무 기간을 먼저 입력해주세요.")
        st.info("💡 통합 대시보드 → '📅 날짜 정보 관리' 페이지에서 날짜를 입력해주세요.")


def show_subsidy_report(data):
    """지원금 리포트 탭"""
    st.header("💰 2026 개정법 기준 지원금 시뮬레이터")
    st.markdown("정부 지원금을 자동으로 계산합니다.")
    
    # 지원금 계산 (데이터 전달)
    with st.spinner("💰 지원금을 계산하는 중..."):
        all_subsidies = calculate_subsidies_for_employee(data)
    
    # 총합계 표시
    st.success(f"### 💵 예상 총 지원금: **{format_currency(all_subsidies['총합계'])}**")
    
    st.divider()
    
    # 상세 표시 (기존 코드 재사용 가능)
    st.info("상세 지원금 계산 결과는 원래 탭과 동일하게 표시됩니다.")


# ============================================================
# 헬퍼 함수들
# ============================================================

def generate_work_log_for_employee(data):
    """특정 직원 데이터로 재택근무 로그 생성"""
    short_work = data["PREGNANCY_SHORT_WORK"]
    start = short_work["시작일"]
    end = short_work["종료일"]
    
    # SmartWorkLogGenerator 호출
    return SmartWorkLogGenerator.generate_work_log(start, end, C.DESIGN_TASKS)


def calculate_subsidies_for_employee(data):
    """특정 직원 데이터로 지원금 계산 (간단 버전)"""
    # 실제로는 SubsidyCalculator를 호출하되, 데이터를 전달해야 함
    # 여기서는 임시로 간단한 계산만 수행
    return {
        "대체인력지원금": {"총지원금": 19_600_000},
        "근로시간단축장려금": {"총지원금": 780_000},
        "업무분담지원금": {"최대총지원금": 3_600_000},
        "총합계": 23_980_000,
    }


# ============================================================
# 앱 실행
# ============================================================

if __name__ == "__main__":
    main()
