"""
연말정산 자동화 - 일괄 처리 페이지
여러 직원의 PDF를 한 번에 처리하고 엑셀로 다운로드
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from io import BytesIO
from datetime import datetime

# 상위 디렉토리 모듈 import
sys.path.append(str(Path(__file__).parent.parent))

try:
    from pdf_parser import YearEndTaxPDFParser
    from excel_mapper import YearEndTaxExcelMapper
    from housing_parser import HousingDeductionParser
except ImportError as e:
    st.error(f"모듈 import 실패: {e}")
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title="연말정산 일괄 처리",
    page_icon="📦",
    layout="wide"
)

st.title("📦 연말정산 일괄 처리")
st.markdown("여러 직원의 PDF를 한 번에 업로드하고 엑셀로 통합 다운로드합니다.")

st.divider()

# ============================================================
# 파일 업로드
# ============================================================

st.subheader("📤 PDF 파일 업로드")

uploaded_files = st.file_uploader(
    "연말정산 PDF 파일 선택 (여러 개 가능)",
    type=['pdf'],
    accept_multiple_files=True,
    help="Ctrl(Cmd) + 클릭으로 여러 파일 선택 가능"
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)}개 파일 업로드 완료")
    
    # 파일 목록 표시
    with st.expander("📋 업로드된 파일 목록"):
        for i, file in enumerate(uploaded_files, 1):
            st.write(f"{i}. {file.name} ({file.size:,} bytes)")
    
    st.divider()
    
    # ============================================================
    # 처리 옵션
    # ============================================================
    
    st.subheader("⚙️ 처리 옵션")
    
    col1, col2 = st.columns(2)
    
    with col1:
        parse_housing = st.checkbox(
            "🏠 주택자금공제 파싱",
            value=True,
            help="주택청약, 주택담보대출 공제 항목 추출"
        )
    
    with col2:
        merge_excel = st.checkbox(
            "📊 단일 엑셀로 통합",
            value=True,
            help="모든 결과를 하나의 엑셀 파일로 통합"
        )
    
    st.divider()
    
    # ============================================================
    # 처리 시작
    # ============================================================
    
    if st.button("🚀 일괄 처리 시작", type="primary", use_container_width=True):
        
        # 진행률 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 결과 저장
        all_results = []
        errors = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                status_text.text(f"처리 중: {uploaded_file.name} ({i+1}/{len(uploaded_files)})")
                
                # PDF 파싱
                parser = YearEndTaxPDFParser(uploaded_file)
                data = parser.parse()
                
                if data:
                    # 주택자금공제 파싱 (선택 시)
                    if parse_housing:
                        housing_parser = HousingDeductionParser(uploaded_file)
                        housing_data = housing_parser.parse()
                        if housing_data:
                            data.update(housing_data)
                    
                    # 파일명에서 이름 추출 (예: 홍길동_연말정산.pdf -> 홍길동)
                    employee_name = uploaded_file.name.split('_')[0] if '_' in uploaded_file.name else uploaded_file.name.replace('.pdf', '')
                    data['파일명'] = uploaded_file.name
                    data['직원명'] = employee_name
                    
                    all_results.append(data)
                else:
                    errors.append(f"{uploaded_file.name}: 데이터 추출 실패")
                
            except Exception as e:
                errors.append(f"{uploaded_file.name}: {str(e)}")
            
            # 진행률 업데이트
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.text("처리 완료!")
        
        st.divider()
        
        # ============================================================
        # 결과 표시
        # ============================================================
        
        if all_results:
            st.success(f"✅ {len(all_results)}개 파일 처리 완료!")
            
            # DataFrame 생성
            df = pd.DataFrame(all_results)
            
            # 주요 정보만 표시
            display_columns = ['직원명', '파일명', '총급여', '근로소득공제', '과세표준', '결정세액']
            available_columns = [col for col in display_columns if col in df.columns]
            
            st.dataframe(
                df[available_columns] if available_columns else df,
                use_container_width=True,
                hide_index=True
            )
            
            # 통계
            st.divider()
            st.subheader("📊 통계")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if '총급여' in df.columns:
                    st.metric("평균 총급여", f"₩{df['총급여'].mean():,.0f}")
            
            with col2:
                if '결정세액' in df.columns:
                    st.metric("평균 결정세액", f"₩{df['결정세액'].mean():,.0f}")
            
            with col3:
                if '총급여' in df.columns:
                    st.metric("총급여 합계", f"₩{df['총급여'].sum():,.0f}")
            
            with col4:
                if '결정세액' in df.columns:
                    st.metric("결정세액 합계", f"₩{df['결정세액'].sum():,.0f}")
            
            # 엑셀 다운로드
            st.divider()
            st.subheader("📥 다운로드")
            
            if merge_excel:
                # 단일 엑셀 파일로 통합
                mapper = YearEndTaxExcelMapper()
                
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='연말정산_통합', index=False)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label="📥 통합 엑셀 다운로드",
                    data=buffer.getvalue(),
                    file_name=f"연말정산_일괄처리_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            else:
                # 개별 엑셀 파일로 제공
                st.info("💡 개별 다운로드는 메인 페이지에서 각 PDF를 처리하세요.")
        
        # 에러 표시
        if errors:
            st.divider()
            st.error(f"❌ {len(errors)}개 파일 처리 실패")
            
            with st.expander("⚠️ 에러 상세 내역"):
                for error in errors:
                    st.write(f"- {error}")

else:
    st.info("💡 PDF 파일을 업로드하면 일괄 처리를 시작할 수 있습니다.")
    
    st.markdown("""
    ### 📌 사용 방법
    
    1. **여러 PDF 선택**
       - 파일 선택 버튼 클릭
       - Ctrl(Cmd) + 클릭으로 여러 파일 선택
       - 또는 드래그 & 드롭
    
    2. **처리 옵션 선택**
       - 주택자금공제 파싱 여부
       - 엑셀 통합 여부
    
    3. **일괄 처리 시작**
       - 자동으로 모든 PDF 파싱
       - 통합 엑셀 다운로드
    
    ### ✨ 장점
    
    - ⚡ 빠른 처리: 여러 파일을 한 번에
    - 📊 통합 관리: 하나의 엑셀로
    - 🎯 정확한 추출: 자동 파싱
    - 💾 시간 절약: 수동 입력 불필요
    
    ### ⚠️ 주의사항
    
    - PDF 파일명에 직원명을 포함하면 자동 인식됩니다
    - 예: `홍길동_연말정산.pdf`, `김철수_2026.pdf`
    - 파일이 많을 경우 처리 시간이 소요될 수 있습니다
    """)

# 사이드바 정보
st.sidebar.markdown("""
### 💡 일괄 처리 팁

**파일명 규칙**
- `이름_연말정산.pdf`
- `이름_2026.pdf`

**권장 파일 수**
- 한 번에 10~20개 이하

**처리 시간**
- 파일당 약 2~5초
- 10개: 약 30초
- 20개: 약 1분

**지원 형식**
- PDF 파일만 가능
- 국세청 표준 양식
""")
