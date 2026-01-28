"""
app.py
Remote Work Management System - Main Application
Modular design with clean separation of concerns
"""

import streamlit as st
from datetime import datetime, date, time
import pandas as pd
import sys
from pathlib import Path

# shared 모듈 import
sys.path.append(str(Path(__file__).parent.parent))
from shared.design import apply_design
from shared.utils import show_success

# Import custom modules
from database import (
    init_database, seed_initial_data, get_all_employees,
    add_work_log, get_work_logs, get_company_setting,
    update_company_setting, get_system_logs, add_system_log,
    get_work_stats, add_employee, update_employee, delete_employee,
    get_employee_by_id, add_user
)
from auth import (
    hash_password, init_session_state, login_page,
    logout, is_authenticated, is_admin
)
from admin_tools import (
    bulk_history_injector, inline_editor, smart_randomizer,
    calculate_work_hours
)
from reports import report_generator, statistics_dashboard
from work_schedules import WORK_SCHEDULE_PRESETS, get_schedule_names

# Page config
st.set_page_config(
    page_title="재택근무 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 모던 그린 미니멀 디자인 적용
apply_design()

st.sidebar.divider()

# Custom CSS (추가 스타일)
st.markdown("""
<style>
    /* Main theme - Sage Green */
    .stApp {
        background: linear-gradient(135deg, #A8C5A0 0%, #8FAD87 100%);
    }
    
    /* Sidebar - 더 진하게 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2D4A2A 0%, #1F3D1C 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    
    /* Main content area - 완전 흰색 배경 */
    .main .block-container {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Metrics - 더 명확하게 */
    [data-testid="stMetricValue"] {
        font-size: 36px !important;
        font-weight: 800 !important;
        color: #2D4A2A !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 16px !important;
        color: #1F3D1C !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 14px !important;
        font-weight: 600 !important;
    }
    
    /* Headers - 가독성 최고 */
    h1 {
        color: #1F3D1C !important;
        font-weight: 800 !important;
        font-size: 42px !important;
        border-bottom: 4px solid #6B9462 !important;
        padding-bottom: 15px !important;
        margin-bottom: 30px !important;
    }
    
    h2 {
        color: #2D4A2A !important;
        font-weight: 700 !important;
        font-size: 32px !important;
        margin-top: 25px !important;
    }
    
    h3 {
        color: #3A5A37 !important;
        font-weight: 600 !important;
        font-size: 24px !important;
    }
    
    /* Paragraphs and text - 명확하게 */
    p, span, div {
        color: #1F3D1C !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
    }
    
    /* Labels - 더 진하게 */
    label {
        color: #1F3D1C !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    /* Buttons - 더 큰 크기와 명확한 색상 */
    .stButton>button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 12px 24px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        min-height: 50px !important;
    }
    
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #6B9462 0%, #4A7A42 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 8px rgba(107, 148, 98, 0.3) !important;
    }
    
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 16px rgba(107, 148, 98, 0.5) !important;
        background: linear-gradient(135deg, #7AA871 0%, #5A8A52 100%) !important;
    }
    
    .stButton>button[kind="secondary"] {
        background-color: #E8F4E5 !important;
        color: #1F3D1C !important;
        border: 2px solid #6B9462 !important;
        font-weight: 600 !important;
    }
    
    .stButton>button[kind="secondary"]:hover {
        background-color: #D0E8CC !important;
        border-color: #4A7A42 !important;
    }
    
    /* Input fields - 더 명확하게 */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>div,
    .stTextArea>div>div>textarea,
    .stDateInput>div>div>input,
    .stTimeInput>div>div>input {
        border: 2px solid #B5D1AF !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-size: 16px !important;
        color: #1F3D1C !important;
        background-color: #FFFFFF !important;
        font-weight: 500 !important;
    }
    
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>div:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #6B9462 !important;
        box-shadow: 0 0 0 3px rgba(107, 148, 98, 0.2) !important;
    }
    
    /* Select dropdown text */
    .stSelectbox>div>div>div>div {
        color: #1F3D1C !important;
        font-weight: 600 !important;
    }
    
    /* Info boxes - 더 명확하게 */
    .stAlert {
        border-radius: 12px !important;
        border-left: 5px solid #6B9462 !important;
        padding: 1.2rem !important;
        font-weight: 600 !important;
    }
    
    /* Tables - 가독성 향상 */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 2px solid #B5D1AF !important;
    }
    
    .stDataFrame tbody tr {
        background-color: #FFFFFF !important;
    }
    
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #F5F9F4 !important;
    }
    
    .stDataFrame th {
        background: linear-gradient(135deg, #6B9462 0%, #4A7A42 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 12px !important;
    }
    
    .stDataFrame td {
        color: #1F3D1C !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 10px !important;
    }
    
    /* Success messages - 더 진하게 */
    .stSuccess {
        background-color: #D4EDDA !important;
        color: #155724 !important;
        border-left: 5px solid #28A745 !important;
        border-radius: 10px !important;
        padding: 1.2rem !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    /* Error messages */
    .stError {
        background-color: #F8D7DA !important;
        color: #721C24 !important;
        border-left: 5px solid #DC3545 !important;
        border-radius: 10px !important;
        padding: 1.2rem !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    /* Warning messages */
    .stWarning {
        background-color: #FFF3CD !important;
        color: #856404 !important;
        border-left: 5px solid #FFC107 !important;
        border-radius: 10px !important;
        padding: 1.2rem !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    /* Info messages */
    .stInfo {
        background-color: #D1ECF1 !important;
        color: #0C5460 !important;
        border-left: 5px solid #17A2B8 !important;
        border-radius: 10px !important;
        padding: 1.2rem !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    /* Tabs - 더 명확하게 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #E8F4E5 !important;
        border-radius: 10px 10px 0 0 !important;
        color: #1F3D1C !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 12px 24px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6B9462 0%, #4A7A42 100%) !important;
        color: #FFFFFF !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #E8F4E5 !important;
        border-radius: 10px !important;
        color: #1F3D1C !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 12px !important;
    }
    
    /* Form labels */
    .stForm label {
        color: #1F3D1C !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    /* Radio buttons */
    .stRadio label {
        color: #1F3D1C !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }
    
    /* Checkbox */
    .stCheckbox label {
        color: #1F3D1C !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }
    
    /* Remove decorations */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #E8F4E5;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #6B9462;
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #4A7A42;
    }
    
    /* Horizontal line */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, #6B9462, transparent) !important;
        margin: 30px 0 !important;
    }
</style>
""", unsafe_allow_html=True)


def init_app():
    """Initialize application (database, session)"""
    # Initialize database
    init_database()
    
    # Seed initial data with admin and user accounts
    admin_password_hash = hash_password("admin1234")
    user_password_hash = hash_password("songmi1234")
    seed_initial_data(admin_password_hash, user_password_hash)
    
    # Initialize session state
    init_session_state()


def dashboard_page():
    """Main dashboard"""
    st.title("📊 대시보드")
    
    # Welcome message
    st.markdown(f"""
    ### 환영합니다, {st.session_state.full_name}님! 👋
    **역할:** {st.session_state.role} | **시스템 버전:** 2.0
    """)
    
    st.write("---")
    
    # Overall statistics
    all_logs = get_work_logs()
    all_employees = get_all_employees()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "👥 활성 직원",
            len(all_employees),
            help="현재 등록된 활성 직원 수"
        )
    
    with col2:
        st.metric(
            "📝 총 근무 기록",
            len(all_logs),
            help="시스템에 저장된 총 근무 기록 수"
        )
    
    with col3:
        if all_logs:
            total_hours = sum(log['work_hours'] for log in all_logs)
            st.metric(
                "⏱️ 총 근무시간",
                f"{total_hours:.1f}h",
                help="전체 직원의 누적 근무시간"
            )
        else:
            st.metric("⏱️ 총 근무시간", "0h")
    
    with col4:
        if all_logs:
            manual_count = sum(1 for log in all_logs if log['is_manual'] == 1)
            st.metric(
                "✏️ 수동 입력",
                f"{manual_count}건",
                help="관리자가 직접 입력한 기록 수"
            )
        else:
            st.metric("✏️ 수동 입력", "0건")
    
    st.write("---")
    
    # Recent work logs
    st.subheader("📋 최근 근무 기록 (10건)")
    
    if all_logs:
        recent_logs = all_logs[:10]
        df = pd.DataFrame(recent_logs)
        display_df = df[['work_date', 'emp_id', 'start_time', 'end_time', 'work_hours', 'work_description']]
        display_df.columns = ['날짜', '사번', '시작', '종료', '근무시간', '업무내용']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("📭 아직 근무 기록이 없습니다. '근무 기록 입력' 메뉴에서 추가하세요.")
    
    # Quick actions - 권한별 다른 메뉴
    st.write("---")
    st.subheader("⚡ 빠른 작업")
    
    if is_admin():
        # 관리자용 빠른 작업
        col_action1, col_action2, col_action3 = st.columns(3)
        
        with col_action1:
            if st.button("⚡ 간편 출퇴근", use_container_width=True, type="primary", key="dash_quick_work"):
                st.session_state.nav_page = "quick_work"
                st.rerun()
        
        with col_action2:
            if st.button("📦 일괄 입력", use_container_width=True, key="dash_admin_tools"):
                st.session_state.nav_page = "admin_tools"
                st.rerun()
        
        with col_action3:
            if st.button("📥 보고서 생성", use_container_width=True, key="dash_reports"):
                st.session_state.nav_page = "reports"
                st.rerun()
    else:
        # 일반 사용자용 빠른 작업
        col_action1, col_action2 = st.columns(2)
        
        with col_action1:
            if st.button("⚡ 오늘 출퇴근 기록", use_container_width=True, type="primary", key="dash_user_quick_work"):
                st.session_state.nav_page = "quick_work"
                st.rerun()
        
        with col_action2:
            if st.button("🔍 내 기록 보기", use_container_width=True, key="dash_user_view_logs"):
                st.session_state.nav_page = "view_logs"
                st.rerun()


def quick_work_entry_page():
    """Quick work entry for regular users"""
    st.title("⚡ 간편 출퇴근 기록")
    
    st.info("💡 간편하게 오늘의 출퇴근을 기록하세요. 빠른 선택으로 쉽게 완료할 수 있습니다!")
    
    # Get current user's emp_id
    employees = get_all_employees()
    current_user_name = st.session_state.full_name
    current_employee = next((emp for emp in employees if emp['name'] == current_user_name), None)
    
    if not current_employee:
        st.error("⚠️ 직원 정보를 찾을 수 없습니다. 관리자에게 문의하세요.")
        return
    
    emp_id = current_employee['emp_id']
    
    with st.form("quick_work_entry_form"):
        st.write(f"**👤 직원:** {current_employee['name']} ({current_employee['department']} {current_employee['position']})")
        
        # Today's date (can't change)
        work_date = st.date_input(
            "📅 근무 날짜",
            value=date.today(),
            disabled=True,
            help="오늘 날짜로 자동 설정됩니다"
        )
        
        # 시차 출퇴근제 프리셋 선택
        st.write("**⏰ 근무 시간대 선택 (시차 출퇴근제)**")
        
        preset_names = [preset["name"] for preset in WORK_SCHEDULE_PRESETS.values()]
        selected_preset_name = st.selectbox(
            "근무 시간대",
            options=preset_names,
            help="시차 출퇴근제 또는 단축근무 프리셋을 선택하세요"
        )
        
        # 선택된 프리셋 찾기
        selected_preset = None
        for key, preset in WORK_SCHEDULE_PRESETS.items():
            if preset["name"] == selected_preset_name:
                selected_preset = preset
                break
        
        col1, col2 = st.columns(2)
        
        if "맞춤형" in selected_preset_name or selected_preset is None:
            # 직접 입력
            with col1:
                start_time = st.time_input("출근 시간", value=time(9, 0))
            with col2:
                end_time = st.time_input("퇴근 시간", value=time(18, 0))
        else:
            # 프리셋 사용
            with col1:
                start_time = st.time_input(
                    "출근 시간", 
                    value=selected_preset["start_time"],
                    help=f"프리셋: {selected_preset['start_time'].strftime('%H:%M')}"
                )
            with col2:
                end_time = st.time_input(
                    "퇴근 시간", 
                    value=selected_preset["end_time"],
                    help=f"프리셋: {selected_preset['end_time'].strftime('%H:%M')}"
                )
        
        # Work type - quick select
        work_type = st.radio(
            "🏢 근무 유형",
            options=["재택근무", "사무실근무", "외근"],
            horizontal=True,
            index=0
        )
        
        # Work description - quick templates
        st.write("**📝 업무 내용 (빠른 템플릿)**")
        template = st.selectbox(
            "템플릿 선택",
            options=[
                "브랜드 리뉴얼 UI/UX 시안 검토 및 수정",
                "신규 제품 패키지 디자인 작업",
                "홈페이지 메인 배너 제작",
                "마케팅 자료 디자인 작업",
                "SNS 콘텐츠 이미지 제작",
                "고객사 제안서 디자인 작업",
                "직접 입력"
            ]
        )
        
        if template == "직접 입력":
            work_description = st.text_area(
                "업무 내용 작성",
                height=100,
                placeholder="오늘 수행한 업무를 입력하세요..."
            )
        else:
            work_description = template
            st.info(f"✅ 선택된 템플릿: {template}")
        
        # Submit button
        submitted = st.form_submit_button("💾 기록 저장", type="primary", use_container_width=True)
        
        if submitted:
            if not work_description:
                st.error("⚠️ 업무 내용을 입력해주세요.")
            elif start_time >= end_time:
                st.error("⚠️ 퇴근 시간이 출근 시간보다 늦어야 합니다.")
            else:
                # Calculate hours
                start_str = start_time.strftime("%H:%M:00")
                end_str = end_time.strftime("%H:%M:00")
                from admin_tools import calculate_work_hours
                hours = calculate_work_hours(start_str, end_str, 1.0)
                
                # Add to database
                log_id = add_work_log(
                    emp_id=emp_id,
                    work_date=work_date.isoformat(),
                    start_time=start_str,
                    end_time=end_str,
                    break_time="12:00-13:00",
                    work_hours=hours,
                    work_description=work_description,
                    work_type=work_type,
                    created_by=st.session_state.full_name,
                    is_manual=0  # 일반 사용자는 0
                )
                
                # Log the action
                add_system_log(
                    st.session_state.username,
                    "근무 기록 입력",
                    f"{emp_id} / {work_date} / {hours}시간"
                )
                
                st.success(f"✅ 오늘의 근무 기록이 저장되었습니다! (근무시간: {hours}시간)")
                st.rerun()


def work_entry_page():
    """Manual work log entry - Admin only"""
    st.title("✏️ 근무 기록 입력 (관리자)")
    
    st.info("💡 개별 근무 기록을 수동으로 입력합니다. 과거 날짜도 입력 가능합니다.")
    
    with st.form("work_entry_form"):
        # Employee selection
        employees = get_all_employees()
        emp_options = {f"{emp['name']} ({emp['emp_id']}) - {emp['department']} {emp['position']}": emp['emp_id'] 
                       for emp in employees}
        
        selected_emp = st.selectbox("👤 직원 선택", options=list(emp_options.keys()))
        emp_id = emp_options[selected_emp]
        
        # Work date
        work_date = st.date_input(
            "📅 근무 날짜",
            value=date.today(),
            help="과거 날짜도 선택 가능합니다"
        )
        
        # Work type
        work_type = st.selectbox(
            "🏢 근무 유형",
            options=["재택근무", "사무실근무", "외근"],
            index=0
        )
        
        # Time inputs
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input("⏰ 시작 시간", value=time(11, 0))
        with col2:
            end_time = st.time_input("⏰ 종료 시간", value=time(18, 0))
        
        # Break time
        break_time = st.text_input("☕ 휴게시간", value="12:00-13:00")
        
        # Work description
        work_description = st.text_area(
            "📝 업무 내용",
            height=120,
            placeholder="오늘 수행한 업무를 상세히 입력하세요..."
        )
        
        # Submit
        submitted = st.form_submit_button("💾 저장", type="primary", use_container_width=True)
        
        if submitted:
            # Validation
            if not work_description:
                st.error("⚠️ 업무 내용을 입력해주세요.")
            elif start_time >= end_time:
                st.error("⚠️ 종료 시간이 시작 시간보다 늦어야 합니다.")
            else:
                # Calculate hours
                start_str = start_time.strftime("%H:%M:%S")
                end_str = end_time.strftime("%H:%M:%S")
                hours = calculate_work_hours(start_str, end_str, 1.0)
                
                # Add to database
                log_id = add_work_log(
                    emp_id=emp_id,
                    work_date=work_date.isoformat(),
                    start_time=start_str,
                    end_time=end_str,
                    break_time=break_time,
                    work_hours=hours,
                    work_description=work_description,
                    work_type=work_type,
                    created_by=st.session_state.full_name,
                    is_manual=1
                )
                
                # Log the action
                add_system_log(
                    st.session_state.username,
                    "근무 기록 입력",
                    f"{emp_id} / {work_date} / {hours}시간"
                )
                
                st.success(f"✅ 근무 기록이 저장되었습니다! (ID: {log_id})")


def view_logs_page():
    """View and search work logs"""
    if is_admin():
        st.title("🔍 근무 기록 조회 (전체)")
    else:
        st.title("🔍 내 근무 기록")
    
    st.info("💡 저장된 근무 기록을 조회하고 검색합니다.")
    
    # 일반 사용자는 자신의 기록만 조회
    if not is_admin():
        employees = get_all_employees()
        current_user_name = st.session_state.full_name
        current_employee = next((emp for emp in employees if emp['name'] == current_user_name), None)
        
        if not current_employee:
            st.error("⚠️ 직원 정보를 찾을 수 없습니다.")
            return
        
        emp_id_filter = current_employee['emp_id']
        
        # 기간 필터만 제공
        col1, col2 = st.columns(2)
        with col1:
            start_filter = st.date_input("시작일", value=date(2026, 1, 1))
        with col2:
            end_filter = st.date_input("종료일", value=date.today())
    else:
        # 관리자는 전체 조회 가능
        # Filters
        with st.expander("🔎 필터 설정", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                employees = get_all_employees()
                emp_filter_options = ["전체"] + [f"{emp['name']} ({emp['emp_id']})" for emp in employees]
                selected_emp_filter = st.selectbox("직원", options=emp_filter_options)
            
            with col2:
                start_filter = st.date_input("시작일", value=date(2026, 1, 1))
            
            with col3:
                end_filter = st.date_input("종료일", value=date.today())
        
        # Get logs
        if selected_emp_filter == "전체":
            emp_id_filter = None
        else:
            emp_id_filter = selected_emp_filter.split('(')[1].strip(')')
    
    logs = get_work_logs(
        emp_id=emp_id_filter,
        start_date=start_filter.isoformat(),
        end_date=end_filter.isoformat()
    )
    
    if not logs:
        st.warning("📭 조회된 기록이 없습니다.")
        return
    
    # Statistics
    st.subheader("📊 통계")
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    total_days = len(logs)
    total_hours = sum(log['work_hours'] for log in logs)
    avg_hours = total_hours / total_days if total_days > 0 else 0
    
    with col_stat1:
        st.metric("📆 총 근무일", f"{total_days}일")
    with col_stat2:
        st.metric("⏱️ 총 근무시간", f"{total_hours:.1f}시간")
    with col_stat3:
        st.metric("📈 평균 근무시간", f"{avg_hours:.1f}시간")
    
    # Display logs
    st.subheader("📋 상세 기록")
    df = pd.DataFrame(logs)
    display_df = df[['work_date', 'emp_id', 'start_time', 'end_time', 'work_hours', 'work_description', 'work_type']]
    display_df.columns = ['날짜', '사번', '시작', '종료', '근무시간', '업무내용', '근무유형']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)


def admin_tools_page():
    """Admin-only tools"""
    if not is_admin():
        st.error("🚫 관리자 권한이 필요합니다.")
        return
    
    st.title("⚙️ 관리자 도구")
    
    tab1, tab2, tab3 = st.tabs(["📦 일괄 입력", "✏️ 기록 편집", "🎲 시간 생성기"])
    
    with tab1:
        bulk_history_injector()
    
    with tab2:
        inline_editor()
    
    with tab3:
        smart_randomizer()


def reports_page():
    """Reports and exports"""
    st.title("📥 보고서 출력")
    
    tab1, tab2 = st.tabs(["📄 증빙 보고서", "📊 통계"])
    
    with tab1:
        report_generator()
    
    with tab2:
        statistics_dashboard()


def employee_management_page():
    """Employee management page (admin only)"""
    if not is_admin():
        st.error("🚫 관리자 권한이 필요합니다.")
        return
    
    st.title("👥 직원 관리")
    
    tab1, tab2 = st.tabs(["📋 직원 목록", "➕ 직원 추가"])
    
    with tab1:
        st.subheader("📋 등록된 직원 목록")
        
        employees = get_all_employees()
        
        if not employees:
            st.info("등록된 직원이 없습니다.")
        else:
            # Display statistics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("👥 총 직원 수", len(employees))
            with col2:
                departments = set(emp['department'] for emp in employees if emp['department'])
                st.metric("🏢 부서 수", len(departments))
            
            st.write("---")
            
            # Display employee table with edit/delete options
            for emp in employees:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
                    
                    with col1:
                        st.write(f"**{emp['name']}**")
                        st.caption(f"사번: {emp['emp_id']}")
                    
                    with col2:
                        st.write(f"{emp['department']}")
                        st.caption("부서")
                    
                    with col3:
                        st.write(f"{emp['position']}")
                        st.caption("직급")
                    
                    with col4:
                        if st.button("✏️", key=f"edit_{emp['id']}", help="수정"):
                            st.session_state[f"editing_emp_{emp['id']}"] = True
                            st.rerun()
                    
                    with col5:
                        if st.button("🗑️", key=f"delete_{emp['id']}", help="삭제"):
                            if delete_employee(emp['emp_id']):
                                add_system_log(
                                    st.session_state.username,
                                    "직원 삭제",
                                    f"{emp['name']} ({emp['emp_id']})"
                                )
                                st.success(f"✅ {emp['name']} 직원이 삭제되었습니다.")
                                st.rerun()
                    
                    # Edit form (inline)
                    if st.session_state.get(f"editing_emp_{emp['id']}", False):
                        with st.form(f"edit_emp_form_{emp['id']}"):
                            st.markdown(f"##### ✏️ {emp['name']} 정보 수정")
                            
                            col_e1, col_e2 = st.columns(2)
                            with col_e1:
                                new_name = st.text_input("이름", value=emp['name'])
                                new_department = st.text_input("부서", value=emp['department'])
                            
                            with col_e2:
                                new_position = st.text_input("직급", value=emp['position'])
                                new_hire_date = st.text_input("입사일", value=emp['hire_date'], 
                                                             help="형식: YYYY-MM-DD")
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("💾 저장", type="primary", use_container_width=True):
                                    if update_employee(emp['emp_id'], new_name, new_department, 
                                                      new_position, new_hire_date):
                                        add_system_log(
                                            st.session_state.username,
                                            "직원 정보 수정",
                                            f"{new_name} ({emp['emp_id']})"
                                        )
                                        st.session_state[f"editing_emp_{emp['id']}"] = False
                                        st.success("✅ 직원 정보가 수정되었습니다!")
                                        st.rerun()
                            
                            with col_cancel:
                                if st.form_submit_button("❌ 취소", use_container_width=True):
                                    st.session_state[f"editing_emp_{emp['id']}"] = False
                                    st.rerun()
                    
                    st.divider()
    
    with tab2:
        st.subheader("➕ 새 직원 추가")
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, #E8F4E5 0%, #D0E8CC 100%); 
                    padding: 20px; border-radius: 12px; margin-bottom: 20px; 
                    border-left: 5px solid #6B9462;'>
            <h4 style='color: #2D4A2A; margin: 0 0 10px 0;'>💡 직원 등록 안내</h4>
            <p style='color: #3A5A37; margin: 0; font-size: 14px;'>
            새 직원을 등록하면 출퇴근 기록을 관리할 수 있습니다.<br>
            사번은 중복될 수 없으며, 입사일은 YYYY-MM-DD 형식으로 입력하세요.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("add_employee_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                emp_id = st.text_input(
                    "사번 *",
                    placeholder="예: EMP001",
                    help="고유한 사번을 입력하세요 (중복 불가)"
                )
                name = st.text_input(
                    "이름 *",
                    placeholder="예: 홍길동"
                )
            
            with col2:
                department = st.text_input(
                    "부서 *",
                    placeholder="예: 디자인 기획팀"
                )
                position = st.text_input(
                    "직급 *",
                    placeholder="예: 대리"
                )
            
            hire_date = st.date_input(
                "입사일 *",
                value=date.today(),
                min_value=date(2000, 1, 1),
                max_value=date.today(),
                help="직원의 입사일을 선택하세요 (2000년 이후)"
            )
            
            st.write("---")
            st.markdown("### 🔐 로그인 계정 생성 (선택사항)")
            
            create_account = st.checkbox("이 직원의 로그인 계정을 생성합니다", value=True)
            
            username = ""
            password = ""
            
            if create_account:
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    username = st.text_input(
                        "로그인 ID *",
                        placeholder="예: honggildong",
                        help="영문 소문자로 입력 (공백 없이)"
                    )
                with col_u2:
                    password = st.text_input(
                        "비밀번호 *",
                        type="password",
                        placeholder="최소 4자 이상",
                        help="직원에게 안전하게 전달하세요"
                    )
            
            submitted = st.form_submit_button("➕ 직원 추가", type="primary", use_container_width=True)
            
            if submitted:
                if not emp_id or not name or not department or not position:
                    st.error("⚠️ 모든 필수 항목을 입력해주세요.")
                elif len(emp_id) < 3:
                    st.error("⚠️ 사번은 3자 이상이어야 합니다.")
                elif create_account and (not username or not password):
                    st.error("⚠️ 로그인 계정을 생성하려면 ID와 비밀번호를 입력해주세요.")
                elif create_account and len(password) < 4:
                    st.error("⚠️ 비밀번호는 최소 4자 이상이어야 합니다.")
                else:
                    # 직원 추가
                    if add_employee(emp_id, name, department, position, hire_date.isoformat()):
                        # 사용자 계정 생성 (선택된 경우)
                        account_created = False
                        if create_account:
                            password_hash = hash_password(password)
                            if add_user(username, password_hash, name, 'user'):
                                account_created = True
                            else:
                                st.warning(f"⚠️ 직원은 등록되었으나, 로그인 ID '{username}'는 이미 존재합니다.")
                        
                        add_system_log(
                            st.session_state.username,
                            "직원 추가",
                            f"{name} ({emp_id}) - {department} {position}" + 
                            (f" / 계정생성: {username}" if account_created else "")
                        )
                        
                        if account_created:
                            st.success(f"✅ {name} 직원이 등록되고 로그인 계정({username})이 생성되었습니다!")
                        else:
                            show_success(f"{name} 직원이 등록되었습니다!")
                        
                        st.rerun()
                    else:
                        st.error("⚠️ 사번이 이미 존재합니다. 다른 사번을 사용하세요.")


def system_settings_page():
    """System settings (admin only)"""
    if not is_admin():
        st.error("🚫 관리자 권한이 필요합니다.")
        return
    
    st.title("⚙️ 시스템 설정")
    
    tab1, tab2 = st.tabs(["🏢 회사 정보", "📜 시스템 로그"])
    
    with tab1:
        st.subheader("회사 정보 관리")
        
        with st.form("company_settings_form"):
            company_name = st.text_input(
                "회사명",
                value=get_company_setting('company_name') or '(주)예시회사'
            )
            representative = st.text_input(
                "대표자명",
                value=get_company_setting('representative') or '이진선'
            )
            business_number = st.text_input(
                "사업자등록번호",
                value=get_company_setting('business_number') or '123-45-67890'
            )
            
            if st.form_submit_button("💾 저장", use_container_width=True):
                update_company_setting('company_name', company_name)
                update_company_setting('representative', representative)
                update_company_setting('business_number', business_number)
                
                add_system_log(
                    st.session_state.username,
                    "회사 정보 수정",
                    f"{company_name}"
                )
                
                st.success("✅ 회사 정보가 업데이트되었습니다.")
                st.rerun()
    
    with tab2:
        st.subheader("시스템 로그 (최근 100건)")
        
        logs = get_system_logs(100)
        if logs:
            df = pd.DataFrame(logs)
            st.dataframe(df, use_container_width=True, hide_index=True, height=500)
        else:
            st.info("로그가 없습니다.")


def sidebar_navigation():
    """Sidebar navigation"""
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px 0;'>
            <h2 style='color: #F5F5DC; margin: 0;'>🏢</h2>
            <h3 style='color: #F5F5DC; margin: 10px 0; font-size: 18px;'>재택근무 관리 시스템</h3>
            <p style='color: #C8D5B9; font-size: 12px; margin: 0;'>v2.0 Professional</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; margin: 20px 0;'>
            <p style='margin: 5px 0; font-size: 14px;'><b>👤 {st.session_state.full_name}</b></p>
            <p style='margin: 5px 0; font-size: 12px; color: #C8D5B9;'>🔑 {st.session_state.role}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation menu - 권한별 분리
        if 'nav_page' not in st.session_state:
            st.session_state.nav_page = "dashboard"
        
        if is_admin():
            # 관리자 메뉴
            st.markdown("### 📋 메인 메뉴")
            admin_pages = {
                "📊 대시보드": "dashboard",
                "⚡ 간편 출퇴근": "quick_work",
                "✏️ 근무 기록 입력": "work_entry",
                "🔍 근무 기록 조회": "view_logs",
                "📥 보고서 출력": "reports"
            }
            
            for label, page_id in admin_pages.items():
                if st.button(label, use_container_width=True, 
                            type="primary" if st.session_state.nav_page == page_id else "secondary",
                            key=f"nav_{page_id}"):
                    st.session_state.nav_page = page_id
                    st.rerun()
            
            st.markdown("### ⚙️ 관리자 전용")
            admin_only_pages = {
                "👥 직원 관리": "employee_management",
                "📦 일괄 입력": "admin_tools",
                "⚙️ 시스템 설정": "system_settings"
            }
            
            for label, page_id in admin_only_pages.items():
                if st.button(label, use_container_width=True, 
                            type="primary" if st.session_state.nav_page == page_id else "secondary",
                            key=f"nav_{page_id}"):
                    st.session_state.nav_page = page_id
                    st.rerun()
        else:
            # 일반 사용자 메뉴
            st.markdown("### 📋 메뉴")
            user_pages = {
                "📊 대시보드": "dashboard",
                "⚡ 간편 출퇴근": "quick_work",
                "🔍 내 근무 기록": "view_logs"
            }
            
            for label, page_id in user_pages.items():
                if st.button(label, use_container_width=True, 
                            type="primary" if st.session_state.nav_page == page_id else "secondary",
                            key=f"nav_user_{page_id}"):
                    st.session_state.nav_page = page_id
                    st.rerun()
        
        st.markdown("---")
        
        # 통합 대시보드 이동 버튼
        if st.button("🏠 통합 대시보드로 이동", use_container_width=True, key="home_button"):
            st.info("🌐 브라우저에서 http://localhost:8000 로 접속하세요")
        
        if st.button("🚪 로그아웃", use_container_width=True, key="nav_logout"):
            logout()
            st.rerun()
        
        # Footer
        st.markdown("""
        <div style='text-align: center; font-size: 11px; color: #C8D5B9; margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(200, 213, 185, 0.3);'>
        © 2026 RWM System<br>
        <span style='color: #9CAF88;'>🔒 Secured by Argon2</span>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main application entry point"""
    # Initialize
    init_app()
    
    # Check authentication
    if not is_authenticated():
        login_page()
        return
    
    # Show sidebar navigation
    sidebar_navigation()
    
    # Route to selected page
    page = st.session_state.get('nav_page', 'dashboard')
    
    if page == 'dashboard':
        dashboard_page()
    elif page == 'quick_work':
        quick_work_entry_page()
    elif page == 'work_entry':
        work_entry_page()
    elif page == 'view_logs':
        view_logs_page()
    elif page == 'employee_management':
        employee_management_page()
    elif page == 'admin_tools':
        admin_tools_page()
    elif page == 'reports':
        reports_page()
    elif page == 'system_settings':
        system_settings_page()
    else:
        dashboard_page()


if __name__ == "__main__":
    main()
