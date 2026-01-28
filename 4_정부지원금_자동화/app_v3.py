"""
회사 맞춤형 정부 지원금 자동화 플랫폼 v3.0
- 데이터베이스 통합
- 직원 관리
- 지원금 검색 및 신청 내역 관리
- 통합 대시보드
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Dict, List

# 기존 모듈
import constants as C
from engine import format_currency

# 신규 모듈
from smart_crawler import SmartSubsidyCrawler
from guide_generator import SmartGuideGenerator

# 통합 데이터베이스 (shared)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database import (
    get_company_profile,
    get_all_employees,
    get_employee_by_id,
    add_employee,
    update_employee
)
from shared.design import apply_design
from shared.utils import show_success

# 로컬 데이터베이스 모듈 (지원금 관련)
from database import (
    Database,
    SubsidyManager,
    ApplicationManager,
    initialize_database
)


# ============================================================
# Streamlit 페이지 설정
# ============================================================

st.set_page_config(
    page_title="회사 맞춤 지원금 자동화 v3.0",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 모던 그린 미니멀 디자인 적용
apply_design()


# ============================================================
# 세션 상태 초기화
# ============================================================

def init_session_state():
    """세션 상태 초기화"""
    # 데이터베이스 초기화
    try:
        with Database() as db:
            db.create_tables()
    except Exception as e:
        st.error(f"데이터베이스 초기화 오류: {e}")
    
    # 회사 프로필 (통합 대시보드에서 가져오기)
    if "company_profile" not in st.session_state:
        st.session_state.company_profile = get_company_profile()
    
    # 선택된 지원금
    if "selected_subsidy" not in st.session_state:
        st.session_state.selected_subsidy = None
    
    # 현재 페이지
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"


# ============================================================
# 메인 화면
# ============================================================

def main():
    """메인 함수"""
    init_session_state()
    
    # 사이드바 - 홈 버튼 추가
    with st.sidebar:
        st.markdown("### 🏠 메뉴")
        if st.button("🏠 통합 대시보드로 이동", use_container_width=True, key="home_btn"):
            st.info("🌐 브라우저에서 http://localhost:8000 로 접속하세요")
        st.divider()
    
    # 사이드바
    show_sidebar()
    
    # 회사 프로필 확인
    if not st.session_state.company_profile:
        # 통합 대시보드로 안내
        st.warning("⚠️ 회사 정보가 등록되어 있지 않습니다.")
        st.info("""
        💡 **회사 정보를 먼저 등록해주세요:**
        
        1. 통합 대시보드로 이동 (http://localhost:8000)
        2. 사이드바 → "🏢 회사 정보 관리" 클릭
        3. 회사 정보 입력 및 저장
        4. 이 페이지로 다시 돌아오기
        """)
        
        if st.button("🏠 통합 대시보드로 이동", type="primary", use_container_width=True):
            st.info("🌐 브라우저에서 http://localhost:8000 로 접속하세요")
        
        st.stop()
        return
    
    # 페이지 라우팅
    if st.session_state.current_page == "dashboard":
        show_dashboard()
    elif st.session_state.current_page == "employees":
        show_employee_management()
    elif st.session_state.current_page == "subsidies":
        show_subsidy_search()
    elif st.session_state.current_page == "applications":
        show_application_management()
    elif st.session_state.current_page == "forms":
        show_auto_form_generator()


# ============================================================
# 회사 프로필 설정
# ============================================================

def show_company_profile_setup():
    """회사 프로필 초기 설정 - 통합 대시보드로 안내"""
    st.title("🏢 회사 정보 등록 필요")
    st.markdown("정부 지원금 자동 매칭을 위해 회사 정보가 필요합니다.")
    
    st.info("""
    💡 **통합 대시보드에서 회사 정보를 관리합니다:**
    
    1. 통합 대시보드로 이동 (http://localhost:8000)
    2. 사이드바 → "🏢 회사 정보 관리" 클릭
    3. 회사 정보 입력 및 저장
    4. 이 페이지를 새로고침하거나 다시 방문
    
    **입력할 정보:**
    - 회사명, 대표자명, 사업자등록번호 (필수)
    - 업종, 업태
    - 직원 수, 연매출
    - 주소, 전화번호
    - 우선지원 대상기업 여부
    - 회사 상황 (청년 채용, 디지털 전환 등)
    """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 통합 대시보드로 이동", type="primary", use_container_width=True):
            st.info("🌐 브라우저에서 http://localhost:8000 로 접속하세요")
    
    with col2:
        if st.button("🔄 페이지 새로고침", use_container_width=True):
            st.rerun()
    
    st.stop()


# ============================================================
# 사이드바
# ============================================================

def show_sidebar():
    """사이드바 표시"""
    with st.sidebar:
        st.markdown("## 🏢 회사 맞춤 지원금 자동화")
        st.markdown("### v3.0 - 통합 시스템")
        
        st.divider()
        
        # 회사 정보 (통합 대시보드에서 가져온 정보)
        if st.session_state.company_profile:
            profile = st.session_state.company_profile
            st.markdown(f"""
            **회사**: {profile.get('company_name', '')}  
            **직원**: {profile.get('employee_count', 0)}명  
            **우선지원**: {"✅ 해당" if profile.get('is_priority_support', False) else "❌ 비해당"}
            """)
            
            if st.button("⚙️ 회사 정보 수정", use_container_width=True):
                st.info("""
                💡 **회사 정보는 통합 대시보드에서 수정:**
                
                1. http://localhost:8000 접속
                2. 🏢 회사 정보 관리
                3. 정보 수정 후 저장
                4. 이 페이지 새로고침 (F5)
                """)
        
        st.divider()
        
        # 메뉴
        st.markdown("### 📋 메뉴")
        
        if st.button("📊 대시보드", use_container_width=True, 
                    type="primary" if st.session_state.current_page == "dashboard" else "secondary"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        if st.button("👥 직원 관리", use_container_width=True,
                    type="primary" if st.session_state.current_page == "employees" else "secondary"):
            st.session_state.current_page = "employees"
            st.rerun()
        
        if st.button("🔍 지원금 검색", use_container_width=True,
                    type="primary" if st.session_state.current_page == "subsidies" else "secondary"):
            st.session_state.current_page = "subsidies"
            st.rerun()
        
        if st.button("📝 신청 내역", use_container_width=True,
                    type="primary" if st.session_state.current_page == "applications" else "secondary"):
            st.session_state.current_page = "applications"
            st.rerun()
        
        if st.button("📄 서식 생성", use_container_width=True,
                    type="primary" if st.session_state.current_page == "forms" else "secondary"):
            st.session_state.current_page = "forms"
            st.rerun()
        
        st.divider()
        
        # 통계
        try:
            with Database() as db:
                stats = ApplicationManager.get_statistics(db)
                
                st.markdown("### 📈 통계")
                st.metric("총 신청 건수", f"{stats['total_applications']}건")
                st.metric("예상 수령액", f"{stats['total_expected']:,}원")
                if stats['total_received'] > 0:
                    st.metric("실제 수령액", f"{stats['total_received']:,}원")
        except Exception as e:
            st.caption(f"통계 로드 오류: {e}")
        
        st.divider()
        st.caption(f"v3.0 | {datetime.now().strftime('%Y-%m-%d')}")


# ============================================================
# 대시보드
# ============================================================

def show_dashboard():
    """통합 대시보드"""
    profile = st.session_state.company_profile
    
    st.title(f"📊 {profile.get('company_name', '회사')} 대시보드")
    
    # 주요 통계
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        with Database() as db:
            # 직원 수 (통합 DB에서 가져오기)
            employees = get_all_employees(active_only=True)
            employee_count = len(employees)
            
            # 지원금 수
            subsidies = SubsidyManager.get_all_subsidies(db)
            subsidy_count = len(subsidies)
            
            # 신청 내역
            applications = ApplicationManager.get_all_applications(db)
            application_count = len(applications)
            
            # 통계
            stats = ApplicationManager.get_statistics(db)
            
            with col1:
                st.metric("📋 등록 직원", f"{employee_count}명")
            
            with col2:
                st.metric("💰 매칭 지원금", f"{subsidy_count}개")
            
            with col3:
                st.metric("📝 신청 건수", f"{application_count}건")
            
            with col4:
                st.metric("💵 예상 수령액", f"{stats['total_expected']:,}원")
        
        st.divider()
        
        # 최근 활동
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👥 최근 등록 직원")
            if employees:
                for emp in employees[:5]:
                    dept = emp.get('department', '')
                    pos = emp.get('position', '')
                    st.write(f"• {emp.get('name', '')} ({dept} {pos})")
            else:
                st.info("등록된 직원이 없습니다. 통합 대시보드의 '직원 관리'에서 추가하세요.")
        
        with col2:
            st.subheader("📝 최근 신청 내역")
            if applications:
                for app in applications[:5]:
                    status_emoji = {
                        "준비중": "⏳",
                        "신청완료": "✅",
                        "승인": "🎉",
                        "거절": "❌"
                    }.get(app['status'], "📋")
                    st.write(f"{status_emoji} {app['employee_name']} - {app['subsidy_name']}")
            else:
                st.info("신청 내역이 없습니다.")
        
        st.divider()
        
        # 빠른 액션
        st.subheader("🚀 빠른 시작")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("➕ 직원 추가", use_container_width=True, type="primary"):
                st.session_state.current_page = "employees"
                st.rerun()
        
        with col2:
            if st.button("🔍 지원금 검색", use_container_width=True, type="primary"):
                st.session_state.current_page = "subsidies"
                st.rerun()
        
        with col3:
            if st.button("📄 서식 생성", use_container_width=True, type="primary"):
                st.session_state.current_page = "forms"
                st.rerun()
    
    except Exception as e:
        st.error(f"❌ 데이터 로드 오류: {e}")


# ============================================================
# 직원 관리
# ============================================================

def show_employee_management():
    """직원 관리"""
    st.title("👥 직원 관리")
    
    tab1, tab2 = st.tabs(["📋 직원 목록", "➕ 직원 추가"])
    
    with tab1:
        show_employee_list()
    
    with tab2:
        show_add_employee()


def show_employee_list():
    """직원 목록"""
    st.subheader("📋 등록된 직원")
    
    try:
        with Database() as db:
            employees = EmployeeManager.get_all_employees(db)
        
        if not employees:
            st.info("등록된 직원이 없습니다. '직원 추가' 탭에서 직원을 추가하세요.")
            return
        
        # 검색
        search_keyword = st.text_input("🔍 검색 (이름, 부서, 직급)", placeholder="검색어 입력")
        
        if search_keyword:
            with Database() as db:
                employees = EmployeeManager.search_employees(db, search_keyword)
        
        # 테이블 생성
        df = pd.DataFrame(employees)
        
        # 선택할 컬럼
        display_columns = ['name', 'department', 'position', 'gender', 'age', 
                          'is_pregnant', 'is_on_leave', 'is_youth']
        
        # 한글 컬럼명
        df_display = df[display_columns].copy()
        df_display.columns = ['이름', '부서', '직급', '성별', '나이', 
                             '임신', '휴직', '청년']
        
        # 불리언 값을 이모지로
        df_display['임신'] = df_display['임신'].apply(lambda x: '✅' if x else '❌')
        df_display['휴직'] = df_display['휴직'].apply(lambda x: '✅' if x else '❌')
        df_display['청년'] = df_display['청년'].apply(lambda x: '✅' if x else '❌')
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        st.markdown(f"**총 {len(employees)}명**")
        
        # 직원 상세/수정/삭제
        st.divider()
        st.subheader("직원 상세 관리")
        
        selected_emp_name = st.selectbox("직원 선택", [emp['name'] for emp in employees])
        
        if selected_emp_name:
            selected_emp = next((e for e in employees if e['name'] == selected_emp_name), None)
            
            if selected_emp:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.json(selected_emp)
                
                with col2:
                    if st.button("❌ 삭제", type="secondary", use_container_width=True):
                        try:
                            with Database() as db:
                                EmployeeManager.delete_employee(db, selected_emp['id'])
                            st.success(f"✅ {selected_emp_name}님이 삭제되었습니다.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"삭제 실패: {e}")
    
    except Exception as e:
        st.error(f"❌ 오류: {e}")


def show_add_employee():
    """직원 추가"""
    st.subheader("➕ 새 직원 등록")
    
    with st.form("add_employee_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("이름 *", placeholder="홍길동")
            resident_number = st.text_input("주민등록번호", placeholder="901231-2******")
            department = st.text_input("부서 *", placeholder="개발팀")
            position = st.text_input("직급", placeholder="대리")
            hire_date = st.date_input("입사일")
        
        with col2:
            gender = st.selectbox("성별", ["선택", "남성", "여성"])
            age = st.number_input("나이", 20, 100, 30)
            is_pregnant = st.checkbox("임신 중")
            is_on_leave = st.checkbox("휴직 중")
            is_youth = st.checkbox("청년 (34세 이하)")
            is_disabled = st.checkbox("장애인")
        
        notes = st.text_area("메모", placeholder="추가 정보 입력")
        
        submitted = st.form_submit_button("✅ 등록", type="primary")
        
        if submitted:
            if not name or not department:
                st.error("이름과 부서는 필수 입력 항목입니다.")
                return
            
            employee_data = {
                "name": name,
                "resident_number": resident_number,
                "department": department,
                "position": position,
                "hire_date": hire_date.isoformat() if hire_date else None,
                "gender": gender if gender != "선택" else None,
                "age": age,
                "is_pregnant": is_pregnant,
                "is_on_leave": is_on_leave,
                "is_youth": is_youth,
                "is_disabled": is_disabled,
                "notes": notes
            }
            
            try:
                with Database() as db:
                    emp_id = EmployeeManager.add_employee(db, employee_data)
                show_success(f"{name}님이 등록되었습니다! (ID: {emp_id})")
            except Exception as e:
                st.error(f"❌ 등록 실패: {e}")


# ============================================================
# 지원금 검색
# ============================================================

def show_subsidy_search():
    """지원금 검색"""
    st.title("🔍 지원금 검색")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("💡 최신 정부 공고를 크롤링하여 우리 회사에 적합한 지원금만 표시합니다.")
    
    with col2:
        if st.button("🔄 최신 공고 크롤링", type="primary", use_container_width=True):
            with st.spinner("정부 사이트에서 최신 공고를 가져오는 중..."):
                try:
                    crawler = SmartSubsidyCrawler(st.session_state.company_profile)
                    subsidies = crawler.crawl_all_sources()
                    
                    # DB에 저장
                    with Database() as db:
                        SubsidyManager.bulk_add_subsidies(db, subsidies)
                    
                    st.success(f"✅ {len(subsidies)}개의 지원금을 찾았습니다!")
                    st.rerun()
                except Exception as e:
                    st.error(f"크롤링 오류: {e}")
    
    st.divider()
    
    # 저장된 지원금 표시
    try:
        with Database() as db:
            subsidies = SubsidyManager.get_all_subsidies(db)
        
        if not subsidies:
            st.info("👆 위의 '최신 공고 크롤링' 버튼을 눌러 지원금을 검색하세요.")
            return
        
        # 필터
        col1, col2 = st.columns(2)
        
        with col1:
            categories = list(set(s.get("category", "기타") for s in subsidies))
            category_filter = st.selectbox("카테고리", ["전체"] + categories)
        
        with col2:
            search_keyword = st.text_input("검색", placeholder="지원금명 또는 설명")
        
        # 필터 적용
        filtered = subsidies
        
        if category_filter != "전체":
            filtered = [s for s in filtered if s.get("category") == category_filter]
        
        if search_keyword:
            filtered = [s for s in filtered if 
                       search_keyword.lower() in s['name'].lower() or 
                       search_keyword.lower() in s.get('description', '').lower()]
        
        st.markdown(f"### 📋 매칭된 지원금 ({len(filtered)}개)")
        
        # 지원금 카드
        for i, subsidy in enumerate(filtered, 1):
            with st.expander(
                f"{i}. 💰 {subsidy['name']} (매칭도: {subsidy['match_score']:.0f}%)",
                expanded=(i <= 3)
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**📄 설명**")
                    st.write(subsidy.get('description', '설명 없음'))
                    
                    st.markdown(f"**✓ 왜 추천?**")
                    for reason in subsidy.get('why_matched', []):
                        st.write(f"• {reason}")
                    
                    st.markdown(f"**📎 필요 서류**")
                    for doc in subsidy.get('required_documents', []):
                        st.write(f"• {doc}")
                
                with col2:
                    st.metric("예상 수령액", f"{subsidy['estimated_amount']:,}원")
                    st.metric("최대 기간", f"{subsidy['max_months']}개월")
                    st.caption(f"**신청 기한**: {subsidy.get('deadline', '상시')}")
                    st.caption(f"**문의**: {subsidy.get('contact', '담당 부서')}")
                    
                    if st.button(
                        "📝 신청하기", 
                        key=f"select_{subsidy['id']}",
                        use_container_width=True,
                        type="primary"
                    ):
                        st.session_state.selected_subsidy = subsidy
                        st.session_state.current_page = "forms"
                        st.rerun()
    
    except Exception as e:
        st.error(f"❌ 오류: {e}")


# ============================================================
# 신청 내역 관리
# ============================================================

def show_application_management():
    """신청 내역 관리"""
    st.title("📝 신청 내역 관리")
    
    tab1, tab2 = st.tabs(["📋 전체 내역", "➕ 신청 등록"])
    
    with tab1:
        show_application_list()
    
    with tab2:
        show_add_application()


def show_application_list():
    """신청 내역 목록"""
    st.subheader("📋 전체 신청 내역")
    
    try:
        with Database() as db:
            applications = ApplicationManager.get_all_applications(db)
            stats = ApplicationManager.get_statistics(db)
        
        # 통계
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("총 신청 건수", f"{stats['total_applications']}건")
        
        with col2:
            st.metric("예상 수령액", f"{stats['total_expected']:,}원")
        
        with col3:
            st.metric("실제 수령액", f"{stats['total_received']:,}원")
        
        st.divider()
        
        if not applications:
            st.info("신청 내역이 없습니다.")
            return
        
        # 상태별 필터
        status_filter = st.selectbox(
            "상태",
            ["전체", "준비중", "신청완료", "승인", "거절"]
        )
        
        if status_filter != "전체":
            filtered_apps = [a for a in applications if a['status'] == status_filter]
        else:
            filtered_apps = applications
        
        # 테이블
        for app in filtered_apps:
            status_emoji = {
                "준비중": "⏳",
                "신청완료": "✅",
                "승인": "🎉",
                "거절": "❌"
            }.get(app['status'], "📋")
            
            with st.expander(f"{status_emoji} {app['employee_name']} - {app['subsidy_name']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**직원**: {app['employee_name']} ({app['department']})")
                    st.write(f"**지원금**: {app['subsidy_name']} ({app['category']})")
                    st.write(f"**신청일**: {app['application_date']}")
                    st.write(f"**상태**: {app['status']}")
                    
                    if app['notes']:
                        st.write(f"**메모**: {app['notes']}")
                
                with col2:
                    st.metric("예상 금액", f"{app['expected_amount']:,}원")
                    
                    if app['actual_amount']:
                        st.metric("실제 수령액", f"{app['actual_amount']:,}원")
                    
                    # 상태 업데이트
                    new_status = st.selectbox(
                        "상태 변경",
                        ["준비중", "신청완료", "승인", "거절"],
                        key=f"status_{app['id']}",
                        index=["준비중", "신청완료", "승인", "거절"].index(app['status'])
                    )
                    
                    if new_status == "승인":
                        actual_amount = st.number_input(
                            "실제 수령액",
                            value=app['actual_amount'] or app['expected_amount'],
                            key=f"amount_{app['id']}"
                        )
                    else:
                        actual_amount = None
                    
                    if st.button("💾 저장", key=f"save_{app['id']}"):
                        try:
                            with Database() as db:
                                ApplicationManager.update_application_status(
                                    db, app['id'], new_status, actual_amount
                                )
                            st.success("✅ 저장되었습니다!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"저장 실패: {e}")
    
    except Exception as e:
        st.error(f"❌ 오류: {e}")


def show_add_application():
    """신청 추가"""
    st.subheader("➕ 새 신청 등록")
    
    try:
        with Database() as db:
            employees = EmployeeManager.get_all_employees(db)
            subsidies = SubsidyManager.get_all_subsidies(db)
        
        if not employees:
            st.warning("등록된 직원이 없습니다. 먼저 '직원 관리'에서 직원을 추가하세요.")
            return
        
        if not subsidies:
            st.warning("검색된 지원금이 없습니다. '지원금 검색'에서 지원금을 검색하세요.")
            return
        
        with st.form("add_application_form"):
            # 직원 선택
            employee_options = {f"{emp['name']} ({emp['department']})": emp['id'] 
                              for emp in employees}
            selected_employee = st.selectbox("직원 선택 *", list(employee_options.keys()))
            
            # 지원금 선택
            subsidy_options = {f"{sub['name']} ({sub['category']})": sub 
                             for sub in subsidies}
            selected_subsidy_name = st.selectbox("지원금 선택 *", list(subsidy_options.keys()))
            
            # 신청일
            application_date = st.date_input("신청일", value=date.today())
            
            # 예상 금액
            selected_subsidy = subsidy_options[selected_subsidy_name]
            expected_amount = st.number_input(
                "예상 수령액",
                value=selected_subsidy['estimated_amount'],
                step=10000
            )
            
            # 메모
            notes = st.text_area("메모", placeholder="추가 정보 입력")
            
            submitted = st.form_submit_button("✅ 등록", type="primary")
            
            if submitted:
                application_data = {
                    "employee_id": employee_options[selected_employee],
                    "subsidy_id": selected_subsidy['id'],
                    "application_date": application_date.isoformat(),
                    "status": "준비중",
                    "expected_amount": expected_amount,
                    "notes": notes
                }
                
                try:
                    with Database() as db:
                        app_id = ApplicationManager.add_application(db, application_data)
                    show_success(f"신청이 등록되었습니다! (ID: {app_id})")
                except Exception as e:
                    st.error(f"❌ 등록 실패: {e}")
    
    except Exception as e:
        st.error(f"❌ 오류: {e}")


# ============================================================
# 서식 자동 생성
# ============================================================

def show_auto_form_generator():
    """자동 서식 생성"""
    st.title("📄 서식 자동 생성")
    
    if st.session_state.selected_subsidy is None:
        st.info("먼저 '지원금 검색' 탭에서 지원금을 선택해주세요.")
        
        # DB에서 지원금 목록 표시
        try:
            with Database() as db:
                subsidies = SubsidyManager.get_all_subsidies(db)
            
            if subsidies:
                st.subheader("📋 저장된 지원금 선택")
                
                for subsidy in subsidies[:10]:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**{subsidy['name']}**")
                        st.caption(f"매칭도: {subsidy['match_score']:.0f}% | {subsidy['category']}")
                    
                    with col2:
                        if st.button("선택", key=f"select_form_{subsidy['id']}"):
                            st.session_state.selected_subsidy = subsidy
                            st.rerun()
        except Exception as e:
            st.error(f"오류: {e}")
        
        return
    
    subsidy = st.session_state.selected_subsidy
    
    st.success(f"✅ 선택된 지원금: **{subsidy['name']}**")
    
    if st.button("◀ 다른 지원금 선택"):
        st.session_state.selected_subsidy = None
        st.rerun()
    
    st.divider()
    
    # 직원 선택
    try:
        with Database() as db:
            employees = EmployeeManager.get_all_employees(db)
            company_db = st.session_state.company_profile.to_dict()
        
        if not employees:
            st.warning("등록된 직원이 없습니다.")
            return
        
        selected_emp_name = st.selectbox(
            "직원 선택",
            [emp['name'] for emp in employees]
        )
        
        selected_emp = next((e for e in employees if e['name'] == selected_emp_name), None)
        
        if not selected_emp:
            return
        
        # 서식 생성 가이드
        st.subheader("📋 필요 서식 및 자동 입력 정보")
        
        # 간단한 서식 정보 표시
        st.markdown("### ✅ 자동 입력된 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**직원 정보**")
            st.write(f"• 이름: {selected_emp['name']}")
            st.write(f"• 부서: {selected_emp['department']}")
            st.write(f"• 직급: {selected_emp['position']}")
        
        with col2:
            st.markdown("**회사 정보**")
            st.write(f"• 회사명: {company_db['company_name']}")
            st.write(f"• 업종: {company_db['business_type']}")
            st.write(f"• 직원 수: {company_db['employee_count']}명")
        
        st.divider()
        
        # 추가 입력 필요 정보
        st.markdown("### 📝 추가 입력 필요")
        
        with st.form("form_additional_info"):
            출산예정일 = st.date_input("출산예정일", value=date.today())
            단축시작일 = st.date_input("근로시간 단축 시작일", value=date.today())
            단축종료일 = st.date_input("근로시간 단축 종료일", value=date.today())
            
            submitted = st.form_submit_button("✅ 서식 생성 및 다운로드", type="primary")
            
            if submitted:
                st.success("✅ 입력 데이터가 준비되었습니다!")
                
                # 데이터 정리
                form_data = {
                    "직원": selected_emp,
                    "회사": company_db,
                    "지원금": subsidy,
                    "추가정보": {
                        "출산예정일": 출산예정일.isoformat(),
                        "단축시작일": 단축시작일.isoformat(),
                        "단축종료일": 단축종료일.isoformat()
                    }
                }
                
                with st.expander("📋 입력된 데이터 확인"):
                    st.json(form_data)
                
                st.info("""
                📝 **서식 생성 방법:**
                
                현재 자동 서식 생성 기능은 기존 앱(app.py)과 통합 중입니다.
                
                입력된 데이터를 기반으로 PDF 서식을 생성하는 기능을 개발 중입니다.
                """)
    
    except Exception as e:
        st.error(f"❌ 오류: {e}")


# ============================================================
# 앱 실행
# ============================================================

if __name__ == "__main__":
    main()
