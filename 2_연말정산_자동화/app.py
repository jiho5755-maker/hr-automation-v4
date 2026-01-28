"""
연말정산 자동화 - Streamlit 웹 UI
국세청 간소화 PDF 자동 추출
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import tempfile
import os
import sys
from pathlib import Path

# shared 모듈 import
sys.path.append(str(Path(__file__).parent.parent))
from shared.design import apply_design
from shared.utils import show_success

# 로컬 모듈 임포트
from pdf_parser import TaxPDFParser

# ============================================================
# Streamlit 페이지 설정
# ============================================================

st.set_page_config(
    page_title="연말정산 자동화",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 모던 그린 미니멀 디자인 적용
apply_design()

# Custom CSS (추가 스타일)
st.markdown("""
<style>
    /* Main theme - Blue Professional */
    .stApp {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1565C0 0%, #0D47A1 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Headers */
    h1 {
        color: #0D47A1 !important;
        font-weight: 800 !important;
        font-size: 42px !important;
        border-bottom: 4px solid #1976D2 !important;
        padding-bottom: 15px !important;
        margin-bottom: 30px !important;
    }
    
    h2 {
        color: #1565C0 !important;
        font-weight: 700 !important;
        font-size: 32px !important;
        margin-top: 25px !important;
    }
    
    h3 {
        color: #1976D2 !important;
        font-weight: 600 !important;
        font-size: 24px !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 36px !important;
        font-weight: 800 !important;
        color: #0D47A1 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 16px !important;
        color: #1565C0 !important;
        font-weight: 700 !important;
    }
    
    /* Buttons */
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
        background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 8px rgba(25, 118, 210, 0.3) !important;
    }
    
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 16px rgba(25, 118, 210, 0.5) !important;
        background: linear-gradient(135deg, #1E88E5 0%, #1976D2 100%) !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 3px dashed #1976D2 !important;
        border-radius: 15px !important;
        padding: 30px !important;
        background: #E3F2FD !important;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: #C8E6C9 !important;
        color: #1B5E20 !important;
        border-left: 5px solid #4CAF50 !important;
        border-radius: 10px !important;
        padding: 1.2rem !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    /* Info messages */
    .stInfo {
        background-color: #BBDEFB !important;
        color: #01579B !important;
        border-left: 5px solid #2196F3 !important;
        border-radius: 10px !important;
        padding: 1.2rem !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    /* Warning messages */
    .stWarning {
        background-color: #FFF9C4 !important;
        color: #F57F17 !important;
        border-left: 5px solid #FFC107 !important;
        border-radius: 10px !important;
        padding: 1.2rem !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    /* Tables */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 2px solid #90CAF9 !important;
    }
    
    .stDataFrame th {
        background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 12px !important;
    }
    
    .stDataFrame td {
        color: #0D47A1 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 10px !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #E3F2FD !important;
        border-radius: 10px !important;
        color: #0D47A1 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 12px !important;
    }
    
    /* Remove decorations */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Horizontal line */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, #1976D2, transparent) !important;
        margin: 30px 0 !important;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """메인 애플리케이션"""
    
    # 사이드바 - 홈 버튼
    with st.sidebar:
        st.markdown("### 🏠 메뉴")
        if st.button("🏠 통합 대시보드로 이동", use_container_width=True):
            st.info("🌐 브라우저에서 http://localhost:8000 로 접속하세요")
        st.divider()
    
    # 헤더
    st.title("💰 연말정산 자동화 - PDF 파서")
    st.subheader("국세청 간소화 PDF 자동 추출")
    
    st.markdown("""
    ---
    본 시스템은 **국세청 간소화 서비스 PDF**를 자동으로 분석하여 연말정산 항목을 추출합니다.
    
    ✅ **자동 추출 항목**
    - 💊 의료비 (실손의료보험금 자동 차감)
    - 🛡️ 보험료 (건강/고용/국민연금)
    - 💳 신용카드 사용액
    - 🏠 전세자금 대출 원리금
    - 🏦 주택청약저축 납입액
    - 🎁 기부금
    - 📚 교육비
    
    ---
    """)
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs([
        "📤 PDF 업로드",
        "📊 파싱 결과",
        "📥 엑셀 다운로드"
    ])
    
    with tab1:
        show_upload_tab()
    
    with tab2:
        show_results_tab()
    
    with tab3:
        show_download_tab()
    
    # 사이드바
    with st.sidebar:
        st.header("💰 연말정산 자동화")
        st.markdown("""
        **v1.0 Professional**
        
        국세청 간소화 PDF를  
        자동으로 분석합니다.
        """)
        
        st.divider()
        
        st.markdown("### 📋 사용 방법")
        st.markdown("""
        1. PDF 파일 업로드
        2. 자동 파싱 대기
        3. 결과 확인
        4. 엑셀 다운로드
        """)
        
        st.divider()
        
        st.info("💡 **팁**: 국세청 홈택스에서 다운로드한 PDF를 사용하세요.")
        
        st.divider()
        
        st.markdown("""
        <div style='text-align: center; font-size: 11px; color: #E3F2FD; margin-top: 30px;'>
        © 2026 Tax Automation<br>
        <span style='color: #90CAF9;'>🔒 안전한 로컬 처리</span>
        </div>
        """, unsafe_allow_html=True)


def show_upload_tab():
    """PDF 업로드 탭"""
    st.header("📤 PDF 파일 업로드")
    
    st.info("💡 국세청 홈택스에서 다운로드한 '소득·세액공제자료 조회' PDF 파일을 업로드하세요.")
    
    uploaded_file = st.file_uploader(
        "PDF 파일 선택",
        type=['pdf'],
        help="국세청 간소화 서비스 PDF 파일만 지원됩니다."
    )
    
    if uploaded_file is not None:
        # 파일 정보 표시
        col1, col2 = st.columns(2)
        with col1:
            st.metric("파일명", uploaded_file.name)
        with col2:
            file_size = uploaded_file.size / 1024  # KB
            st.metric("파일 크기", f"{file_size:.1f} KB")
        
        st.divider()
        
        # 파싱 버튼
        if st.button("🚀 PDF 파싱 시작", type="primary", use_container_width=True):
            with st.spinner("🔍 PDF를 분석하는 중... 잠시만 기다려주세요"):
                try:
                    # 임시 파일로 저장
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # PDF 파싱
                    parser = TaxPDFParser()
                    parsed_data = parser.parse_pdf(tmp_path)
                    
                    # 임시 파일 삭제
                    os.unlink(tmp_path)
                    
                    # 세션 스테이트에 저장
                    st.session_state.parsed_data = parsed_data
                    st.session_state.parser = parser
                    st.session_state.file_name = uploaded_file.name
                    
                    st.success("✅ PDF 파싱 완료! '📊 파싱 결과' 탭에서 확인하세요.")
                    
                except Exception as e:
                    st.error(f"❌ 파싱 중 오류 발생: {str(e)}")
                    st.warning("PDF 파일이 국세청 간소화 서비스 형식인지 확인해주세요.")
    else:
        st.warning("📁 PDF 파일을 업로드해주세요.")
        
        # 샘플 이미지 또는 설명
        with st.expander("❓ 어디서 PDF를 다운로드하나요?"):
            st.markdown("""
            ### 국세청 홈택스 다운로드 방법
            
            1. **홈택스 접속**: https://www.hometax.go.kr
            2. **로그인**: 공동/금융인증서
            3. **연말정산 간소화**: 메뉴 선택
            4. **소득·세액공제 자료**: 조회
            5. **PDF 저장**: 다운로드 버튼 클릭
            
            💡 매년 1월 15일부터 이용 가능합니다.
            """)


def show_results_tab():
    """파싱 결과 탭"""
    st.header("📊 파싱 결과")
    
    if 'parsed_data' not in st.session_state:
        st.info("📭 아직 파싱된 데이터가 없습니다. '📤 PDF 업로드' 탭에서 파일을 업로드하세요.")
        return
    
    parser = st.session_state.parser
    summary = parser.export_summary()
    
    # 전체 요약
    st.subheader("💵 금액 요약")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💊 의료비 (순)",
            f"{summary['summary']['net_medical']:,}원",
            help="총 의료비에서 실손보험금을 뺀 금액"
        )
        st.caption(f"실손보험: {summary['summary']['insurance_reimbursement']:,}원")
    
    with col2:
        st.metric(
            "🛡️ 보험료",
            f"{summary['summary']['insurance_total']:,}원",
            help="건강/고용/국민연금 합계"
        )
        st.caption(f"{summary['detail']['insurance_count']}건")
    
    with col3:
        st.metric(
            "💳 카드 사용",
            f"{summary['summary']['card_total']:,}원",
            help="신용카드/체크카드 사용액"
        )
    
    with col4:
        total_housing = summary['summary']['jeonse_loan'] + summary['summary']['housing_subscription']
        st.metric(
            "🏠 주택 관련",
            f"{total_housing:,}원",
            help="전세자금 + 주택청약"
        )
    
    st.divider()
    
    # 상세 내역
    st.subheader("📋 상세 내역")
    
    # 의료비
    with st.expander("💊 의료비 상세", expanded=True):
        if st.session_state.parsed_data.medical_expenses:
            st.markdown(f"""
            **의료비 총 지출액**: {summary['summary']['medical_total']:,}원  
            **실손의료보험금**: {summary['summary']['insurance_reimbursement']:,}원  
            **실제 공제 가능액**: {summary['summary']['net_medical']:,}원
            """)
            
            medical_df = pd.DataFrame(st.session_state.parsed_data.medical_expenses)
            if not medical_df.empty:
                medical_df.columns = ['의료기관', '지출액', '실손보험금']
                medical_df['지출액'] = medical_df['지출액'].apply(lambda x: f"{x:,}원")
                medical_df['실손보험금'] = medical_df['실손보험금'].apply(lambda x: f"{x:,}원")
                st.dataframe(medical_df, use_container_width=True, hide_index=True)
        else:
            st.info("의료비 내역이 없습니다.")
    
    # 보험료
    with st.expander("🛡️ 보험료 상세"):
        if st.session_state.parsed_data.insurance:
            insurance_df = pd.DataFrame(st.session_state.parsed_data.insurance)
            insurance_df.columns = ['보험 종류', '납입액']
            insurance_df['납입액'] = insurance_df['납입액'].apply(lambda x: f"{x:,}원")
            st.dataframe(insurance_df, use_container_width=True, hide_index=True)
            
            st.success(f"✅ 총 보험료: {summary['summary']['insurance_total']:,}원")
        else:
            st.info("보험료 내역이 없습니다.")
    
    # 주택 관련
    with st.expander("🏠 주택 관련 상세"):
        col_h1, col_h2 = st.columns(2)
        
        with col_h1:
            st.markdown("#### 전세자금 대출")
            if summary['summary']['jeonse_loan'] > 0:
                st.success(f"✅ 원리금 상환액: {summary['summary']['jeonse_loan']:,}원")
            else:
                st.info("전세자금 대출 내역이 없습니다.")
        
        with col_h2:
            st.markdown("#### 주택청약저축")
            if summary['summary']['housing_subscription'] > 0:
                st.success(f"✅ 납입액: {summary['summary']['housing_subscription']:,}원")
            else:
                st.info("주택청약저축 내역이 없습니다.")
    
    # 기타
    if st.session_state.parsed_data.donations:
        with st.expander("🎁 기부금 상세"):
            donation_df = pd.DataFrame(st.session_state.parsed_data.donations)
            st.dataframe(donation_df, use_container_width=True, hide_index=True)
    
    if st.session_state.parsed_data.education:
        with st.expander("📚 교육비 상세"):
            education_df = pd.DataFrame(st.session_state.parsed_data.education)
            st.dataframe(education_df, use_container_width=True, hide_index=True)


def show_download_tab():
    """엑셀 다운로드 탭"""
    st.header("📥 엑셀 다운로드")
    
    if 'parsed_data' not in st.session_state:
        st.info("📭 아직 파싱된 데이터가 없습니다. '📤 PDF 업로드' 탭에서 파일을 업로드하세요.")
        return
    
    st.info("💡 파싱 결과를 엑셀 파일로 다운로드합니다. 회계 처리나 기록용으로 사용하세요.")
    
    parser = st.session_state.parser
    summary = parser.export_summary()
    
    # 엑셀 생성
    excel_buffer = BytesIO()
    
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        # Sheet 1: 요약
        summary_data = pd.DataFrame([
            {"항목": "의료비 총 지출액", "금액": f"{summary['summary']['medical_total']:,}원"},
            {"항목": "실손의료보험금", "금액": f"{summary['summary']['insurance_reimbursement']:,}원"},
            {"항목": "의료비 순 공제액", "금액": f"{summary['summary']['net_medical']:,}원"},
            {"항목": "", "금액": ""},
            {"항목": "보험료 총액", "금액": f"{summary['summary']['insurance_total']:,}원"},
            {"항목": "", "금액": ""},
            {"항목": "신용카드 사용액", "금액": f"{summary['summary']['card_total']:,}원"},
            {"항목": "", "금액": ""},
            {"항목": "전세자금 대출", "금액": f"{summary['summary']['jeonse_loan']:,}원"},
            {"항목": "주택청약저축", "금액": f"{summary['summary']['housing_subscription']:,}원"},
            {"항목": "", "금액": ""},
            {"항목": "기부금 총액", "금액": f"{summary['summary']['donation_total']:,}원"},
            {"항목": "교육비 총액", "금액": f"{summary['summary']['education_total']:,}원"},
        ])
        summary_data.to_excel(writer, sheet_name='요약', index=False)
        
        # Sheet 2: 의료비
        if st.session_state.parsed_data.medical_expenses:
            medical_df = pd.DataFrame(st.session_state.parsed_data.medical_expenses)
            medical_df.columns = ['의료기관', '지출액', '실손보험금']
            medical_df.to_excel(writer, sheet_name='의료비', index=False)
        
        # Sheet 3: 보험료
        if st.session_state.parsed_data.insurance:
            insurance_df = pd.DataFrame(st.session_state.parsed_data.insurance)
            insurance_df.columns = ['보험종류', '납입액']
            insurance_df.to_excel(writer, sheet_name='보험료', index=False)
        
        # Sheet 4: 기부금
        if st.session_state.parsed_data.donations:
            donation_df = pd.DataFrame(st.session_state.parsed_data.donations)
            donation_df.to_excel(writer, sheet_name='기부금', index=False)
        
        # Sheet 5: 교육비
        if st.session_state.parsed_data.education:
            education_df = pd.DataFrame(st.session_state.parsed_data.education)
            education_df.to_excel(writer, sheet_name='교육비', index=False)
    
    excel_data = excel_buffer.getvalue()
    
    # 통계
    st.subheader("📊 생성 정보")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("원본 파일", st.session_state.file_name)
    with col2:
        sheet_count = 1  # 요약
        if st.session_state.parsed_data.medical_expenses:
            sheet_count += 1
        if st.session_state.parsed_data.insurance:
            sheet_count += 1
        if st.session_state.parsed_data.donations:
            sheet_count += 1
        if st.session_state.parsed_data.education:
            sheet_count += 1
        st.metric("시트 수", f"{sheet_count}개")
    with col3:
        st.metric("생성 시각", datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    st.divider()
    
    # 다운로드 버튼
    file_name_base = st.session_state.file_name.replace('.pdf', '')
    download_filename = f"연말정산_{file_name_base}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    st.download_button(
        label="📥 엑셀 다운로드",
        data=excel_data,
        file_name=download_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        type="primary"
    )
    
    st.success("✅ 다운로드 버튼을 클릭하여 엑셀 파일을 저장하세요!")
    
    # 포함 내용 안내
    with st.expander("📋 엑셀 파일 포함 내용"):
        st.markdown("""
        **시트 구성**:
        1. **요약**: 전체 항목별 금액 요약
        2. **의료비**: 의료기관별 지출 내역
        3. **보험료**: 보험 종류별 납입액
        4. **기부금**: 기부처별 기부 내역 (있는 경우)
        5. **교육비**: 교육기관별 교육비 (있는 경우)
        
        💡 각 시트는 회계 처리나 증빙 자료로 활용할 수 있습니다.
        """)


if __name__ == "__main__":
    main()
