"""
재택근무 관리시스템 - 캘린더 뷰
월별 캘린더로 근무 현황을 한눈에 확인
"""

import streamlit as st
import calendar
from datetime import datetime, date, timedelta
import sys
from pathlib import Path

# 상위 디렉토리 모듈 import
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.database import get_all_employees, get_employee_by_name
from database import get_db_connection

# 페이지 설정
st.set_page_config(
    page_title="재택근무 캘린더",
    page_icon="📅",
    layout="wide"
)

# CSS 스타일
st.markdown("""
<style>
    .calendar-day {
        border: 1px solid #ddd;
        padding: 10px;
        min-height: 80px;
        border-radius: 5px;
        background-color: #fff;
    }
    .calendar-day-header {
        font-weight: bold;
        margin-bottom: 5px;
        color: #333;
    }
    .work-remote {
        background-color: #e3f2fd !important;
        border-left: 3px solid #2196f3;
    }
    .work-office {
        background-color: #f3e5f5 !important;
        border-left: 3px solid #9c27b0;
    }
    .work-leave {
        background-color: #fff3e0 !important;
        border-left: 3px solid #ff9800;
    }
    .weekend {
        background-color: #fafafa !important;
    }
    .today {
        border: 2px solid #4caf50 !important;
        box-shadow: 0 2px 4px rgba(76,175,80,0.3);
    }
</style>
""", unsafe_allow_html=True)

st.title("📅 재택근무 캘린더")
st.markdown("월별 근무 현황을 캘린더 형식으로 확인합니다.")

st.divider()

# ============================================================
# 년월 선택
# ============================================================

col1, col2, col3 = st.columns([2, 2, 6])

with col1:
    current_year = datetime.now().year
    selected_year = st.selectbox(
        "년도",
        range(current_year - 1, current_year + 2),
        index=1
    )

with col2:
    current_month = datetime.now().month
    selected_month = st.selectbox(
        "월",
        range(1, 13),
        index=current_month - 1
    )

# ============================================================
# 직원 선택
# ============================================================

employees = get_all_employees(active_only=True)
employee_names = ["전체 직원"] + [emp['name'] for emp in employees]

selected_name = st.selectbox("👤 직원 선택", employee_names)

st.divider()

# ============================================================
# 캘린더 데이터 조회
# ============================================================

# 선택한 월의 근무 로그 조회
with get_db_connection() as conn:
    cursor = conn.cursor()
    
    if selected_name == "전체 직원":
        # 전체 직원의 근무 로그
        cursor.execute("""
        SELECT e.name, w.work_date, w.work_type, w.work_location, w.notes
        FROM work_logs w
        JOIN employees e ON w.emp_id = e.emp_id
        WHERE strftime('%Y', w.work_date) = ? AND strftime('%m', w.work_date) = ?
        ORDER BY w.work_date, e.name
        """, (str(selected_year), f"{selected_month:02d}"))
    else:
        # 특정 직원의 근무 로그
        employee = get_employee_by_name(selected_name)
        emp_id = employee['emp_id']
        
        cursor.execute("""
        SELECT e.name, w.work_date, w.work_type, w.work_location, w.notes
        FROM work_logs w
        JOIN employees e ON w.emp_id = e.emp_id
        WHERE w.emp_id = ? AND strftime('%Y', w.work_date) = ? AND strftime('%m', w.work_date) = ?
        ORDER BY w.work_date
        """, (emp_id, str(selected_year), f"{selected_month:02d}"))
    
    work_logs = cursor.fetchall()

# 로그를 딕셔너리로 변환 (날짜별)
work_dict = {}
for log in work_logs:
    work_date = log[1]  # work_date
    if work_date not in work_dict:
        work_dict[work_date] = []
    
    work_dict[work_date].append({
        'name': log[0],
        'work_type': log[2],
        'work_location': log[3],
        'notes': log[4]
    })

# ============================================================
# 캘린더 렌더링
# ============================================================

st.subheader(f"📆 {selected_year}년 {selected_month}월")

# 범례
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("🏠 **재택근무** - 파란색")
with col2:
    st.markdown("🏢 **사무실근무** - 보라색")
with col3:
    st.markdown("🏖️ **휴가/휴직** - 주황색")
with col4:
    st.markdown("✅ **오늘** - 녹색 테두리")

st.divider()

# 캘린더 생성
cal = calendar.monthcalendar(selected_year, selected_month)
today = date.today()

# 요일 헤더
weekdays = ['월', '화', '수', '목', '금', '토', '일']
cols = st.columns(7)
for i, day in enumerate(weekdays):
    with cols[i]:
        st.markdown(f"**{day}**")

# 각 주별로 렌더링
for week in cal:
    cols = st.columns(7)
    
    for i, day in enumerate(week):
        with cols[i]:
            if day == 0:
                # 빈 날짜
                st.markdown('<div class="calendar-day"></div>', unsafe_allow_html=True)
            else:
                # 날짜 객체 생성
                current_date = date(selected_year, selected_month, day)
                date_str = current_date.strftime("%Y-%m-%d")
                
                # 스타일 클래스 결정
                css_class = "calendar-day"
                
                # 주말
                if i >= 5:  # 토, 일
                    css_class += " weekend"
                
                # 오늘
                if current_date == today:
                    css_class += " today"
                
                # 근무 로그가 있으면 스타일 추가
                if date_str in work_dict:
                    # 첫 번째 로그의 근무 유형으로 배경색 결정
                    first_log = work_dict[date_str][0]
                    if '재택' in first_log['work_type']:
                        css_class += " work-remote"
                    elif '사무실' in first_log['work_type'] or '출근' in first_log['work_type']:
                        css_class += " work-office"
                    elif '휴가' in first_log['work_type'] or '휴직' in first_log['work_type']:
                        css_class += " work-leave"
                
                # 날짜 출력
                st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                st.markdown(f'<div class="calendar-day-header">{day}일</div>', unsafe_allow_html=True)
                
                # 근무 로그 출력
                if date_str in work_dict:
                    for log in work_dict[date_str]:
                        if selected_name == "전체 직원":
                            st.caption(f"{log['name']}: {log['work_type']}")
                        else:
                            st.caption(f"{log['work_type']}")
                
                st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 통계
# ============================================================

st.divider()

st.subheader("📊 이번 달 통계")

if work_logs:
    # 근무 유형별 집계
    work_type_count = {}
    for log in work_logs:
        work_type = log[2]  # work_type
        work_type_count[work_type] = work_type_count.get(work_type, 0) + 1
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 근무일", len(set([log[1] for log in work_logs])))
    
    with col2:
        remote_days = sum([count for wtype, count in work_type_count.items() if '재택' in wtype])
        st.metric("재택근무", f"{remote_days}일")
    
    with col3:
        office_days = sum([count for wtype, count in work_type_count.items() if '사무실' in wtype or '출근' in wtype])
        st.metric("사무실근무", f"{office_days}일")
    
    with col4:
        leave_days = sum([count for wtype, count in work_type_count.items() if '휴가' in wtype or '휴직' in wtype])
        st.metric("휴가/휴직", f"{leave_days}일")
    
    # 근무 유형별 상세
    with st.expander("📋 근무 유형별 상세"):
        for work_type, count in sorted(work_type_count.items(), key=lambda x: x[1], reverse=True):
            st.write(f"- **{work_type}**: {count}일")

else:
    st.info(f"💡 {selected_year}년 {selected_month}월에 등록된 근무 기록이 없습니다.")

# ============================================================
# 사이드바
# ============================================================

st.sidebar.markdown("""
### 💡 캘린더 사용법

**색상 의미**
- 🔵 파란색: 재택근무
- 🟣 보라색: 사무실근무
- 🟠 주황색: 휴가/휴직
- ⬜ 회색: 주말
- 🟢 녹색 테두리: 오늘

**기능**
- 년월 선택으로 다른 달 보기
- 직원 선택으로 개인별 캘린더
- 통계로 한눈에 파악

**팁**
- 전체 직원 선택 시 모든 근무 현황 확인
- 개인 선택 시 상세 근무 패턴 분석
""")

st.sidebar.divider()

st.sidebar.success("""
✅ **활용 방안**

- 월별 재택근무 현황 파악
- 팀별 근무 일정 조율
- 휴가 계획 수립
- 근무 패턴 분석
""")
