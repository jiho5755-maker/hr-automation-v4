"""
정부지원금 자동화 - 신청 이력 관리
지원금 신청 현황을 추적하고 관리
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 상위 디렉토리 모듈 import
sys.path.append(str(Path(__file__).parent.parent))

from database import Database, ApplicationManager

# 페이지 설정
st.set_page_config(
    page_title="지원금 신청 이력",
    page_icon="📋",
    layout="wide"
)

# CSS 스타일
st.markdown("""
<style>
    .status-box {
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        text-align: center;
        font-weight: bold;
    }
    .status-pending {
        background-color: #fff3cd;
        color: #856404;
    }
    .status-submitted {
        background-color: #d1ecf1;
        color: #0c5460;
    }
    .status-approved {
        background-color: #d4edda;
        color: #155724;
    }
    .status-rejected {
        background-color: #f8d7da;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

st.title("📋 정부지원금 신청 이력")
st.markdown("신청한 지원금의 현황을 확인하고 관리합니다.")

st.divider()

# ============================================================
# 데이터베이스 연결
# ============================================================

db = Database()
app_manager = ApplicationManager()

# ============================================================
# 필터 옵션
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    status_filter = st.selectbox(
        "📊 상태",
        ["전체", "신청준비", "신청완료", "승인", "반려"]
    )

with col2:
    period_filter = st.selectbox(
        "📅 기간",
        ["전체", "최근 1개월", "최근 3개월", "최근 6개월", "올해"]
    )

with col3:
    sort_by = st.selectbox(
        "🔄 정렬",
        ["최근 신청순", "오래된 순", "금액 높은 순", "금액 낮은 순"]
    )

st.divider()

# ============================================================
# 신청 이력 조회
# ============================================================

try:
    # 모든 신청 이력 가져오기
    all_applications = app_manager.get_all_applications()
    
    if not all_applications:
        st.info("💡 아직 신청한 지원금이 없습니다.")
        
        st.markdown("""
        ### 📌 지원금 신청 방법
        
        1. **메인 페이지로 이동** 
           - 사이드바에서 'app_v3' 선택
        
        2. **지원금 검색**
           - 키워드 또는 조건으로 검색
        
        3. **신청하기**
           - 상세 정보 입력 후 신청
        
        4. **이력 확인**
           - 이 페이지에서 진행 상황 확인
        """)
        
        st.stop()
    
    # DataFrame 생성
    df = pd.DataFrame(all_applications)
    
    # 필터 적용
    filtered_df = df.copy()
    
    # 상태 필터
    if status_filter != "전체":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    # 기간 필터
    if period_filter != "전체":
        today = datetime.now()
        
        if period_filter == "최근 1개월":
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        elif period_filter == "최근 3개월":
            start_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
        elif period_filter == "최근 6개월":
            start_date = (today - timedelta(days=180)).strftime("%Y-%m-%d")
        elif period_filter == "올해":
            start_date = f"{today.year}-01-01"
        
        filtered_df = filtered_df[filtered_df['application_date'] >= start_date]
    
    # 정렬
    if sort_by == "최근 신청순":
        filtered_df = filtered_df.sort_values('application_date', ascending=False)
    elif sort_by == "오래된 순":
        filtered_df = filtered_df.sort_values('application_date', ascending=True)
    elif sort_by == "금액 높은 순":
        filtered_df = filtered_df.sort_values('expected_amount', ascending=False)
    elif sort_by == "금액 낮은 순":
        filtered_df = filtered_df.sort_values('expected_amount', ascending=True)
    
    # ============================================================
    # 통계
    # ============================================================
    
    st.subheader("📊 신청 통계")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 신청", f"{len(filtered_df)}건")
    
    with col2:
        approved = len(filtered_df[filtered_df['status'] == '승인'])
        st.metric("승인", f"{approved}건")
    
    with col3:
        total_expected = filtered_df['expected_amount'].sum()
        st.metric("예상 총액", f"₩{total_expected:,.0f}")
    
    with col4:
        # 승인된 금액 합계 (실제 지급 금액이 있다면)
        approved_df = filtered_df[filtered_df['status'] == '승인']
        if len(approved_df) > 0:
            approved_amount = approved_df['expected_amount'].sum()
            st.metric("승인 금액", f"₩{approved_amount:,.0f}")
        else:
            st.metric("승인 금액", "₩0")
    
    st.divider()
    
    # ============================================================
    # 신청 이력 테이블
    # ============================================================
    
    st.subheader("📋 신청 목록")
    
    if len(filtered_df) == 0:
        st.info(f"💡 {status_filter} / {period_filter} 조건에 맞는 신청이 없습니다.")
    else:
        # 표시용 DataFrame 생성
        display_df = filtered_df.copy()
        
        # 상태 색상 표시
        def status_color(status):
            if status == "신청준비":
                return "🟡 신청준비"
            elif status == "신청완료":
                return "🔵 신청완료"
            elif status == "승인":
                return "🟢 승인"
            elif status == "반려":
                return "🔴 반려"
            return status
        
        display_df['상태'] = display_df['status'].apply(status_color)
        display_df['예상금액'] = display_df['expected_amount'].apply(lambda x: f"₩{x:,.0f}")
        
        # 컬럼 선택
        columns_to_show = ['상태', 'subsidy_name', 'application_date', '예상금액']
        column_names = ['상태', '지원금명', '신청일', '예상금액']
        
        display_df = display_df[columns_to_show]
        display_df.columns = column_names
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # ============================================================
        # 상세 정보
        # ============================================================
        
        st.divider()
        st.subheader("🔍 상세 정보")
        
        # 선택한 신청 확인
        selected_idx = st.selectbox(
            "상세보기",
            range(len(filtered_df)),
            format_func=lambda i: f"{filtered_df.iloc[i]['subsidy_name']} ({filtered_df.iloc[i]['application_date']})"
        )
        
        if selected_idx is not None:
            selected = filtered_df.iloc[selected_idx]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **📌 기본 정보**
                - **지원금명**: {selected['subsidy_name']}
                - **신청일**: {selected['application_date']}
                - **상태**: {status_color(selected['status'])}
                - **예상금액**: ₩{selected['expected_amount']:,.0f}
                """)
            
            with col2:
                st.markdown(f"""
                **📝 추가 정보**
                - **신청 ID**: {selected.get('id', 'N/A')}
                - **지원금 ID**: {selected.get('subsidy_id', 'N/A')}
                """)
            
            # 비고
            if 'notes' in selected and selected['notes']:
                st.markdown(f"""
                **📄 비고**
                
                {selected['notes']}
                """)
            
            # 상태 변경
            st.divider()
            st.markdown("**🔄 상태 변경**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ 승인으로 변경", use_container_width=True):
                    if app_manager.update_application_status(selected['id'], "승인"):
                        st.success("상태가 '승인'으로 변경되었습니다!")
                        st.rerun()
                    else:
                        st.error("상태 변경 실패")
            
            with col2:
                if st.button("🔵 신청완료로 변경", use_container_width=True):
                    if app_manager.update_application_status(selected['id'], "신청완료"):
                        st.success("상태가 '신청완료'로 변경되었습니다!")
                        st.rerun()
                    else:
                        st.error("상태 변경 실패")
            
            with col3:
                if st.button("❌ 반려로 변경", use_container_width=True):
                    if app_manager.update_application_status(selected['id'], "반려"):
                        st.warning("상태가 '반려'로 변경되었습니다.")
                        st.rerun()
                    else:
                        st.error("상태 변경 실패")
    
    # ============================================================
    # 상태별 차트
    # ============================================================
    
    st.divider()
    st.subheader("📈 상태별 분포")
    
    status_counts = df['status'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 상태별 건수
        st.bar_chart(status_counts)
    
    with col2:
        # 상태별 비율
        st.write("**상태별 비율**")
        for status, count in status_counts.items():
            percentage = (count / len(df)) * 100
            st.write(f"- {status}: {count}건 ({percentage:.1f}%)")

except Exception as e:
    st.error(f"❌ 데이터 조회 실패: {str(e)}")
    import traceback
    with st.expander("🔍 에러 상세"):
        st.code(traceback.format_exc())

# ============================================================
# 사이드바
# ============================================================

st.sidebar.markdown("""
### 💡 상태 설명

**🟡 신청준비**
- 신청서 작성 중
- 서류 준비 중

**🔵 신청완료**
- 신청서 제출 완료
- 심사 대기 중

**🟢 승인**
- 심사 통과
- 지원금 지급 예정/완료

**🔴 반려**
- 심사 탈락
- 조건 미충족

### 📊 활용 방법

1. **필터 사용**
   - 상태/기간으로 검색
   - 정렬 기능 활용

2. **상태 관리**
   - 진행 상황 업데이트
   - 메모 추가

3. **통계 활용**
   - 승인율 확인
   - 예상 지원금 파악
""")

st.sidebar.divider()

st.sidebar.success("""
✅ **팁**

- 정기적으로 상태 업데이트
- 반려 사유 메모
- 승인 금액 실제 지급액과 비교
- 신청 성공률 분석
""")
