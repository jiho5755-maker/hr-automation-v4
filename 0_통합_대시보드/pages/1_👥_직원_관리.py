"""
통합 직원 관리 페이지
Employee Management Page

모든 직원 정보를 한 곳에서 통합 관리
이곳에서 입력한 정보가 모든 모듈에 자동으로 반영됩니다!
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import date

# 상위 디렉토리의 shared 모듈 import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.database import (
    get_db, 
    get_all_employees, 
    get_employee_by_id,
    get_employee_by_name,
    add_employee, 
    update_employee, 
    delete_employee,
    get_departments,
    add_system_log
)
from shared.utils import show_success, show_error, show_info, show_warning
from shared.design import apply_design

# 디자인 적용
apply_design()


# ============================================================================
# 세션 상태 초기화
# ============================================================================

def init_employee_state():
    """직원 관리 페이지 세션 상태 초기화 - PRD §8.2 SL-8"""
    if 'show_employee_form' not in st.session_state:
        st.session_state.show_employee_form = False
    if 'form_mode' not in st.session_state:
        st.session_state.form_mode = 'add'  # 'add' or 'edit'
    if 'editing_employee' not in st.session_state:
        st.session_state.editing_employee = None


# ============================================================================
# 직원 목록 표시 - PRD §5.2.1
# ============================================================================

def show_employee_list():
    """직원 목록 테이블 표시"""
    
    st.markdown("### 👥 직원 목록")
    
    # 검색 및 필터
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_name = st.text_input("🔍 이름 검색", placeholder="직원 이름 입력", label_visibility="collapsed")
    
    with col2:
        departments = get_departments()
        dept_filter = st.selectbox("부서 필터", ["전체"] + departments, label_visibility="collapsed")
    
    with col3:
        status_filter = st.selectbox("상태 필터", ["재직", "전체", "퇴사"], label_visibility="collapsed")
    
    # 직원 목록 조회
    employees = get_all_employees(active_only=(status_filter == "재직"))
    
    # 필터 적용
    if search_name:
        employees = [emp for emp in employees if search_name.lower() in emp['name'].lower()]
    
    if dept_filter != "전체":
        employees = [emp for emp in employees if emp.get('department') == dept_filter]
    
    # 테이블 표시
    if employees:
        st.info(f"총 **{len(employees)}명**의 직원이 검색되었습니다.")
        
        # 테이블 헤더 및 데이터
        for emp in employees:
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1, 1, 1, 1.5])
                
                with col1:
                    st.write(f"**{emp['name']}**")
                    if emp.get('is_pregnant'):
                        st.caption("🤰 임신")
                    if emp.get('is_on_leave'):
                        st.caption("🏖️ 휴직")
                
                with col2:
                    st.write(emp.get('department', 'N/A'))
                
                with col3:
                    st.write(emp.get('position', 'N/A'))
                
                with col4:
                    st.write(emp.get('hire_date', 'N/A'))
                
                with col5:
                    status = "✅ 재직" if emp.get('is_active') else "⏸️ 퇴사"
                    st.write(status)
                
                with col6:
                    col_edit, col_delete = st.columns(2)
                    
                    with col_edit:
                        if st.button("✏️ 수정", key=f"edit_{emp['emp_id']}", use_container_width=True):
                            st.session_state.show_employee_form = True
                            st.session_state.form_mode = 'edit'
                            st.session_state.editing_employee = emp
                            st.rerun()
                    
                    with col_delete:
                        if st.button("🗑️ 삭제", key=f"delete_{emp['emp_id']}", use_container_width=True):
                            if st.session_state.get(f"confirm_delete_{emp['emp_id']}", False):
                                handle_delete_employee(emp['emp_id'], emp['name'])
                            else:
                                st.session_state[f"confirm_delete_{emp['emp_id']}"] = True
                                show_warning(f"{emp['name']} 삭제를 확인하려면 다시 클릭하세요.")
                                st.rerun()
                
                st.divider()
    else:
        st.info("등록된 직원이 없습니다.")


# ============================================================================
# 직원 정보 입력 폼 - PRD §5.2.3, §5.2.4
# ============================================================================

def show_employee_form():
    """직원 정보 입력/수정 폼 표시"""
    
    mode = st.session_state.form_mode
    editing_emp = st.session_state.editing_employee if mode == 'edit' else None
    
    st.markdown(f"### {'✏️ 직원 정보 수정' if mode == 'edit' else '➕ 새 직원 추가'}")
    
    with st.form("employee_form", clear_on_submit=False):
        # ====================================================================
        # 필수 정보 - PRD §5.2.3
        # ====================================================================
        
        st.markdown("#### 📋 필수 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "이름 *", 
                value=editing_emp.get('name', '') if editing_emp else '',
                placeholder="홍길동"
            )
            
            department = st.text_input(
                "부서 *", 
                value=editing_emp.get('department', '') if editing_emp else '',
                placeholder="개발팀"
            )
        
        with col2:
            position = st.text_input(
                "직급 *", 
                value=editing_emp.get('position', '') if editing_emp else '',
                placeholder="사원"
            )
            
            hire_date_val = editing_emp.get('hire_date') if editing_emp else None
            if hire_date_val and isinstance(hire_date_val, str):
                try:
                    from datetime import datetime
                    hire_date_val = datetime.strptime(hire_date_val, '%Y-%m-%d').date()
                except:
                    hire_date_val = date.today()
            
            hire_date = st.date_input(
                "입사일 *", 
                value=hire_date_val or date.today()
            )
        
        st.divider()
        
        # ====================================================================
        # 선택 정보 - PRD §5.2.4
        # ====================================================================
        
        st.markdown("#### 📝 선택 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            resident_number = st.text_input(
                "주민등록번호", 
                value=editing_emp.get('resident_number', '') if editing_emp else '',
                placeholder="123456-1234567",
                help="개인정보 보호를 위해 암호화 저장 권장"
            )
            
            gender = st.selectbox(
                "성별", 
                ["선택 안 함", "남성", "여성"],
                index=["선택 안 함", "남성", "여성"].index(editing_emp.get('gender', '선택 안 함')) if editing_emp and editing_emp.get('gender') else 0
            )
            
            age = st.number_input(
                "나이", 
                min_value=0, 
                max_value=100, 
                value=int(editing_emp.get('age', 0)) if editing_emp and editing_emp.get('age') else 0,
                step=1
            )
        
        with col2:
            email = st.text_input(
                "이메일", 
                value=editing_emp.get('email', '') if editing_emp else '',
                placeholder="example@company.com"
            )
            
            phone = st.text_input(
                "전화번호", 
                value=editing_emp.get('phone', '') if editing_emp else '',
                placeholder="010-1234-5678"
            )
        
        st.divider()
        
        # ====================================================================
        # 특수 상태 - PRD §5.2.4
        # ====================================================================
        
        st.markdown("#### 🏷️ 특수 상태")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            is_pregnant = st.checkbox(
                "🤰 임신 중", 
                value=bool(editing_emp.get('is_pregnant', False)) if editing_emp else False
            )
        
        with col2:
            is_on_leave = st.checkbox(
                "🏖️ 휴직 중", 
                value=bool(editing_emp.get('is_on_leave', False)) if editing_emp else False
            )
        
        with col3:
            is_youth = st.checkbox(
                "🎓 청년", 
                value=bool(editing_emp.get('is_youth', False)) if editing_emp else False
            )
        
        with col4:
            is_disabled = st.checkbox(
                "♿ 장애인", 
                value=bool(editing_emp.get('is_disabled', False)) if editing_emp else False
            )
        
        st.divider()
        
        # ====================================================================
        # 기타 정보
        # ====================================================================
        
        notes = st.text_area(
            "메모", 
            value=editing_emp.get('notes', '') if editing_emp else '',
            placeholder="추가 메모 사항",
            height=100
        )
        
        # ====================================================================
        # 버튼
        # ====================================================================
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            submit = st.form_submit_button(
                "💾 저장" if mode == 'add' else "💾 수정 저장", 
                type="primary", 
                use_container_width=True
            )
        
        with col2:
            cancel = st.form_submit_button(
                "❌ 취소", 
                use_container_width=True
            )
        
        # ====================================================================
        # 폼 처리 - IC-1: 직원 정보 저장 플로우
        # ====================================================================
        
        if cancel:
            st.session_state.show_employee_form = False
            st.session_state.editing_employee = None
            st.rerun()
        
        if submit:
            # Step 1: 필수 필드 검증
            if not all([name, department, position]):
                show_error("필수 정보(이름, 부서, 직급)를 모두 입력하세요.")
                return
            
            # 직원 데이터 구성
            employee_data = {
                'name': name,
                'department': department,
                'position': position,
                'hire_date': hire_date.strftime('%Y-%m-%d'),
                'resident_number': resident_number if resident_number else None,
                'gender': gender if gender != "선택 안 함" else None,
                'age': age if age > 0 else None,
                'email': email if email else None,
                'phone': phone if phone else None,
                'is_pregnant': is_pregnant,
                'is_on_leave': is_on_leave,
                'is_youth': is_youth,
                'is_disabled': is_disabled,
                'notes': notes if notes else None,
                'created_by': st.session_state.user.get('username') if st.session_state.user else 'system'
            }
            
            try:
                if mode == 'add':
                    # Step 2: 직원 추가
                    emp_id = add_employee(employee_data)
                    
                    if emp_id:
                        # Step 3: 시스템 로그 기록
                        add_system_log(
                            st.session_state.user.get('username'), 
                            "직원 추가", 
                            "employee_management",
                            f"직원 {name} 추가"
                        )
                        
                        # Step 4: session_state.current_employee 업데이트
                        st.session_state.current_employee = get_employee_by_id(emp_id)
                        
                        # Step 5: 폼 닫기
                        st.session_state.show_employee_form = False
                        
                        # Step 6: 성공 토스트
                        show_success(f"✅ {name}님이 등록되었습니다!")
                        st.rerun()
                    else:
                        show_error("직원 등록에 실패했습니다.")
                
                elif mode == 'edit' and editing_emp:
                    # Step 2: 직원 수정
                    success = update_employee(editing_emp['emp_id'], employee_data)
                    
                    if success:
                        # Step 3: 시스템 로그 기록
                        add_system_log(
                            st.session_state.user.get('username'), 
                            "직원 정보 수정", 
                            "employee_management",
                            f"직원 {name} 정보 수정"
                        )
                        
                        # Step 4: session_state.current_employee 업데이트
                        updated_emp = get_employee_by_id(editing_emp['emp_id'])
                        if st.session_state.current_employee and st.session_state.current_employee.get('emp_id') == editing_emp['emp_id']:
                            st.session_state.current_employee = updated_emp
                        
                        # Step 5: 폼 닫기
                        st.session_state.show_employee_form = False
                        st.session_state.editing_employee = None
                        
                        # Step 6: 성공 토스트
                        show_success(f"✅ {name}님의 정보가 수정되었습니다!")
                        st.rerun()
                    else:
                        show_error("직원 정보 수정에 실패했습니다.")
            
            except Exception as e:
                show_error(f"오류 발생: {str(e)}")


# ============================================================================
# 직원 삭제 처리 - PRD §5.2.7
# ============================================================================

def handle_delete_employee(emp_id, emp_name):
    """직원 삭제 (소프트 삭제)"""
    try:
        # 소프트 삭제 (is_active = 0)
        success = delete_employee(emp_id, hard_delete=False)
        
        if success:
            # 시스템 로그 기록
            add_system_log(
                st.session_state.user.get('username'), 
                "직원 삭제", 
                "employee_management",
                f"직원 {emp_name} 삭제 (소프트)"
            )
            
            # 현재 선택된 직원이 삭제된 경우 초기화
            if st.session_state.current_employee and st.session_state.current_employee.get('emp_id') == emp_id:
                st.session_state.current_employee = None
            
            # 확인 플래그 제거
            if f"confirm_delete_{emp_id}" in st.session_state:
                del st.session_state[f"confirm_delete_{emp_id}"]
            
            show_success(f"✅ {emp_name}님이 삭제되었습니다.")
            st.rerun()
        else:
            show_error("직원 삭제에 실패했습니다.")
    
    except Exception as e:
        show_error(f"오류 발생: {str(e)}")


# ============================================================================
# 메인 함수
# ============================================================================

def show():
    """통합 직원 관리 페이지 메인 함수"""
    
    # 세션 상태 초기화
    init_employee_state()
    
    # 타이틀
    st.markdown('<div class="main-title">👥 통합 직원 관리</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">모든 직원 정보를 한 곳에서 통합 관리</div>', unsafe_allow_html=True)
    
    # 안내 메시지
    st.info("""
    **🔄 데이터 자동 동기화**
    
    이곳에서 입력/수정한 직원 정보는 **모든 모듈(출산육아, 재택근무, 급여관리)**에 자동으로 반영됩니다!
    
    더 이상 각 모듈마다 직원 정보를 따로 입력할 필요가 없습니다. ✨
    """)
    
    # 새 직원 추가 버튼 - PRD §5.2.2
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("➕ 새 직원 추가", type="primary", use_container_width=True):
            st.session_state.show_employee_form = True
            st.session_state.form_mode = 'add'
            st.session_state.editing_employee = None
            st.rerun()
    
    st.divider()
    
    # 폼 표시 또는 목록 표시
    if st.session_state.show_employee_form:
        show_employee_form()
        
        st.divider()
        
        if st.button("⬅️ 목록으로 돌아가기", use_container_width=True):
            st.session_state.show_employee_form = False
            st.session_state.editing_employee = None
            st.rerun()
    else:
        show_employee_list()


# ============================================================================
# 페이지 실행
# ============================================================================

show()
