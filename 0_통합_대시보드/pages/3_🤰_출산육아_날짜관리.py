"""
날짜 정보 관리 페이지 (통합 대시보드)
직원의 임신/출산/휴직 관련 날짜를 직접 입력/수정
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
import json

# shared 모듈 import
sys.path.append(str(Path(__file__).parent.parent.parent))
from shared.database import (
    get_all_employees,
    get_employee_by_id,
    get_employee_by_name,
    update_employee
)
from shared.design import apply_design
from shared.utils import show_success

# 페이지 설정
st.set_page_config(
    page_title="출산·육아 날짜 관리",
    page_icon="🤰",
    layout="wide"
)

# 모던 그린 미니멀 디자인 적용
apply_design()

st.title("🤰 출산·육아 날짜 관리")
st.markdown("""
직원의 임신/출산/휴직 관련 날짜를 입력하고 관리합니다.  
**여기서 입력한 정보는 모든 자동화 시스템에 자동으로 연동됩니다.**
""")

# 직원 선택
employees = get_all_employees(active_only=True)
if not employees:
    st.warning("⚠️ 등록된 직원이 없습니다. 먼저 직원을 등록해주세요.")
    st.stop()

employee_names = [emp['name'] for emp in employees]

selected_name = st.selectbox("👤 직원 선택", employee_names, key="employee_select")

if selected_name:
    employee = get_employee_by_name(selected_name)
    
    # 기존 날짜 정보 불러오기
    existing_dates = {}
    if employee.get('notes'):
        try:
            existing_dates = json.loads(employee['notes'])
        except:
            pass
    
    st.divider()
    
    st.subheader(f"📋 {employee['name']}님의 날짜 정보")
    
    with st.form("date_info_form"):
        st.markdown("### 🤰 임신 관련 날짜")
        
        col1, col2 = st.columns(2)
        
        # 기존 데이터 파싱
        pregnancy_data = existing_dates.get('pregnancy_dates', {})
        maternity_data = existing_dates.get('maternity', {})
        parental_data = existing_dates.get('parental_leave', {})
        replacement_data = existing_dates.get('replacement', {})
        
        with col1:
            pregnancy_confirmed = st.date_input(
                "임신 확인일",
                value=datetime.fromisoformat(pregnancy_data.get('confirmed')).date() if pregnancy_data.get('confirmed') else None,
                help="임신이 확인된 날짜"
            )
            
            expected_delivery = st.date_input(
                "출산 예정일",
                value=datetime.fromisoformat(pregnancy_data.get('expected_delivery')).date() if pregnancy_data.get('expected_delivery') else None,
                help="예상 출산 날짜"
            )
        
        with col2:
            short_work_start = st.date_input(
                "단축근무 시작일",
                value=datetime.fromisoformat(pregnancy_data.get('short_work_start')).date() if pregnancy_data.get('short_work_start') else None,
                help="임신 중 근로시간 단축 시작일"
            )
            
            short_work_end = st.date_input(
                "단축근무 종료일",
                value=datetime.fromisoformat(pregnancy_data.get('short_work_end')).date() if pregnancy_data.get('short_work_end') else None,
                help="임신 중 근로시간 단축 종료일"
            )
            
            # 자동 계산: 단축근무 일수
            if short_work_start and short_work_end:
                short_work_days = (short_work_end - short_work_start).days + 1
                st.success(f"📊 단축근무 기간: **{short_work_days}일**")
            else:
                st.info("💡 시작일과 종료일을 선택하면 자동 계산됩니다")
        
        # 근무시간 설정
        st.markdown("#### ⏰ 단축근무 시간")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            work_start_time = st.time_input(
                "출근 시간",
                value=datetime.strptime(pregnancy_data.get('work_start_time', "10:00"), "%H:%M").time(),
                help="단축근무 시 출근 시간"
            )
        
        with col2:
            work_end_time = st.time_input(
                "퇴근 시간",
                value=datetime.strptime(pregnancy_data.get('work_end_time', "18:00"), "%H:%M").time(),
                help="단축근무 시 퇴근 시간"
            )
        
        with col3:
            work_hours = st.number_input(
                "실근로시간",
                min_value=4,
                max_value=8,
                value=pregnancy_data.get('work_hours', 7),
                help="하루 실제 근무 시간"
            )
        
        st.divider()
        
        st.markdown("### 👶 출산 휴가")
        
        col1, col2 = st.columns(2)
        
        with col1:
            maternity_start = st.date_input(
                "출산휴가 시작일",
                value=datetime.fromisoformat(maternity_data.get('start')).date() if maternity_data.get('start') else None,
                help="출산전후휴가 시작 날짜"
            )
            
            maternity_end = st.date_input(
                "출산휴가 종료일",
                value=datetime.fromisoformat(maternity_data.get('end')).date() if maternity_data.get('end') else None,
                help="출산전후휴가 종료 날짜 (법정 90일)"
            )
            
            # 자동 계산: 출산휴가 일수
            maternity_days = 90  # 기본값
            if maternity_start and maternity_end:
                maternity_days_calc = (maternity_end - maternity_start).days + 1
                st.success(f"📊 출산휴가 기간: **{maternity_days_calc}일**")
                maternity_days = maternity_days_calc
            else:
                st.info("💡 시작일과 종료일을 선택하면 자동 계산됩니다")
        
        with col2:
            actual_delivery = st.date_input(
                "실제 출산일",
                value=datetime.fromisoformat(maternity_data.get('actual_delivery')).date() if maternity_data.get('actual_delivery') else None,
                help="실제로 출산한 날짜"
            )
            
            is_multiple = st.checkbox(
                "다태아 출산",
                value=maternity_data.get('is_multiple', False),
                help="쌍둥이 이상의 경우 체크 (120일)"
            )
            
            if is_multiple:
                st.info("💡 다태아는 법정 휴가 120일")
        
        st.divider()
        
        st.markdown("### 🍼 육아 휴직")
        
        col1, col2 = st.columns(2)
        
        with col1:
            parental_start = st.date_input(
                "육아휴직 시작일",
                value=datetime.fromisoformat(parental_data.get('start')).date() if parental_data.get('start') else None,
                help="육아휴직 시작 날짜"
            )
            
            parental_end = st.date_input(
                "육아휴직 종료일",
                value=datetime.fromisoformat(parental_data.get('end')).date() if parental_data.get('end') else None,
                help="육아휴직 종료 날짜 (최대 1년)"
            )
            
            # 자동 계산: 육아휴직 일수 및 개월
            parental_months = 12  # 기본값
            parental_days = 365  # 기본값
            if parental_start and parental_end:
                parental_days = (parental_end - parental_start).days + 1
                parental_months_calc = round(parental_days / 30.0, 1)
                st.success(f"📊 육아휴직 기간: **{parental_days}일** (약 **{parental_months_calc}개월**)")
                parental_months = int(parental_months_calc)
            else:
                st.info("💡 시작일과 종료일을 선택하면 자동 계산됩니다")
        
        with col2:
            st.markdown("#### 📊 육아휴직 정보")
            if parental_start and parental_end:
                st.metric("총 일수", f"{parental_days}일")
                st.metric("총 개월", f"{parental_months_calc}개월")
                st.metric("총 주", f"{parental_days // 7}주")
            else:
                st.info("왼쪽에서 날짜를 선택하세요")
        
        st.divider()
        
        st.markdown("### 👥 대체인력")
        
        col1, col2 = st.columns(2)
        
        with col1:
            replacement_hire = st.date_input(
                "대체인력 채용일",
                value=datetime.fromisoformat(replacement_data.get('hire_date')).date() if replacement_data.get('hire_date') else None,
                help="대체인력 채용 날짜"
            )
            
            handover_start = st.date_input(
                "인수인계 시작일",
                value=datetime.fromisoformat(replacement_data.get('handover_start')).date() if replacement_data.get('handover_start') else None,
                help="업무 인수인계 시작 날짜"
            )
        
        with col2:
            handover_end = st.date_input(
                "인수인계 종료일",
                value=datetime.fromisoformat(replacement_data.get('handover_end')).date() if replacement_data.get('handover_end') else None,
                help="업무 인수인계 완료 날짜"
            )
            
            # 자동 계산: 인수인계 일수
            handover_days = 20  # 기본값
            if handover_start and handover_end:
                handover_days = (handover_end - handover_start).days + 1
                st.success(f"📊 인수인계 기간: **{handover_days}일**")
                
                # 주말 제외 영업일 계산
                business_days = 0
                current_date = handover_start
                while current_date <= handover_end:
                    if current_date.weekday() < 5:  # 월~금
                        business_days += 1
                    current_date += timedelta(days=1)
                st.info(f"💼 영업일 기준: **{business_days}일** (주말 제외)")
            else:
                st.info("💡 시작일과 종료일을 선택하면 자동 계산됩니다")
        
        st.divider()
        
        # 저장 버튼
        submitted = st.form_submit_button("💾 날짜 정보 저장", type="primary", use_container_width=True)
        
        if submitted:
            try:
                # 자동 계산된 값들 준비
                short_work_days_final = (short_work_end - short_work_start).days + 1 if short_work_start and short_work_end else None
                maternity_days_final = (maternity_end - maternity_start).days + 1 if maternity_start and maternity_end else maternity_days
                parental_days_final = (parental_end - parental_start).days + 1 if parental_start and parental_end else None
                parental_months_final = round(parental_days_final / 30.0, 1) if parental_days_final else parental_months
                handover_days_final = (handover_end - handover_start).days + 1 if handover_start and handover_end else handover_days
                
                # 날짜 정보를 JSON 형식으로 변환
                date_info = {
                    'pregnancy_dates': {
                        'confirmed': str(pregnancy_confirmed) if pregnancy_confirmed else None,
                        'expected_delivery': str(expected_delivery) if expected_delivery else None,
                        'short_work_start': str(short_work_start) if short_work_start else None,
                        'short_work_end': str(short_work_end) if short_work_end else None,
                        'short_work_days': short_work_days_final,
                        'work_start_time': work_start_time.strftime("%H:%M"),
                        'work_end_time': work_end_time.strftime("%H:%M"),
                        'work_hours': work_hours
                    },
                    'maternity': {
                        'start': str(maternity_start) if maternity_start else None,
                        'end': str(maternity_end) if maternity_end else None,
                        'actual_delivery': str(actual_delivery) if actual_delivery else None,
                        'days': maternity_days_final,
                        'is_multiple': is_multiple
                    },
                    'parental_leave': {
                        'start': str(parental_start) if parental_start else None,
                        'end': str(parental_end) if parental_end else None,
                        'days': parental_days_final,
                        'months': parental_months_final
                    },
                    'replacement': {
                        'hire_date': str(replacement_hire) if replacement_hire else None,
                        'handover_start': str(handover_start) if handover_start else None,
                        'handover_end': str(handover_end) if handover_end else None,
                        'handover_days': handover_days_final
                    }
                }
                
                # 데이터베이스 업데이트 (notes 필드에 JSON으로 저장)
                update_data = {
                    'is_pregnant': 1 if (pregnancy_confirmed or expected_delivery or short_work_start) else 0,
                    'is_on_leave': 1 if (parental_start or maternity_start) else 0,
                    'notes': json.dumps(date_info, ensure_ascii=False)
                }
                
                success = update_employee(employee['emp_id'], update_data)
                
                if success:
                    st.success(f"✅ {employee['name']}님의 날짜 정보가 저장되었습니다!")
                    st.info("""
                    💡 **다음 앱들에서 자동으로 사용됩니다:**
                    - 출산육아 자동화 (재택근무 로그, 정부 서식)
                    - 정부지원금 자동화 (지원금 계산)
                    - 재택근무 관리시스템 (일정 관리)
                    """)
                    show_success("날짜 정보가 저장되었습니다!")
                else:
                    st.error("❌ 저장에 실패했습니다. 다시 시도해주세요.")
                
            except Exception as e:
                st.error(f"❌ 저장 실패: {str(e)}")
                import traceback
                with st.expander("오류 상세 정보"):
                    st.code(traceback.format_exc())

# 안내 메시지
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.info("""
    💡 **사용 안내**
    
    1. **✨ 자동 계산 기능**
       - 📅 **단축근무**: 시작일~종료일 → 근무 일수
       - 👶 **출산휴가**: 시작일~종료일 → 휴가 일수
       - 🍼 **육아휴직**: 시작일~종료일 → 일수 및 개월
       - 👥 **인수인계**: 시작일~종료일 → 일수 및 영업일
    
    2. **모든 앱에 반영**
       - 출산육아 자동화
       - 정부지원금 자동화
       - 재택근무 관리시스템
    
    3. **언제든지 수정 가능**
    """)

with col2:
    st.success("""
    ✅ **편리한 기능**
    
    - 📅 캘린더 UI로 쉬운 날짜 선택
    - 🤖 일수 자동 계산
    - 📊 영업일 계산 (주말 제외)
    - ⏰ 시간 선택 지원
    - 💾 즉시 저장 및 모든 앱에 반영
    - 🔄 언제든지 수정 가능
    - ✨ 기존 데이터 자동 불러오기
    """)
