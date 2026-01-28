"""
admin_tools.py
Remote Work Management System - Admin Tools
Bulk History Injector, Smart Randomizer, Inline Editor
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta, time
import random
from typing import List, Dict
from database import (
    bulk_add_work_logs, get_work_logs, update_work_log, 
    delete_work_log, add_system_log, get_all_employees
)
from work_schedules import WORK_SCHEDULE_PRESETS
from holidays import is_workday, get_holiday_name
from department_tasks import get_department_tasks


def add_random_minutes_seconds(base_time: time, min_offset: int = 1, max_offset: int = 7) -> time:
    """
    Add random minutes and seconds to base time
    Args:
        base_time: Base time object
        min_offset: Minimum minutes to add (can be negative)
        max_offset: Maximum minutes to add
    Returns:
        New time object with random offset
    """
    # Convert to datetime for easier manipulation
    dt = datetime.combine(date.today(), base_time)
    
    # Add random minutes
    random_minutes = random.randint(min_offset, max_offset)
    dt += timedelta(minutes=random_minutes)
    
    # Add random seconds (0-59)
    random_seconds = random.randint(0, 59)
    dt += timedelta(seconds=random_seconds)
    
    return dt.time()


def calculate_work_hours(start_time: str, end_time: str, break_duration: float = 1.0) -> float:
    """
    Calculate work hours
    Args:
        start_time: "HH:MM" or "HH:MM:SS"
        end_time: "HH:MM" or "HH:MM:SS"
        break_duration: Break time in hours
    Returns:
        Work hours as float
    """
    try:
        # Parse time strings
        start_parts = start_time.split(':')
        end_parts = end_time.split(':')
        
        start_dt = datetime.strptime(f"{start_parts[0]}:{start_parts[1]}", "%H:%M")
        end_dt = datetime.strptime(f"{end_parts[0]}:{end_parts[1]}", "%H:%M")
        
        # Calculate difference
        diff = (end_dt - start_dt).total_seconds() / 3600
        
        # Subtract break time
        work_hours = max(0, diff - break_duration)
        
        return round(work_hours, 2)
    except Exception as e:
        st.error(f"시간 계산 오류: {e}")
        return 0.0


def generate_weekday_dates(start_date: date, end_date: date) -> List[date]:
    """
    Generate list of workday dates (Monday-Friday, excluding holidays) between start and end
    주말(토/일)과 법정 공휴일을 자동으로 제외합니다.
    """
    dates = []
    current = start_date
    while current <= end_date:
        # Check if it's a workday (Mon-Fri and not a holiday)
        if is_workday(current):
            dates.append(current)
        current += timedelta(days=1)
    return dates


def bulk_history_injector():
    """Admin tool: Bulk insert work history - REDESIGNED"""
    st.subheader("📦 일괄 기록 생성")
    
    # 상단 정보 카드
    st.markdown("""
    <div style='background: linear-gradient(135deg, #D1ECF1 0%, #BEE5EB 100%); 
                padding: 25px; border-radius: 15px; margin-bottom: 30px; 
                border-left: 5px solid #17A2B8;'>
        <h4 style='color: #0C5460; margin: 0 0 15px 0;'>⚡ 빠른 대량 생성</h4>
        <ul style='color: #0C5460; margin: 0; font-size: 14px; line-height: 1.8;'>
            <li>✅ <b>평일만 자동 선택</b> (토/일 제외)</li>
            <li>✅ <b>법정 공휴일 자동 제외</b> (신정, 설날, 추석 등)</li>
            <li>✅ 시간 자동 랜덤화 (자연스러운 패턴)</li>
            <li>✅ 업무 내용 자동 생성 (15가지 템플릿)</li>
            <li>✅ 한 번에 최대 100일 생성 가능</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Step 1: 직원 선택 (form 밖)
    st.markdown("### 1️⃣ 직원 선택")
    employees = get_all_employees()
    emp_options = {f"👤 {emp['name']} ({emp['emp_id']}) - {emp['department']} {emp['position']}": emp['emp_id'] 
                  for emp in employees}
    selected_emp = st.selectbox("대상 직원", options=list(emp_options.keys()), 
                                help="근무 기록을 생성할 직원을 선택하세요")
    emp_id = emp_options[selected_emp]
    
    st.write("---")
    
    # Step 2: 입력 모드 선택 (form 밖 - 즉시 반영)
    st.markdown("### 2️⃣ 입력 모드 선택")
    input_mode = st.radio(
        "입력 방식을 선택하세요",
        ["📦 표준 모드 - 모든 날짜에 동일한 시간 적용 (빠름)", 
         "⚙️ 고급 모드 - 날짜별로 다른 시간 설정 (유연함)"],
        label_visibility="collapsed",
        help="표준 모드: 같은 시간대로 빠르게 생성 / 고급 모드: 각 날짜마다 다른 출퇴근 시간 설정"
    )
    
    is_advanced_mode = "고급 모드" in input_mode
    
    if is_advanced_mode:
        st.info("⚙️ 고급 모드: 날짜를 먼저 선택하면 각 날짜별로 시간을 개별 설정할 수 있습니다.")
    else:
        st.success("📦 표준 모드: 빠르게 일괄 생성합니다.")
    
    st.write("---")
    
    with st.form("bulk_injector_form"):
        
        # Step 3: 기간 설정
        st.markdown("### 3️⃣ 생성 기간")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            start_date = st.date_input("📅 시작일", value=date(2026, 1, 21))
        with col2:
            end_date = st.date_input("📅 종료일", value=date(2026, 2, 27))
        with col3:
            if start_date and end_date:
                weekdays = generate_weekday_dates(start_date, end_date)
                total_days = (end_date - start_date).days + 1
                excluded = total_days - len(weekdays)
                st.metric("📊 근무일", f"{len(weekdays)}일", 
                         delta=f"제외: {excluded}일" if excluded > 0 else "주말/공휴일 없음",
                         delta_color="off")
        
        st.write("---")
        
        # ===== 표준 모드와 고급 모드 분기 =====
        if not is_advanced_mode:
            # ==================== 표준 모드 ====================
            # Step 4: 근무 시간대 선택 (시차 출퇴근제)
            st.markdown("### 4️⃣ 근무 시간대 설정")
            
            # 프리셋 선택
            preset_names = [preset["name"] for preset in WORK_SCHEDULE_PRESETS.values()]
            selected_preset_name = st.selectbox(
                "🕐 근무 시간대 프리셋",
                options=preset_names,
                help="시차 출퇴근제 또는 단축근무 프리셋을 선택하세요"
            )
            
            # 선택된 프리셋 찾기
            selected_preset = None
            for key, preset in WORK_SCHEDULE_PRESETS.items():
                if preset["name"] == selected_preset_name:
                    selected_preset = preset
                    break
            
            # 맞춤형 선택 시 직접 입력, 아니면 프리셋 사용
            if "맞춤형" in selected_preset_name:
                col3, col4, col5 = st.columns(3)
                with col3:
                    st.markdown("**🌅 출근 시간**")
                    base_start = st.time_input("기준 시간", value=time(9, 0), label_visibility="collapsed")
                    start_random_min = st.slider("랜덤 범위 (±분)", 0, 10, 5, 
                                                help="예: 5분 → 08:55 ~ 09:05 사이 랜덤", key="start_rand")
                    st.success(f"✅ {base_start.strftime('%H:%M')} ± {start_random_min}분")
                
                with col4:
                    st.markdown("**🌆 퇴근 시간**")
                    base_end = st.time_input("기준 시간", value=time(18, 0), label_visibility="collapsed")
                    end_random_min = st.slider("랜덤 범위 (+분)", 0, 15, 7,
                                              help="예: 7분 → 18:00 ~ 18:07 사이 랜덤", key="end_rand")
                    st.success(f"✅ {base_end.strftime('%H:%M')} + 0~{end_random_min}분")
                
                with col5:
                    st.markdown("**☕ 휴게 시간**")
                    break_time_preset = st.selectbox(
                        "시간 선택",
                        options=[
                            "12:00-13:00 (1시간)",
                            "12:30-13:30 (1시간)",
                            "13:00-14:00 (1시간)",
                            "직접 입력"
                        ],
                        label_visibility="collapsed",
                        key="break_preset"
                    )
                    
                    if "직접 입력" in break_time_preset:
                        break_time = st.text_input("입력", value="12:00-13:00", placeholder="예: 12:00-13:00")
                    else:
                        break_time = break_time_preset.split(" (")[0]
                    
                    st.success(f"✅ {break_time}")
            else:
                # 프리셋 사용
                base_start = selected_preset["start_time"]
                base_end = selected_preset["end_time"]
                break_time = selected_preset["break_time"]
                start_random_min = selected_preset["random_start_max"]
                end_random_min = selected_preset["random_end_max"]
                
                # 프리셋 정보 표시
                col3, col4, col5 = st.columns(3)
                with col3:
                    st.markdown("**🌅 출근 시간**")
                    st.info(f"{base_start.strftime('%H:%M')} ± {start_random_min}분")
                with col4:
                    st.markdown("**🌆 퇴근 시간**")
                    st.info(f"{base_end.strftime('%H:%M')} + 0~{end_random_min}분")
                with col5:
                    st.markdown("**☕ 휴게 시간**")
                    st.info(f"{break_time}")
                
                # 미세 조정 옵션
                with st.expander("⚙️ 시간 미세 조정 (선택사항)"):
                    st.write("프리셋을 기본으로 사용하되, 필요시 시간을 수정할 수 있습니다.")
                    col_adj1, col_adj2 = st.columns(2)
                    with col_adj1:
                        adjust_start = st.time_input("출근 시간 조정", value=base_start, key="adj_start")
                        if adjust_start != base_start:
                            base_start = adjust_start
                            st.success("✅ 출근 시간이 조정되었습니다.")
                    
                    with col_adj2:
                        adjust_end = st.time_input("퇴근 시간 조정", value=base_end, key="adj_end")
                        if adjust_end != base_end:
                            base_end = adjust_end
                            st.success("✅ 퇴근 시간이 조정되었습니다.")
            
            st.write("---")
            
            # Step 5: 근무 유형 선택
            st.markdown("### 5️⃣ 근무 유형")
            work_type = st.selectbox(
                "근무 형태를 선택하세요",
                ["🏠 재택근무", "🏢 사무실 출근", "🚗 외근", "✈️ 출장"],
                label_visibility="collapsed",
                key="work_type_select"
            )
            # 아이콘 제거
            work_type_clean = work_type.split(" ", 1)[1] if " " in work_type else work_type
            
            st.write("---")
            
            # Step 6: 업무 내용
            st.markdown("### 6️⃣ 업무 내용")
            work_desc_option = st.radio(
                "생성 방식",
                ["🎲 자동 생성 (추천) - 부서별 업무 템플릿에서 랜덤 선택", 
                 "📝 동일한 내용 사용 - 직접 입력"],
                label_visibility="collapsed"
            )
            
            if "동일한 내용" in work_desc_option:
                work_description = st.text_area("업무 내용 입력", 
                                              value="재택 근무 수행",
                                              height=80,
                                              placeholder="모든 날짜에 동일하게 입력될 업무 내용...")
            else:
                work_description = None
                st.success("✅ 직원의 부서에 맞는 업무 템플릿에서 자동으로 다양하게 생성됩니다.")
            
            st.write("---")
        
        else:
            # ==================== 고급 모드 ====================
            st.markdown("### 4️⃣ 개별 일정 설정 (고급 모드)")
            st.info("📝 각 날짜별로 출퇴근 시간, 휴게시간, 근무유형을 개별 설정할 수 있습니다!")
            
            if start_date > end_date:
                st.error("⚠️ 시작일이 종료일보다 늦을 수 없습니다.")
            else:
                # 근무일 목록 생성
                weekdays = generate_weekday_dates(start_date, end_date)
                
                if not weekdays:
                    st.warning("⚠️ 선택한 기간에 근무일이 없습니다. (모두 주말 또는 공휴일)")
                else:
                    # 제외된 공휴일 정보
                    from holidays import KOREAN_HOLIDAYS
                    excluded_holidays = []
                    current = start_date
                    while current <= end_date:
                        if current in KOREAN_HOLIDAYS and current not in weekdays:
                            excluded_holidays.append((current, KOREAN_HOLIDAYS[current]))
                        current += timedelta(days=1)
                    
                    if excluded_holidays:
                        with st.expander(f"📅 제외된 공휴일 ({len(excluded_holidays)}일)", expanded=False):
                            for holiday_date, holiday_name in excluded_holidays:
                                st.write(f"- {holiday_date.strftime('%Y-%m-%d')} ({holiday_date.strftime('%a')}): **{holiday_name}**")
                    
                    # 직원의 부서 정보 가져오기
                    from database import get_employee_by_id
                    employee = get_employee_by_id(emp_id)
                    employee_department = employee['department'] if employee else "기타"
                    department_task_templates = get_department_tasks(employee_department)
                    
                    # 초기 데이터프레임 생성 (세션 스테이트 활용)
                    if 'advanced_schedule_df' not in st.session_state or st.session_state.get('schedule_emp_id') != emp_id or st.session_state.get('schedule_dates') != (start_date, end_date):
                        # 기본 값으로 데이터프레임 생성
                        schedule_data = []
                        for work_date in weekdays:
                            schedule_data.append({
                                '날짜': work_date.strftime('%Y-%m-%d'),
                                '요일': ['월', '화', '수', '목', '금', '토', '일'][work_date.weekday()],
                                '출근시간': '09:00',
                                '퇴근시간': '18:00',
                                '휴게시간': '12:00-13:00',
                                '근무유형': '재택근무',
                                '업무내용': random.choice(department_task_templates)
                            })
                        
                        st.session_state.advanced_schedule_df = pd.DataFrame(schedule_data)
                        st.session_state.schedule_emp_id = emp_id
                        st.session_state.schedule_dates = (start_date, end_date)
                    
                    st.markdown("#### 📅 일정 편집")
                    st.caption("⬇️ 아래 테이블을 직접 수정하세요. 각 셀을 더블클릭하면 편집할 수 있습니다.")
                    
                    # 데이터 에디터
                    edited_df = st.data_editor(
                        st.session_state.advanced_schedule_df,
                        hide_index=True,
                        use_container_width=True,
                        num_rows="fixed",
                        column_config={
                            "날짜": st.column_config.TextColumn("날짜", disabled=True, width="small"),
                            "요일": st.column_config.TextColumn("요일", disabled=True, width="small"),
                            "출근시간": st.column_config.TextColumn("출근시간", width="small", help="HH:MM 형식"),
                            "퇴근시간": st.column_config.TextColumn("퇴근시간", width="small", help="HH:MM 형식"),
                            "휴게시간": st.column_config.TextColumn("휴게시간", width="small", help="HH:MM-HH:MM 형식"),
                            "근무유형": st.column_config.SelectboxColumn(
                                "근무유형",
                                options=["재택근무", "사무실 출근", "외근", "출장"],
                                width="small"
                            ),
                            "업무내용": st.column_config.TextColumn("업무내용", width="large")
                        },
                        key="schedule_editor"
                    )
                    
                    # 편집된 데이터를 세션 스테이트에 저장
                    st.session_state.advanced_schedule_df = edited_df
                    
                    # 사용 팁
                    st.info("""
                    💡 **편집 팁**
                    - 셀을 더블클릭하면 직접 수정할 수 있습니다
                    - 같은 값을 여러 행에 적용하려면: 첫 번째 셀 수정 → Ctrl+C 복사 → 다른 셀들 선택 → Ctrl+V 붙여넣기
                    - 엑셀처럼 드래그해서 여러 셀을 한번에 수정할 수 있습니다
                    """)
            
            st.write("---")
        
        # Submit button - 크고 명확하게
        if is_advanced_mode:
            submit = st.form_submit_button("🚀 고급 모드로 생성하기", type="primary", use_container_width=True)
        else:
            submit = st.form_submit_button("🚀 일괄 생성 시작", type="primary", use_container_width=True)
        
        if submit and not is_advanced_mode:
            if start_date > end_date:
                st.error("⚠️ 시작일이 종료일보다 늦을 수 없습니다.")
            else:
                # Generate weekday dates
                weekdays = generate_weekday_dates(start_date, end_date)
                
                if not weekdays:
                    st.warning("⚠️ 선택한 기간에 근무일이 없습니다. (모두 주말 또는 공휴일)")
                else:
                    # 제외된 날짜 정보 수집
                    from holidays import KOREAN_HOLIDAYS
                    excluded_holidays = []
                    current = start_date
                    while current <= end_date:
                        if current in KOREAN_HOLIDAYS and current not in weekdays:
                            excluded_holidays.append((current, KOREAN_HOLIDAYS[current]))
                        current += timedelta(days=1)
                    
                    # 제외된 공휴일이 있으면 표시
                    if excluded_holidays:
                        with st.expander(f"📅 제외된 공휴일 ({len(excluded_holidays)}일)", expanded=False):
                            for holiday_date, holiday_name in excluded_holidays:
                                st.write(f"- {holiday_date.strftime('%Y-%m-%d')} ({holiday_date.strftime('%a')}): **{holiday_name}**")
                    
                    # 직원 정보 가져오기 (부서 정보 필요)
                    from database import get_employee_by_id
                    employee = get_employee_by_id(emp_id)
                    employee_department = employee['department'] if employee else "기타"
                    
                    # 해당 부서의 업무 템플릿 가져오기
                    department_task_templates = get_department_tasks(employee_department)
                    
                    # Prepare bulk logs
                    logs = []
                    for work_date in weekdays:
                        # Randomize times
                        random_start = add_random_minutes_seconds(
                            base_start, 
                            -abs(start_random_min), 
                            abs(start_random_min)
                        )
                        random_end = add_random_minutes_seconds(
                            base_end, 
                            0, 
                            end_random_min
                        )
                        
                        # Format times
                        start_str = random_start.strftime("%H:%M:%S")
                        end_str = random_end.strftime("%H:%M:%S")
                        
                        # Calculate hours
                        work_hours = calculate_work_hours(start_str, end_str, 1.0)
                        
                        # Select work description
                        if work_description:
                            desc = work_description
                        else:
                            # 부서별 업무 템플릿에서 랜덤 선택
                            desc = random.choice(department_task_templates)
                        
                        logs.append({
                            'emp_id': emp_id,
                            'work_date': work_date.isoformat(),
                            'start_time': start_str,
                            'end_time': end_str,
                            'break_time': break_time,
                            'work_hours': work_hours,
                            'work_description': desc,
                            'work_type': work_type_clean,
                            'created_by': st.session_state.full_name,
                            'is_manual': 1
                        })
                    
                    # Insert to database
                    with st.spinner("⏳ 기록 생성 중... 잠시만 기다려주세요"):
                        count = bulk_add_work_logs(logs)
                        add_system_log(
                            st.session_state.username,
                            "일괄 기록 생성",
                            f"{emp_id} / {start_date} ~ {end_date} / {count}건"
                        )
                    
                    # 성공 메시지 - 더 눈에 띄게
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #D4EDDA 0%, #C3E6CB 100%); 
                                padding: 30px; border-radius: 15px; text-align: center;
                                border-left: 5px solid #28A745; margin: 20px 0;'>
                        <h2 style='color: #155724; margin: 0 0 10px 0;'>🎉 생성 완료!</h2>
                        <h1 style='color: #28A745; margin: 0 0 15px 0; font-size: 48px;'>{count}개</h1>
                        <p style='color: #155724; margin: 0; font-size: 16px;'>
                        {start_date} ~ {end_date} 기간의 근무 기록이 성공적으로 생성되었습니다.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 통계 카드
                    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                    with col_s1:
                        total_days = (end_date - start_date).days + 1
                        st.metric("📅 전체 기간", f"{total_days}일")
                    with col_s2:
                        excluded_count = total_days - count
                        st.metric("🚫 제외일", f"{excluded_count}일", 
                                 help="주말 및 공휴일")
                    with col_s3:
                        total_hours = sum(log['work_hours'] for log in logs)
                        st.metric("⏱️ 총 근무시간", f"{total_hours:.1f}시간")
                    with col_s4:
                        avg_hours = total_hours / count if count > 0 else 0
                        st.metric("📊 평균 시간", f"{avg_hours:.1f}시간")
                    
                    # Show preview - 더 보기 좋게
                    st.write("---")
                    with st.expander("📋 생성된 기록 상세 보기 (클릭)", expanded=False):
                        preview_df = pd.DataFrame(logs)
                        # 필요한 컬럼만 선택
                        display_cols = ['work_date', 'start_time', 'end_time', 'work_hours', 'work_description']
                        if set(display_cols).issubset(preview_df.columns):
                            preview_df_display = preview_df[display_cols].copy()
                            preview_df_display.columns = ['날짜', '시작', '종료', '시간', '업무내용']
                            st.dataframe(preview_df_display, use_container_width=True, height=400)
        
        elif submit and is_advanced_mode:
            # ==================== 고급 모드 Submit 처리 ====================
            if 'advanced_schedule_df' not in st.session_state:
                st.error("⚠️ 일정 데이터가 없습니다. 기간을 먼저 선택해주세요.")
            else:
                df = st.session_state.advanced_schedule_df
                
                # 데이터프레임에서 로그 생성
                logs = []
                error_messages = []
                
                for idx, row in df.iterrows():
                    try:
                        work_date_str = row['날짜']
                        start_time_str = row['출근시간'].strip()
                        end_time_str = row['퇴근시간'].strip()
                        break_time_str = row['휴게시간'].strip()
                        work_type_str = row['근무유형'].strip()
                        work_desc_str = row['업무내용'].strip()
                        
                        # 시간 형식 검증 및 초 추가
                        if len(start_time_str.split(':')) == 2:
                            # 초 단위 랜덤 추가
                            start_time_str += f":{random.randint(0, 59):02d}"
                        if len(end_time_str.split(':')) == 2:
                            end_time_str += f":{random.randint(0, 59):02d}"
                        
                        # 근무시간 계산
                        work_hours = calculate_work_hours(start_time_str, end_time_str, 1.0)
                        
                        logs.append({
                            'emp_id': emp_id,
                            'work_date': work_date_str,
                            'start_time': start_time_str,
                            'end_time': end_time_str,
                            'break_time': break_time_str,
                            'work_hours': work_hours,
                            'work_description': work_desc_str,
                            'work_type': work_type_str,
                            'created_by': st.session_state.full_name,
                            'is_manual': 1
                        })
                    except Exception as e:
                        error_messages.append(f"❌ {row['날짜']} 행 오류: {str(e)}")
                
                if error_messages:
                    st.error("일부 데이터에 오류가 있습니다:")
                    for msg in error_messages:
                        st.write(msg)
                else:
                    # 데이터베이스에 저장
                    with st.spinner("⏳ 고급 모드로 기록 생성 중... 잠시만 기다려주세요"):
                        count = bulk_add_work_logs(logs)
                        add_system_log(
                            st.session_state.username,
                            "일괄 기록 생성 (고급 모드)",
                            f"{emp_id} / {count}건"
                        )
                    
                    # 성공 메시지
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #D4EDDA 0%, #C3E6CB 100%); 
                                padding: 30px; border-radius: 15px; text-align: center;
                                border-left: 5px solid #28A745; margin: 20px 0;'>
                        <h2 style='color: #155724; margin: 0 0 10px 0;'>🎉 고급 모드 생성 완료!</h2>
                        <h1 style='color: #28A745; margin: 0 0 15px 0; font-size: 48px;'>{count}개</h1>
                        <p style='color: #155724; margin: 0; font-size: 16px;'>
                        맞춤 설정된 근무 기록이 성공적으로 생성되었습니다.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 통계 카드
                    col_s1, col_s2, col_s3 = st.columns(3)
                    with col_s1:
                        st.metric("📅 생성 개수", f"{count}일")
                    with col_s2:
                        total_hours = sum(log['work_hours'] for log in logs)
                        st.metric("⏱️ 총 근무시간", f"{total_hours:.1f}시간")
                    with col_s3:
                        avg_hours = total_hours / count if count > 0 else 0
                        st.metric("📊 평균 시간", f"{avg_hours:.1f}시간")
                    
                    # 세션 스테이트 초기화
                    if 'advanced_schedule_df' in st.session_state:
                        del st.session_state.advanced_schedule_df
                    if 'schedule_emp_id' in st.session_state:
                        del st.session_state.schedule_emp_id
                    if 'schedule_dates' in st.session_state:
                        del st.session_state.schedule_dates


def inline_editor():
    """Admin tool: Edit work logs inline - FULLY REDESIGNED"""
    st.markdown("## ✏️ 근무 기록 관리")
    
    # 초기화
    if 'selected_logs' not in st.session_state:
        st.session_state.selected_logs = set()
    if 'select_all' not in st.session_state:
        st.session_state.select_all = False
    
    # Filters - 심플하게
    col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
    with col_f1:
        employees = get_all_employees()
        emp_options = ["전체"] + [f"{emp['name']} ({emp['emp_id']})" for emp in employees]
        selected_emp = st.selectbox("👤 직원 선택", options=emp_options)
    
    with col_f2:
        filter_start = st.date_input("시작일", value=date(2026, 1, 1))
    
    with col_f3:
        filter_end = st.date_input("종료일", value=date.today())
    
    # Get logs
    if selected_emp == "전체":
        emp_id = None
    else:
        emp_id = selected_emp.split('(')[1].strip(')')
    
    logs = get_work_logs(
        emp_id=emp_id,
        start_date=filter_start.isoformat(),
        end_date=filter_end.isoformat()
    )
    
    if not logs:
        st.info("📭 표시할 기록이 없습니다.")
        return
    
    # 통계 - 간결하게
    total_logs = len(logs)
    total_hours = sum(log['work_hours'] for log in logs)
    selected_count = len(st.session_state.selected_logs)
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.metric("총 기록", f"{total_logs}건")
    with col_stat2:
        st.metric("총 시간", f"{total_hours:.1f}h")
    with col_stat3:
        st.metric("선택", f"{selected_count}건", delta=f"{selected_count}/{total_logs}")
    with col_stat4:
        if selected_count > 0:
            if st.button(f"🗑️ 선택 삭제 ({selected_count}건)", type="primary", use_container_width=True):
                for log_id in list(st.session_state.selected_logs):
                    delete_work_log(log_id)
                add_system_log(
                    st.session_state.username,
                    "일괄 삭제",
                    f"{selected_count}건 삭제"
                )
                st.session_state.selected_logs.clear()
                st.success(f"✅ {selected_count}개 기록 삭제 완료!")
                st.rerun()
    
    st.write("")
    
    # 전체 선택/해제
    col_select, col_action = st.columns([1, 3])
    with col_select:
        select_all = st.checkbox("전체 선택", key="select_all_checkbox")
        if select_all != st.session_state.select_all:
            st.session_state.select_all = select_all
            if select_all:
                st.session_state.selected_logs = {log['id'] for log in logs}
            else:
                st.session_state.selected_logs.clear()
            st.rerun()
    
    with col_action:
        if len(st.session_state.selected_logs) > 0:
            st.info(f"✅ {len(st.session_state.selected_logs)}개 선택됨")
    
    st.write("---")
    
    # 테이블 형식 - 깔끔하게
    for i, log in enumerate(logs):
        # 체크박스 + 한 줄 표시
        col_check, col_date, col_time, col_hours, col_desc, col_actions = st.columns([0.3, 1, 1.5, 0.7, 2.5, 0.8])
        
        with col_check:
            is_selected = st.checkbox(
                "",
                value=log['id'] in st.session_state.selected_logs,
                key=f"check_{log['id']}",
                label_visibility="collapsed"
            )
            if is_selected:
                st.session_state.selected_logs.add(log['id'])
            else:
                st.session_state.selected_logs.discard(log['id'])
        
        with col_date:
            st.write(f"**{log['work_date']}**")
            st.caption(f"{log['emp_id']}")
        
        with col_time:
            st.write(f"{log['start_time']} → {log['end_time']}")
            st.caption(f"휴게: {log['break_time']}")
        
        with col_hours:
            st.write(f"**{log['work_hours']}h**")
            st.caption(f"{log['work_type']}")
        
        with col_desc:
            desc_short = log['work_description'][:50] + "..." if len(log['work_description']) > 50 else log['work_description']
            st.write(desc_short)
        
        with col_actions:
            col_edit, col_del = st.columns(2)
            with col_edit:
                if st.button("✏️", key=f"edit_{log['id']}", help="수정"):
                    st.session_state[f"editing_{log['id']}"] = True
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"delete_{log['id']}", help="삭제"):
                    if delete_work_log(log['id']):
                        add_system_log(st.session_state.username, "기록 삭제", f"ID {log['id']}")
                        st.success("✅ 삭제 완료")
                        st.rerun()
        
        # 수정 모드 - 인라인
        if st.session_state.get(f"editing_{log['id']}", False):
            with st.container():
                st.markdown(f"##### ✏️ 기록 수정 (ID: {log['id']})")
                with st.form(f"edit_form_{log['id']}"):
                    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
                    with col_e1:
                        new_start = st.text_input("시작", value=log['start_time'])
                    with col_e2:
                        new_end = st.text_input("종료", value=log['end_time'])
                    with col_e3:
                        new_break = st.text_input("휴게", value=log['break_time'])
                    with col_e4:
                        new_type = st.selectbox("유형", options=["재택근무", "사무실근무", "외근"],
                                               index=["재택근무", "사무실근무", "외근"].index(log['work_type']))
                    
                    new_desc = st.text_area("업무 내용", value=log['work_description'], height=80)
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("💾 저장", type="primary", use_container_width=True):
                            new_hours = calculate_work_hours(new_start, new_end, 1.0)
                            updates = {
                                'start_time': new_start,
                                'end_time': new_end,
                                'break_time': new_break,
                                'work_hours': new_hours,
                                'work_description': new_desc,
                                'work_type': new_type
                            }
                            if update_work_log(log['id'], updates, st.session_state.full_name):
                                add_system_log(st.session_state.username, "기록 수정", f"ID {log['id']}")
                                st.session_state[f"editing_{log['id']}"] = False
                                st.success("✅ 저장 완료!")
                                st.rerun()
                    with col_cancel:
                        if st.form_submit_button("❌ 취소", use_container_width=True):
                            st.session_state[f"editing_{log['id']}"] = False
                            st.rerun()
        
        st.divider()


def smart_randomizer():
    """Admin tool: Generate random realistic work times - REDESIGNED"""
    st.subheader("🎲 스마트 랜덤 생성기")
    
    # 상단 정보 카드
    st.markdown("""
    <div style='background: linear-gradient(135deg, #FFF3CD 0%, #FFE8A1 100%); 
                padding: 25px; border-radius: 15px; margin-bottom: 30px; 
                border-left: 5px solid #FFC107;'>
        <h4 style='color: #856404; margin: 0 0 10px 0;'>🎯 자연스러운 시간 생성</h4>
        <p style='color: #856404; margin: 0; font-size: 14px;'>
        정각이 아닌 실제 사람처럼 랜덤한 초 단위까지 포함된 시간을 생성합니다.<br>
        예: 11:00 → 11:03:47, 10:57:23 등 (매번 다름)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌅 출근 시간")
        base_start = st.time_input("기준 시간", value=time(11, 0), key="rand_start")
        start_range = st.slider("랜덤 범위 (±분)", 0, 10, 5, key="rand_start_range",
                               help="기준 시간에서 앞뒤로 이 범위만큼 랜덤")
        
        if st.button("🎲 생성하기", use_container_width=True, key="gen_start", type="primary"):
            random_time = add_random_minutes_seconds(base_start, -abs(start_range), abs(start_range))
            st.markdown(f"""
            <div style='background: #D4EDDA; padding: 20px; border-radius: 10px; text-align: center;
                       border-left: 4px solid #28A745; margin-top: 15px;'>
                <h3 style='color: #155724; margin: 0 0 10px 0;'>✅ 생성 완료</h3>
                <h2 style='color: #28A745; margin: 0; font-size: 36px; font-weight: 800;'>
                    {random_time.strftime('%H:%M:%S')}
                </h2>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🌆 퇴근 시간")
        base_end = st.time_input("기준 시간", value=time(18, 0), key="rand_end")
        end_range = st.slider("랜덤 범위 (+분)", 0, 15, 7, key="rand_end_range",
                             help="기준 시간에서 뒤로 이 범위만큼 랜덤")
        
        if st.button("🎲 생성하기", use_container_width=True, key="gen_end", type="primary"):
            random_time = add_random_minutes_seconds(base_end, 0, end_range)
            st.markdown(f"""
            <div style='background: #D4EDDA; padding: 20px; border-radius: 10px; text-align: center;
                       border-left: 4px solid #28A745; margin-top: 15px;'>
                <h3 style='color: #155724; margin: 0 0 10px 0;'>✅ 생성 완료</h3>
                <h2 style='color: #28A745; margin: 0; font-size: 36px; font-weight: 800;'>
                    {random_time.strftime('%H:%M:%S')}
                </h2>
            </div>
            """, unsafe_allow_html=True)
    
    # Batch generation
    st.write("---")
    st.markdown("### 📊 일괄 샘플 생성")
    st.info("💡 10개의 샘플을 한 번에 생성하여 패턴을 확인할 수 있습니다.")
    
    if st.button("🎲 10개 샘플 생성", type="primary", use_container_width=True, key="gen_batch"):
        samples = []
        for i in range(10):
            start = add_random_minutes_seconds(time(11, 0), -5, 5)
            end = add_random_minutes_seconds(time(18, 0), 0, 10)
            hours = calculate_work_hours(start.strftime("%H:%M:%S"), end.strftime("%H:%M:%S"))
            samples.append({
                '순번': f"#{i + 1}",
                '출근 시간': start.strftime("%H:%M:%S"),
                '퇴근 시간': end.strftime("%H:%M:%S"),
                '근무 시간': f"{hours}시간"
            })
        
        st.markdown("### 📋 생성 결과")
        st.dataframe(pd.DataFrame(samples), use_container_width=True, hide_index=True)
