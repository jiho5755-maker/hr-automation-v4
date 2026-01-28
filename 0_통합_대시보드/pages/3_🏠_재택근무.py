"""
재택근무 관리 페이지
Remote Work Management Page

일정 관리, 근무 기록 추적, 월간 리포트 생성
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import date, datetime, timedelta
import calendar

# 상위 디렉토리의 shared 모듈 import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.database import get_db, get_all_employees, get_employee_by_id, add_system_log
from shared.utils import show_success, show_error, show_info, format_date, get_korean_weekday
from shared.design import apply_design

# 디자인 적용
apply_design()


# ============================================================================
# 세션 상태 초기화
# ============================================================================

def init_remote_work_state():
    """재택근무 페이지 세션 상태 초기화"""
    if 'selected_employee_id' not in st.session_state:
        st.session_state.selected_employee_id = None
    if 'current_month' not in st.session_state:
        st.session_state.current_month = date.today().replace(day=1)


# ============================================================================
# 직원 선택
# ============================================================================

def show_employee_selector():
    """직원 선택 UI"""
    
    st.markdown("### 👤 직원 선택")
    
    # 통합 DB에서 직원 목록 조회
    employees = get_all_employees(active_only=True)
    
    if not employees:
        st.warning("등록된 직원이 없습니다. '👥 직원 관리' 메뉴에서 직원을 추가하세요.")
        return None
    
    # 직원 선택 드롭다운
    employee_options = {f"{emp['name']} ({emp.get('department', 'N/A')})": emp for emp in employees}
    
    selected_name = st.selectbox(
        "직원 선택",
        options=["직원을 선택하세요..."] + list(employee_options.keys()),
        label_visibility="collapsed"
    )
    
    if selected_name != "직원을 선택하세요...":
        selected_emp = employee_options[selected_name]
        
        # session_state 업데이트
        st.session_state.selected_employee_id = selected_emp['emp_id']
        st.session_state.current_employee = selected_emp
        
        # 직원 정보 표시
        st.success(f"**{selected_emp['name']}**")
        st.caption(f"📦 {selected_emp.get('department', 'N/A')} / {selected_emp.get('position', 'N/A')}")
        
        return selected_emp
    
    return None


# ============================================================================
# 근무 기록 추가
# ============================================================================

def show_work_log_form(employee):
    """근무 기록 추가 폼"""
    
    st.markdown("### ➕ 근무 기록 추가")
    
    with st.form("work_log_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            work_date = st.date_input("근무일", value=date.today())
            work_type = st.selectbox("근무 유형", ["재택근무", "출근", "반차", "휴가"])
        
        with col2:
            start_time = st.time_input("시작 시각", value=datetime.strptime("09:00", "%H:%M").time())
            end_time = st.time_input("종료 시각", value=datetime.strptime("18:00", "%H:%M").time())
        
        work_description = st.text_area(
            "업무 내용",
            placeholder="오늘의 업무 내용을 입력하세요...",
            height=100
        )
        
        submit = st.form_submit_button("💾 저장", type="primary", use_container_width=True)
        
        if submit:
            try:
                # 근무 시간 계산
                start_dt = datetime.combine(work_date, start_time)
                end_dt = datetime.combine(work_date, end_time)
                work_hours = (end_dt - start_dt).seconds / 3600
                
                # DB에 저장
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO work_logs (
                            emp_id, work_date, work_type, start_time, end_time,
                            work_hours, work_description, status, is_manual, created_by
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        employee['emp_id'],
                        work_date.strftime('%Y-%m-%d'),
                        work_type,
                        start_time.strftime('%H:%M'),
                        end_time.strftime('%H:%M'),
                        work_hours,
                        work_description,
                        'approved',
                        1,
                        st.session_state.user.get('username')
                    ))
                    conn.commit()
                
                # 시스템 로그 기록
                add_system_log(
                    st.session_state.user.get('username'),
                    "근무 기록 추가",
                    "remote_work",
                    f"{employee['name']} - {work_date} {work_type}"
                )
                
                show_success(f"✅ 근무 기록이 저장되었습니다!")
                st.rerun()
            
            except Exception as e:
                show_error(f"오류 발생: {str(e)}")


# ============================================================================
# 근무 기록 조회
# ============================================================================

def show_work_logs(employee):
    """근무 기록 조회"""
    
    st.markdown("### 📊 근무 기록")
    
    # 기간 선택
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        start_date = st.date_input("시작일", value=date.today().replace(day=1))
    
    with col2:
        end_date = st.date_input("종료일", value=date.today())
    
    with col3:
        if st.button("🔍 조회", use_container_width=True):
            st.rerun()
    
    # DB에서 근무 기록 조회
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT work_date, work_type, start_time, end_time, work_hours, 
                   work_description, status
            FROM work_logs
            WHERE emp_id = ? 
              AND work_date >= ? 
              AND work_date <= ?
            ORDER BY work_date DESC
        """, (
            employee['emp_id'],
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        ))
        logs = cursor.fetchall()
    
    if logs:
        st.info(f"총 **{len(logs)}일**의 근무 기록이 있습니다.")
        
        # 통계
        total_hours = sum(log[4] for log in logs if log[4])
        remote_count = sum(1 for log in logs if log[1] == '재택근무')
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("총 근무 시간", f"{total_hours:.1f}시간")
        with col2:
            st.metric("재택근무 일수", f"{remote_count}일")
        
        st.divider()
        
        # 근무 기록 테이블
        for log in logs:
            work_date, work_type, start_time, end_time, work_hours, work_desc, status = log
            
            # 근무 유형별 이모지
            type_emoji = {
                '재택근무': '🏠',
                '출근': '🏢',
                '반차': '⏰',
                '휴가': '🏖️'
            }.get(work_type, '📋')
            
            # 상태별 색상
            status_emoji = {
                'approved': '✅',
                'pending': '⏳',
                'rejected': '❌'
            }.get(status, '❓')
            
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 3])
                
                with col1:
                    st.write(f"**{work_date}**")
                    st.caption(get_korean_weekday(datetime.strptime(work_date, '%Y-%m-%d').date()))
                
                with col2:
                    st.write(f"{type_emoji} {work_type}")
                
                with col3:
                    st.write(f"{start_time} - {end_time}")
                    st.caption(f"{work_hours:.1f}시간")
                
                with col4:
                    st.write(f"{status_emoji} {work_desc or 'N/A'}")
                
                st.divider()
    else:
        st.info("조회된 근무 기록이 없습니다.")


# ============================================================================
# 월간 리포트
# ============================================================================

def show_monthly_report(employee):
    """월간 리포트 생성"""
    
    st.markdown("### 📈 월간 리포트")
    
    # 월 선택
    col1, col2 = st.columns([2, 1])
    
    with col1:
        report_month = st.date_input(
            "조회 월",
            value=date.today().replace(day=1),
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("📊 리포트 생성", type="primary", use_container_width=True):
            # 해당 월의 근무 기록 조회
            year_month = report_month.strftime('%Y-%m')
            
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT work_date, work_type, work_hours
                    FROM work_logs
                    WHERE emp_id = ? 
                      AND strftime('%Y-%m', work_date) = ?
                    ORDER BY work_date
                """, (employee['emp_id'], year_month))
                logs = cursor.fetchall()
            
            if logs:
                # 통계 계산
                total_days = len(logs)
                total_hours = sum(log[2] for log in logs if log[2])
                remote_days = sum(1 for log in logs if log[1] == '재택근무')
                office_days = sum(1 for log in logs if log[1] == '출근')
                
                # 리포트 표시
                st.markdown(f"#### {report_month.strftime('%Y년 %m월')} 근무 리포트")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("총 근무일", f"{total_days}일")
                
                with col2:
                    st.metric("총 근무시간", f"{total_hours:.1f}시간")
                
                with col3:
                    st.metric("재택근무", f"{remote_days}일")
                
                with col4:
                    st.metric("출근", f"{office_days}일")
                
                # 시스템 로그 기록
                add_system_log(
                    st.session_state.user.get('username'),
                    "월간 리포트 생성",
                    "remote_work",
                    f"{employee['name']} - {year_month}"
                )
                
                show_success("✅ 월간 리포트가 생성되었습니다!")
            else:
                show_info(f"{year_month}에 근무 기록이 없습니다.")


# ============================================================================
# 메인 함수
# ============================================================================

def show():
    """재택근무 관리 페이지 메인 함수"""
    
    # 세션 상태 초기화
    init_remote_work_state()
    
    # 타이틀
    st.markdown('<div class="main-title">🏠 재택근무 관리</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">일정 관리, 근무 기록 추적, 월간 리포트 생성</div>', unsafe_allow_html=True)
    
    # 안내 메시지
    st.info("""
    **🔄 통합 DB 사용**
    
    '👥 직원 관리' 메뉴에서 추가한 직원이 자동으로 표시됩니다!
    
    근무 기록은 `work_logs` 테이블에 저장되며, 홈 대시보드에서도 조회할 수 있습니다. ✨
    """)
    
    # 레이아웃: 사이드바 + 메인
    col_sidebar, col_main = st.columns([1, 3])
    
    with col_sidebar:
        selected_employee = show_employee_selector()
    
    with col_main:
        if selected_employee:
            # 탭으로 기능 구분
            tab1, tab2, tab3 = st.tabs(["➕ 기록 추가", "📊 기록 조회", "📈 월간 리포트"])
            
            with tab1:
                show_work_log_form(selected_employee)
            
            with tab2:
                show_work_logs(selected_employee)
            
            with tab3:
                show_monthly_report(selected_employee)
        else:
            st.info("👈 좌측에서 직원을 선택하세요.")


# ============================================================================
# 페이지 실행
# ============================================================================

show()
