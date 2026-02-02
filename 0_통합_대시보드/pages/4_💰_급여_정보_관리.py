"""
급여 정보 관리 페이지
직원별 기본 급여 정보를 입력/관리
급여관리 앱(8505)에서 이 정보를 사용하여 자동 계산
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# shared 모듈 import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.database import get_db, get_all_employees
from shared.design import apply_design
from shared.utils import show_success, show_error, format_currency

# 급여관리 모듈 import (DB 함수 사용)
payroll_path = Path(__file__).parent.parent.parent / "5_급여관리_자동화"
sys.path.insert(0, str(payroll_path))

try:
    from database import (
        init_payroll_tables,
        get_payroll_setting,
        add_payroll_setting,
        update_payroll_setting
    )
    import constants as C
    PAYROLL_MODULE_LOADED = True
except Exception as e:
    PAYROLL_MODULE_LOADED = False
    PAYROLL_ERROR = str(e)

# 디자인 적용
apply_design()


# ============================================================================
# 메인 함수
# ============================================================================

def show():
    """급여 정보 관리 페이지"""
    
    # 타이틀
    st.markdown('<div class="main-title">💰 급여 정보 관리</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">직원별 기본 급여 정보 설정</div>', unsafe_allow_html=True)
    
    st.info("""
    **💡 안내**
    
    여기서 입력한 급여 정보는 **급여관리 앱(포트 8505)**에서 자동으로 사용됩니다!
    
    - ✅ 기본급, 고정 수당 입력
    - ✅ 4대보험 적용 설정
    - ✅ 포괄임금제 설정
    - ✅ DC형 퇴직연금 설정
    
    **상세 급여 계산은 급여관리 앱(8505)에서 진행하세요!**
    """)
    
    st.divider()
    
    # 모듈 로드 확인
    if not PAYROLL_MODULE_LOADED:
        st.error(f"""
        ⚠️ **급여관리 모듈을 불러올 수 없습니다**
        
        오류: {PAYROLL_ERROR}
        
        **해결 방법:**
        ```bash
        cd 5_급여관리_자동화
        pip install -r requirements.txt
        ```
        """)
        return
    
    # DB 테이블 초기화
    init_payroll_tables()
    
    # ========================================================================
    # 직원 선택
    # ========================================================================
    
    st.markdown("### 👤 직원 선택")
    
    employees = get_all_employees(active_only=True)
    
    if not employees:
        st.warning("등록된 직원이 없습니다. '👥 직원 관리' 메뉴에서 직원을 추가하세요.")
        return
    
    employee_options = {f"{emp['name']} ({emp['department']})": emp for emp in employees}
    
    selected = st.selectbox("👤 직원 선택", list(employee_options.keys()))
    
    if not selected:
        return
    
    employee = employee_options[selected]
    emp_id = employee['emp_id']
    
    st.divider()
    
    # ========================================================================
    # 급여 정보 입력
    # ========================================================================
    
    st.markdown(f"### 📝 {employee['name']}님의 급여 정보")
    
    # 기존 설정 불러오기
    existing_setting = get_payroll_setting(emp_id)
    
    # ====================================================================
    # 🚀 포괄임금제 체크박스 (폼 밖 - 즉시 반응!)
    # ====================================================================
    
    st.markdown("#### ⚙️ 근무 형태 설정")
    
    col_pre1, col_pre2 = st.columns(2)
    
    with col_pre1:
        work_type_option = st.selectbox(
            "🏢 근무형태",
            ["사무실 출퇴근", "재택근무 (간주근로시간제)"],
            index=1 if existing_setting and existing_setting.get('work_type') == '재택근무 (간주근로시간제)' else 0,
            key=f"work_type_pre_{emp_id}"
        )
    
    with col_pre2:
        is_inclusive_wage = st.checkbox(
            "💼 포괄임금제 적용",
            value=existing_setting.get('is_inclusive_wage', False) if existing_setting else False,
            help="연장/야간/휴일근무 수당이 기본급에 포함된 경우",
            disabled=(work_type_option == "재택근무 (간주근로시간제)"),
            key=f"inclusive_pre_{emp_id}"
        )
    
    # 포괄임금제 설정 미리 입력 (폼 밖)
    fixed_ot_hours_pre = 0.0
    fixed_ot_amount_pre = 0
    
    if is_inclusive_wage:
        st.markdown("#### 💼 포괄임금제 상세 설정")
        st.caption("⚠️ 시간 또는 금액 중 하나만 입력하세요 (금액 우선 적용)")
        
        col_ot1, col_ot2 = st.columns(2)
        
        # 통상임금 기준 시간급 계산 (식대 포함) - 미리보기용
        temp_base_salary = existing_setting.get('base_salary', 3000000) if existing_setting else 3000000
        temp_work_hours = existing_setting.get('work_hours', 209) if existing_setting else 209
        temp_allowances = existing_setting.get('allowances', {}) if existing_setting else {}
        temp_meal_allowance = temp_allowances.get('식대', 0)  # 식대 포함
        # 통상임금 = 기본급 + 식대
        temp_regular_wage = temp_base_salary + temp_meal_allowance
        # 통상 시급 = 통상임금 / 월 근로시간
        temp_hourly_wage = temp_regular_wage / temp_work_hours if temp_work_hours > 0 else 0
        
        with col_ot1:
            fixed_ot_hours_pre = st.number_input(
                "월 고정 OT 시간",
                min_value=0.0,
                max_value=120.0,
                value=existing_setting.get('fixed_ot_hours', 0.0) if existing_setting else 0.0,
                step=1.0,
                help="기본급에 포함된 월 시간외 근무 시간 (시간 입력 시 금액 자동 계산)",
                key=f"ot_hours_pre_{emp_id}"
            )
            
            # 시간 입력 시 금액 자동 계산 표시
            # 연장 가산 시급 = 통상 시급 * 1.5
            if fixed_ot_hours_pre > 0 and temp_hourly_wage > 0:
                overtime_hourly_wage = temp_hourly_wage * 1.5  # 연장 가산 시급
                auto_calc_amount = int(overtime_hourly_wage * fixed_ot_hours_pre)  # 원 단위 절삭
                st.success(f"💰 자동 계산: {format_currency(auto_calc_amount)}")
                st.caption(f"연장 가산 시급 {format_currency(overtime_hourly_wage)} × {fixed_ot_hours_pre}시간")
        
        with col_ot2:
            fixed_ot_amount_pre = st.number_input(
                "고정 OT 금액 (원)",
                min_value=0,
                value=existing_setting.get('fixed_ot_amount', 0) if existing_setting else 0,
                step=10000,
                help="실제 지급되는 고정 OT 금액 (금액 우선 적용, 금액 입력 시 시간 자동 계산)",
                key=f"ot_amount_pre_{emp_id}"
            )
            
            # 금액 입력 시 시간 자동 계산 표시
            # 연장 가산 시급 = 통상 시급 * 1.5
            if fixed_ot_amount_pre > 0 and temp_hourly_wage > 0:
                overtime_hourly_wage = temp_hourly_wage * 1.5  # 연장 가산 시급
                auto_calc_hours = fixed_ot_amount_pre / overtime_hourly_wage
                auto_calc_hours_rounded = round(auto_calc_hours, 1)  # 소수점 첫째 자리에서 반올림
                st.success(f"⏰ 자동 계산: {auto_calc_hours_rounded}시간")
                st.caption(f"연장수당 {format_currency(fixed_ot_amount_pre)} ÷ 연장 가산 시급 {format_currency(overtime_hourly_wage)}")
        
        # 실제 저장할 값 결정 (금액 우선)
        # 연장 가산 시급 = 통상 시급 * 1.5
        overtime_hourly_wage = temp_hourly_wage * 1.5 if temp_hourly_wage > 0 else 0
        
        if fixed_ot_amount_pre > 0:
            # 금액이 입력되면 시간을 자동 계산 (소수점 첫째 자리에서 반올림)
            if overtime_hourly_wage > 0:
                calculated_hours = fixed_ot_amount_pre / overtime_hourly_wage
                fixed_ot_hours_pre = round(calculated_hours, 1)  # 소수점 첫째 자리에서 반올림
        elif fixed_ot_hours_pre > 0:
            # 시간이 입력되면 금액을 자동 계산 (원 단위 절삭)
            if overtime_hourly_wage > 0:
                calculated_amount = overtime_hourly_wage * fixed_ot_hours_pre
                fixed_ot_amount_pre = int(calculated_amount)  # 원 단위 절삭
    
    st.divider()
    
    # 폼 시작
    with st.form(f"payroll_form_{emp_id}"):
        
        # ====================================================================
        # 기본 정보
        # ====================================================================
        
        st.markdown("#### 💵 기본 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            base_salary = st.number_input(
                "월 기본급 (원)",
                min_value=0,
                value=existing_setting['base_salary'] if existing_setting else 3000000,
                step=100000,
                help="월 기본급 (세전)"
            )
            
            work_hours = st.number_input(
                "월 근로시간",
                min_value=100,
                max_value=250,
                value=existing_setting['work_hours'] if existing_setting else 209,
                help="주 40시간 기준 209시간"
            )
        
        with col2:
            # 시간급은 아래 정기 수당 입력 후 계산됨
            if base_salary > 0 and work_hours > 0:
                st.info("""
                💡 **시간급 계산**
                
                아래 정기 수당에서 식대를 입력하면
                자동으로 계산됩니다.
                
                **계산식**: (기본급 + 식대) ÷ 월 근로시간
                """)
            
            # 고정 OT 환산 금액 표시 (기존 값으로 미리보기)
            if is_inclusive_wage and fixed_ot_hours_pre > 0:
                if base_salary > 0 and work_hours > 0:
                    existing_allowances_preview = existing_setting.get('allowances', {}) if existing_setting else {}
                    meal_allowance_preview = existing_allowances_preview.get('식대', 0)
                    accurate_hourly_wage = (base_salary + meal_allowance_preview) / work_hours
                    ot_calculated = accurate_hourly_wage * fixed_ot_hours_pre * 1.5
                    st.metric("💰 고정 OT 환산 (미리보기)", format_currency(ot_calculated))
                    st.caption("식대 입력 후 정확히 계산됩니다")
        
        st.divider()
        
        # ====================================================================
        # 정기 수당
        # ====================================================================
        
        st.markdown("#### 🎁 정기 수당 (매월 고정)")
        
        col1, col2 = st.columns(2)
        
        existing_allowances = existing_setting.get('allowances', {}) if existing_setting else {}
        
        with col1:
            meal_allowance = st.number_input(
                "식대 (비과세 최대 20만원)",
                min_value=0,
                max_value=200000,
                value=existing_allowances.get('식대', 200000),
                step=10000
            )
            
            transport_allowance = st.number_input(
                "교통비",
                min_value=0,
                value=existing_allowances.get('교통비', 100000),
                step=10000
            )
        
        with col2:
            position_allowance = st.number_input(
                "직급수당",
                min_value=0,
                value=existing_allowances.get('직급수당', 0),
                step=10000
            )
            
            duty_allowance = st.number_input(
                "직책수당",
                min_value=0,
                value=existing_allowances.get('직책수당', 0),
                step=10000
            )
        
        # 시간급 최종 계산 표시 (form 안에서 입력한 식대 값 사용)
        if base_salary > 0 and work_hours > 0:
            # 정기 고정 수당 = 식대 (통상임금 기준)
            regular_allowances = meal_allowance
            calculated_hourly_wage = (base_salary + regular_allowances) / work_hours
            
            col_calc1, col_calc2 = st.columns([2, 1])
            with col_calc1:
                st.success(f"💡 **시간급 (통상임금 기준)**: {format_currency(calculated_hourly_wage)}")
                st.caption(f"= (기본급 {format_currency(base_salary)} + 식대 {format_currency(meal_allowance)}) ÷ {work_hours}시간")
            
            # 고정 OT 환산 금액 재계산
            if is_inclusive_wage and fixed_ot_hours_pre > 0:
                # 연장 가산 시급 = 통상 시급 * 1.5
                overtime_hourly_wage = calculated_hourly_wage * 1.5
                ot_calculated = int(overtime_hourly_wage * fixed_ot_hours_pre)  # 원 단위 절삭
                with col_calc2:
                    st.success(f"💰 **고정 OT 환산**: {format_currency(ot_calculated)}")
                    st.caption(f"{fixed_ot_hours_pre}시간 × 연장 가산 시급 {format_currency(overtime_hourly_wage)}")
        
        # 포괄임금제 값은 폼 밖에서 설정한 값 사용
        fixed_ot_hours = fixed_ot_hours_pre
        fixed_ot_amount = fixed_ot_amount_pre
        work_type = work_type_option
        
        st.divider()
        
        # ====================================================================
        # DC형 퇴직연금
        # ====================================================================
        
        st.markdown("#### 💼 DC형 퇴직연금")
        
        dc_pension_rate = st.number_input(
            "DC형 퇴직연금 비율 (%)",
            min_value=0.0,
            max_value=100.0,
            value=existing_setting.get('dc_pension_rate', 8.33) if existing_setting else 8.33,
            step=0.1,
            help="월 기본급 대비 DC형 퇴직연금 적립 비율 (연 1/12 = 8.33%)"
        )
        
        dc_pension_amount = base_salary * (dc_pension_rate / 100)
        st.info(f"💼 **월 DC 퇴직연금**: {format_currency(dc_pension_amount)}")
        
        st.divider()
        
        # ====================================================================
        # 4대보험 적용
        # ====================================================================
        
        st.markdown("#### 🏥 4대 사회보험 적용")
        
        col1, col2 = st.columns(2)
        
        with col1:
            apply_pension = st.checkbox(
                "국민연금 적용",
                value=existing_setting.get('apply_pension', True) if existing_setting else True
            )
            
            apply_health = st.checkbox(
                "건강보험 적용 (장기요양 자동 포함)",
                value=existing_setting.get('apply_health', True) if existing_setting else True
            )
        
        with col2:
            apply_employment = st.checkbox(
                "고용보험 적용",
                value=existing_setting.get('apply_employment', True) if existing_setting else True
            )
        
        st.divider()
        
        # ====================================================================
        # 부양가족 (소득세 계산용)
        # ====================================================================
        
        st.markdown("#### 👨‍👩‍👧‍👦 부양가족 (소득세 계산용)")
        
        dependents = st.number_input(
            "부양가족 수 (본인 포함)",
            min_value=1,
            max_value=10,
            value=existing_setting.get('dependents', 1) if existing_setting else 1,
            help="간이세액표 적용 시 본인 포함 부양가족 수"
        )
        
        st.divider()
        
        # ====================================================================
        # 저장 버튼
        # ====================================================================
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            submit = st.form_submit_button("💾 저장", use_container_width=True, type="primary")
        
        if submit:
            try:
                # 통상임금 산정: 기본급 + 식대
                regular_wage = base_salary + meal_allowance
                # 통상 시급: 통상임금 / 209시간
                hourly_wage = regular_wage / work_hours if work_hours > 0 else 0
                
                # 급여 설정 데이터 구성
                payroll_data = {
                    'emp_id': emp_id,
                    'base_salary': base_salary,
                    'work_hours': work_hours,
                    'work_type': work_type,
                    'is_inclusive_wage': is_inclusive_wage,
                    'fixed_ot_hours': fixed_ot_hours,
                    'fixed_ot_amount': fixed_ot_amount,
                    'dc_pension_rate': dc_pension_rate,
                    'apply_pension': apply_pension,
                    'apply_health': apply_health,
                    'apply_longterm': True,  # 장기요양은 건강보험과 함께 적용
                    'apply_employment': apply_employment,
                    'dependents': dependents,
                    'hourly_wage': hourly_wage,  # 계산된 시간급 저장
                    'allowances': {
                        '식대': meal_allowance,
                        '교통비': transport_allowance,
                        '직급수당': position_allowance,
                        '직책수당': duty_allowance
                    },
                    'tax_free_items': {}  # 기본값
                }
                
                # DB 저장
                if existing_setting:
                    update_payroll_setting(emp_id, payroll_data)
                else:
                    add_payroll_setting(emp_id, payroll_data)
                
                show_success(f"✅ {employee['name']}님의 급여 정보가 저장되었습니다!")
                
                st.info("""
                💡 **다음 단계**
                
                급여관리 앱(포트 8505)에서 상세 급여를 계산하세요!
                
                ```bash
                cd 5_급여관리_자동화
                ./실행하기.command
                ```
                
                접속: http://localhost:8505
                """)
                
            except Exception as e:
                show_error(f"저장 중 오류 발생: {str(e)}")
    
    # ========================================================================
    # 기존 설정 표시
    # ========================================================================
    
    if existing_setting:
        st.divider()
        st.markdown("### 📋 현재 설정 요약")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("기본급", format_currency(existing_setting['base_salary']))
            st.metric("식대", format_currency(existing_setting['allowances'].get('식대', 0)))
        
        with col2:
            st.metric("근로시간", f"{existing_setting['work_hours']}시간")
            st.metric("교통비", format_currency(existing_setting['allowances'].get('교통비', 0)))
        
        with col3:
            st.metric("근무형태", existing_setting.get('work_type', 'N/A'))
            total_allowance = sum(existing_setting['allowances'].values())
            st.metric("총 수당", format_currency(total_allowance))
        
        # 4대보험 적용 현황
        st.markdown("#### 🏥 4대보험 적용 현황")
        
        insurance_status = []
        if existing_setting.get('apply_pension'):
            insurance_status.append("✅ 국민연금")
        if existing_setting.get('apply_health'):
            insurance_status.append("✅ 건강보험")
        if existing_setting.get('apply_employment'):
            insurance_status.append("✅ 고용보험")
        
        if insurance_status:
            st.success(" | ".join(insurance_status))
        else:
            st.warning("⚠️ 4대보험 미적용")
        
        # 포괄임금제
        if existing_setting.get('is_inclusive_wage'):
            st.info(f"""
            💼 **포괄임금제 적용 중**
            
            - 고정 OT 시간: {existing_setting.get('fixed_ot_hours', 0)}시간
            - 고정 OT 금액: {format_currency(existing_setting.get('fixed_ot_amount', 0))}
            """)
    
    st.divider()
    
    # ========================================================================
    # 전체 직원 급여 설정 현황
    # ========================================================================
    
    st.markdown("### 📊 전체 직원 급여 설정 현황")
    
    employees = get_all_employees(active_only=True)
    
    settings_data = []
    for emp in employees:
        setting = get_payroll_setting(emp['emp_id'])
        settings_data.append({
            '이름': emp['name'],
            '부서': emp['department'],
            '기본급': format_currency(setting['base_salary']) if setting else '❌ 미설정',
            '총 수당': format_currency(sum(setting['allowances'].values())) if setting and 'allowances' in setting else '0원',
            '상태': '✅ 설정 완료' if setting else '⚠️ 미설정'
        })
    
    if settings_data:
        import pandas as pd
        df = pd.DataFrame(settings_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 통계
        set_count = sum(1 for d in settings_data if d['상태'] == '✅ 설정 완료')
        unset_count = len(settings_data) - set_count
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("전체 직원", f"{len(settings_data)}명")
        
        with col2:
            st.metric("설정 완료", f"{set_count}명", delta="✅" if set_count > 0 else None)
        
        with col3:
            st.metric("미설정", f"{unset_count}명", delta="⚠️" if unset_count > 0 else None)
        
        if unset_count > 0:
            st.warning(f"""
            ⚠️ **급여 미설정 직원이 {unset_count}명 있습니다!**
            
            위에서 직원을 선택하여 급여 정보를 입력하세요.
            """)
        else:
            st.success("✅ 모든 직원의 급여 정보가 설정되었습니다!")
    
    st.divider()
    
    # ========================================================================
    # 급여관리 앱 안내
    # ========================================================================
    
    st.markdown("### 🚀 다음 단계: 급여관리 앱에서 계산")
    
    st.success("""
    **급여 정보 입력 완료!** ✅
    
    이제 **급여관리 앱(포트 8505)**에서 상세 급여를 계산하세요!
    
    ### 급여관리 앱 실행:
    
    ```bash
    cd 5_급여관리_자동화
    ./실행하기.command
    ```
    
    ### 접속:
    ```
    http://localhost:8505
    ```
    
    ### 급여관리 앱에서 할 수 있는 작업:
    - 💰 월별 급여 계산 (4대보험, 소득세 자동 계산)
    - 📄 급여명세서 PDF 생성
    - 📊 급여대장 Excel 다운로드
    - 🎯 초과근무 수당 계산
    - 📅 연차수당 자동 계산
    """)


# ============================================================================
# 페이지 실행
# ============================================================================

show()
