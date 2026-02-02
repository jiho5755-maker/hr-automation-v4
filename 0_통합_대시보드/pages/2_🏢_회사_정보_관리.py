"""
회사 정보 통합 관리 페이지
모든 앱에서 사용하는 회사 정보를 한 곳에서 관리
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json

# shared 모듈 import
sys.path.append(str(Path(__file__).parent.parent.parent))
from shared.database import (
    get_company_profile,
    update_company_profile
)
from shared.design import apply_design
from shared.utils import show_success
# 인증 함수는 session_state로 체크

# 페이지 설정
st.set_page_config(
    page_title="회사 정보 관리",
    page_icon="🏢",
    layout="wide"
)

# 인증 체크
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⛔ 로그인이 필요합니다.")
    st.info("메인 페이지에서 로그인해주세요.")
    st.stop()

# 모던 그린 미니멀 디자인 적용
apply_design()

st.markdown("""
<style>
    .info-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background: #f0f2f6;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 메인 타이틀
st.title("🏢 회사 정보 통합 관리")
st.markdown("모든 앱에서 사용하는 회사 정보를 한 곳에서 관리합니다.")

# 현재 회사 정보 조회
company = get_company_profile()

# 탭 구성
tab1, tab2 = st.tabs(["📝 회사 정보 수정", "📊 정보 확인"])

# ==================== 회사 정보 수정 탭 ====================
with tab1:
    st.subheader("📝 회사 기본 정보")
    
    with st.form("company_info_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 기본 정보")
            company_name = st.text_input(
                "회사명 *",
                value=company.get('company_name', '') if company else '',
                placeholder="(주)예시회사"
            )
            
            ceo_name = st.text_input(
                "대표자명 *",
                value=company.get('ceo_name', '') if company else '',
                placeholder="홍길동"
            )
            
            business_number = st.text_input(
                "사업자등록번호 *",
                value=company.get('business_number', '') if company else '',
                placeholder="123-45-67890",
                help="숫자와 하이픈(-) 형식"
            )
            
            business_type = st.text_input(
                "업종",
                value=company.get('business_type', '') if company else '',
                placeholder="제조업, 서비스업 등"
            )
            
            industry = st.text_input(
                "업태",
                value=company.get('industry', '') if company else '',
                placeholder="도소매업, IT서비스 등"
            )
        
        with col2:
            st.markdown("### 규모 및 위치")
            employee_count = st.number_input(
                "직원 수",
                min_value=0,
                value=int(company.get('employee_count', 0)) if company else 0,
                step=1
            )
            
            annual_revenue = st.number_input(
                "연매출 (원)",
                min_value=0,
                value=int(company.get('annual_revenue', 0)) if company else 0,
                step=1000000,
                help="단위: 원"
            )
            
            location = st.text_area(
                "주소",
                value=company.get('location', '') if company else '',
                placeholder="서울특별시 강남구 테헤란로 123",
                height=100
            )
            
            phone = st.text_input(
                "대표 전화번호",
                value=company.get('phone', '') if company else '',
                placeholder="02-1234-5678"
            )
        
        st.markdown("### 추가 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            establishment_date = st.date_input(
                "설립일",
                value=datetime.strptime(company.get('establishment_date', str(datetime.now().date())), '%Y-%m-%d').date() if company and company.get('establishment_date') else datetime.now().date(),
                min_value=datetime(1900, 1, 1).date(),
                max_value=datetime.now().date(),
                help="회사 설립일을 선택하세요 (1900년부터 선택 가능)"
            )
        
        with col2:
            is_priority_support = st.checkbox(
                "우선지원 대상기업",
                value=company.get('is_priority_support', False) if company else False,
                help="중소기업 우선지원 대상 여부"
            )
        
        # 상황 정보 (정부지원금용)
        st.markdown("### 회사 상황 (정부지원금 매칭용)")
        
        situations = company.get('situations', []) if company else []
        if isinstance(situations, str):
            try:
                situations = json.loads(situations)
            except:
                situations = []
        
        situation_options = [
            "청년 채용 계획",
            "여성 채용 계획",
            "장애인 채용 계획",
            "지역 인재 채용",
            "신규 사업 확장",
            "디지털 전환 추진",
            "수출 확대",
            "R&D 투자",
            "기술 혁신",
            "고용 유지 어려움"
        ]
        
        selected_situations = st.multiselect(
            "해당하는 상황을 모두 선택하세요",
            situation_options,
            default=[s for s in situations if s in situation_options]
        )
        
        notes = st.text_area(
            "비고",
            value=company.get('notes', '') if company else '',
            placeholder="추가 정보나 특이사항을 입력하세요",
            height=100
        )
        
        st.divider()
        
        submit = st.form_submit_button("💾 저장", type="primary", use_container_width=True)
        
        if submit:
            if not company_name or not ceo_name or not business_number:
                st.error("❌ 회사명, 대표자명, 사업자등록번호는 필수입니다!")
            else:
                try:
                    company_data = {
                        'company_name': company_name,
                        'ceo_name': ceo_name,
                        'business_number': business_number,
                        'business_type': business_type,
                        'industry': industry,
                        'employee_count': employee_count,
                        'annual_revenue': annual_revenue,
                        'location': location,
                        'phone': phone,
                        'establishment_date': str(establishment_date),
                        'is_priority_support': is_priority_support,
                        'situations': json.dumps(selected_situations, ensure_ascii=False),
                        'notes': notes
                    }
                    
                    update_company_profile(company_data)
                    show_success("회사 정보가 업데이트되었습니다!")
                    st.info("💡 모든 앱에 자동으로 반영됩니다!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 오류: {e}")
                    import traceback
                    st.code(traceback.format_exc())

# ==================== 정보 확인 탭 ====================
with tab2:
    st.subheader("📊 현재 회사 정보")
    
    if company:
        # 기본 정보
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏢 기본 정보")
            st.markdown(f"""
            - **회사명**: {company.get('company_name', '-')}
            - **대표자**: {company.get('ceo_name', '-')}
            - **사업자번호**: {company.get('business_number', '-')}
            - **업종**: {company.get('business_type', '-')}
            - **업태**: {company.get('industry', '-')}
            """)
        
        with col2:
            st.markdown("### 📊 규모 정보")
            st.markdown(f"""
            - **직원 수**: {company.get('employee_count', 0)}명
            - **연매출**: {company.get('annual_revenue', 0):,}원
            - **설립일**: {company.get('establishment_date', '-')}
            - **우선지원**: {'✅ 예' if company.get('is_priority_support') else '❌ 아니오'}
            """)
        
        st.divider()
        
        # 연락처 정보
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📞 연락처")
            st.markdown(f"""
            - **전화번호**: {company.get('phone', '-')}
            - **주소**: {company.get('location', '-')}
            """)
        
        with col2:
            st.markdown("### 🎯 회사 상황")
            situations = company.get('situations', [])
            if isinstance(situations, str):
                try:
                    situations = json.loads(situations)
                except:
                    situations = []
            
            if situations:
                for situation in situations:
                    st.markdown(f"- {situation}")
            else:
                st.markdown("- (없음)")
        
        # 메모
        if company.get('notes'):
            st.divider()
            st.markdown("### 📝 비고")
            st.info(company.get('notes'))
        
        # 메타 정보
        st.divider()
        st.markdown("### ⏱️ 시스템 정보")
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"생성일: {company.get('created_at', '-')}")
        with col2:
            st.caption(f"수정일: {company.get('updated_at', '-')}")
        
    else:
        st.warning("⚠️ 등록된 회사 정보가 없습니다.")
        st.info("👈 왼쪽 탭에서 회사 정보를 입력해주세요.")

# 하단 안내
st.divider()
st.success("""
💡 **연동 정보**

이곳에서 수정한 회사 정보는 다음 앱들에 **자동으로 반영**됩니다:

✅ **출산육아 자동화** - 사업주 정보로 사용  
✅ **재택근무 관리** - 회사 설정으로 사용  
✅ **정부지원금 자동화** - 회사 프로필로 사용  
✅ **연말정산 자동화** - 회사 정보로 사용  

한 번만 입력하면 모든 곳에서 사용됩니다! 🎉
""")

# 사용 중인 앱 목록 표시
st.info("""
🔗 **현재 이 정보를 사용하는 앱:**
- 통합 대시보드 (이 페이지)
- 1_출산육아_자동화
- 2_연말정산_자동화
- 3_재택근무_관리시스템
- 4_정부지원금_자동화
""")
