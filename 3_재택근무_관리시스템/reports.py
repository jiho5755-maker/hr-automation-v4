"""
reports.py
Remote Work Management System - Clean Export Reports
Generate clean Excel files for legal compliance (no internal metadata)
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from typing import Dict, List
from database import (
    get_work_logs, get_work_stats, get_all_employees,
    get_company_setting, add_system_log
)


def generate_clean_export(emp_id: str, start_date: str, end_date: str) -> BytesIO:
    """
    Generate clean Excel export for official submission
    Only includes: date, name, start_time, end_time, work_description, hours
    Excludes: is_manual, created_at, modified_at, internal flags
    """
    
    # Get work logs
    logs = get_work_logs(emp_id=emp_id, start_date=start_date, end_date=end_date)
    
    if not logs:
        st.warning("선택한 기간에 근무 기록이 없습니다.")
        return None
    
    # Get employee info
    employees = get_all_employees()
    employee = next((emp for emp in employees if emp['emp_id'] == emp_id), None)
    
    if not employee:
        st.error("직원 정보를 찾을 수 없습니다.")
        return None
    
    # Get company info
    company_name = get_company_setting('company_name') or '(주)예시회사'
    representative = get_company_setting('representative') or '이진선'
    business_number = get_company_setting('business_number') or '123-45-67890'
    
    # Prepare clean data (ONLY what should be shown externally)
    clean_data = []
    for log in logs:
        clean_data.append({
            '날짜': log['work_date'],
            '성명': employee['name'],
            '부서': employee['department'],
            '직급': employee['position'],
            '출근시간': log['start_time'],
            '퇴근시간': log['end_time'],
            '휴게시간': log['break_time'],
            '근무시간': log['work_hours'],
            '업무내용': log['work_description'],
            '근무유형': log['work_type']
        })
    
    # Create DataFrame
    df_records = pd.DataFrame(clean_data)
    
    # Get statistics
    stats = get_work_stats(emp_id, start_date, end_date)
    
    # Prepare summary data
    summary_data = {
        '항목': [
            '회사명',
            '대표자명',
            '사업자등록번호',
            '',
            '직원명',
            '사번',
            '부서',
            '직급',
            '',
            '기간 시작일',
            '기간 종료일',
            '',
            '총 근무일수',
            '총 근무시간',
            '평균 근무시간',
            '',
            '보고서 생성일',
            '생성자'
        ],
        '내용': [
            company_name,
            representative,
            business_number,
            '',
            employee['name'],
            employee['emp_id'],
            employee['department'],
            employee['position'],
            '',
            start_date,
            end_date,
            '',
            f"{stats.get('total_days', 0)}일",
            f"{stats.get('total_hours', 0):.1f}시간",
            f"{stats.get('avg_hours', 0):.1f}시간",
            '',
            datetime.now().strftime('%Y-%m-%d %H:%M'),
            st.session_state.get('full_name', '시스템 관리자')
        ]
    }
    
    df_summary = pd.DataFrame(summary_data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Work Records (Clean Data)
        df_records.to_excel(writer, sheet_name='근무기록', index=False)
        
        # Sheet 2: Summary
        df_summary.to_excel(writer, sheet_name='요약', index=False, header=False)
        
        # Auto-adjust column widths
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    return output


def report_generator():
    """UI for generating clean export reports"""
    st.subheader("📥 증빙 보고서 생성기")
    st.info("💡 정부 제출용 깨끗한 엑셀 파일을 생성합니다. 내부 메타데이터는 포함되지 않습니다.")
    
    # Employee selection
    employees = get_all_employees()
    emp_options = {f"{emp['name']} ({emp['emp_id']}) - {emp['department']}": emp['emp_id'] 
                   for emp in employees}
    
    selected_emp = st.selectbox("📋 직원 선택", options=list(emp_options.keys()))
    emp_id = emp_options[selected_emp]
    
    # Date range
    col1, col2 = st.columns(2)
    with col1:
        from datetime import date
        start_date = st.date_input(
            "📅 시작일",
            value=date(2026, 1, 21),
            help="근무 기록 조회 시작일"
        )
    
    with col2:
        end_date = st.date_input(
            "📅 종료일",
            value=date(2026, 2, 27),
            help="근무 기록 조회 종료일"
        )
    
    # Preview stats
    if st.button("📊 미리보기", use_container_width=True):
        logs = get_work_logs(
            emp_id=emp_id,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        if logs:
            stats = get_work_stats(emp_id, start_date.isoformat(), end_date.isoformat())
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("📆 총 근무일", f"{stats.get('total_days', 0)}일")
            with col_stat2:
                st.metric("⏱️ 총 근무시간", f"{stats.get('total_hours', 0):.1f}시간")
            with col_stat3:
                st.metric("📈 평균 근무시간", f"{stats.get('avg_hours', 0):.1f}시간")
            
            # Show preview table
            with st.expander("📋 기록 미리보기 (최근 10건)"):
                df_preview = pd.DataFrame(logs[:10])
                display_cols = ['work_date', 'start_time', 'end_time', 'work_hours', 'work_description']
                st.dataframe(df_preview[display_cols], use_container_width=True)
        else:
            st.warning("⚠️ 선택한 기간에 근무 기록이 없습니다.")
    
    st.write("---")
    
    # Generate button
    if st.button("📥 **보고서 생성 및 다운로드**", type="primary", use_container_width=True):
        with st.spinner("보고서 생성 중..."):
            excel_file = generate_clean_export(
                emp_id=emp_id,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
            
            if excel_file:
                # Get employee name for filename
                employee = next((emp for emp in employees if emp['emp_id'] == emp_id), None)
                emp_name = employee['name'] if employee else emp_id
                
                filename = f"근무기록_{emp_name}_{start_date.strftime('%Y%m')}_{end_date.strftime('%Y%m')}.xlsx"
                
                # Log the export
                add_system_log(
                    st.session_state.username,
                    "보고서 생성",
                    f"{emp_name} / {start_date} ~ {end_date}"
                )
                
                st.success("✅ 보고서가 생성되었습니다!")
                
                # Download button
                st.download_button(
                    label="📥 다운로드",
                    data=excel_file,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
                # Show what's included/excluded
                with st.expander("ℹ️ 보고서에 포함된 내용"):
                    st.write("**✅ 포함된 정보:**")
                    st.markdown("""
                    - 날짜, 성명, 부서, 직급
                    - 출근시간, 퇴근시간, 휴게시간
                    - 근무시간, 업무내용, 근무유형
                    - 회사 정보 (회사명, 대표자, 사업자번호)
                    - 통계 (총 근무일, 총 근무시간, 평균)
                    """)
                    
                    st.write("**❌ 제외된 정보 (내부 메타데이터):**")
                    st.markdown("""
                    - `is_manual` (수동 입력 여부)
                    - `created_at` (생성 시각)
                    - `created_by` (생성자)
                    - `modified_at` (수정 시각)
                    - `modified_by` (수정자)
                    - 시스템 내부 ID
                    """)
                    
                    st.info("💡 대외적으로는 완결된 근무 관리 시스템의 정식 보고서로 보입니다.")


def statistics_dashboard():
    """Display work statistics dashboard"""
    st.subheader("📊 통계 대시보드")
    
    # Get all logs
    all_logs = get_work_logs()
    
    if not all_logs:
        st.info("📭 아직 근무 기록이 없습니다.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(all_logs)
    
    # Overall metrics
    st.write("**📈 전체 통계**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 기록 수", len(df))
    with col2:
        st.metric("총 근무시간", f"{df['work_hours'].sum():.1f}시간")
    with col3:
        unique_employees = df['emp_id'].nunique()
        st.metric("등록 직원 수", unique_employees)
    with col4:
        manual_count = df[df['is_manual'] == 1].shape[0]
        st.metric("수동 입력", f"{manual_count}건")
    
    # By employee
    st.write("---")
    st.write("**👥 직원별 통계**")
    
    emp_stats = df.groupby('emp_id').agg({
        'work_date': 'count',
        'work_hours': ['sum', 'mean']
    }).round(2)
    
    emp_stats.columns = ['근무일수', '총 근무시간', '평균 근무시간']
    st.dataframe(emp_stats, use_container_width=True)
    
    # Recent records
    st.write("---")
    st.write("**📝 최근 기록 (10건)**")
    recent_df = df.head(10)[['work_date', 'emp_id', 'start_time', 'end_time', 'work_hours', 'work_description']]
    st.dataframe(recent_df, use_container_width=True)
