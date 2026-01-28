"""
설정 페이지
Settings Page

시스템 정보 및 설정 관리
"""

import streamlit as st
import sys
from pathlib import Path
import os

# 상위 디렉토리의 shared 모듈 import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.database import get_db
from shared.design import apply_design

# 디자인 적용
apply_design()


# ============================================================================
# 설정 페이지
# ============================================================================

def show():
    """설정 페이지 표시"""
    
    # 타이틀
    st.markdown('<div class="main-title">⚙️ 시스템 설정</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">시스템 정보 및 설정 관리</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # 시스템 정보
    # ========================================================================
    
    st.markdown("### 📊 시스템 정보")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **버전 정보**:
        - 시스템 버전: v4.0.0 (통합)
        - 데이터베이스: SQLite (hr_master.db)
        - 백업 위치: `_backups/`
        """)
        
        st.markdown("""
        **포트 정보** (변경됨!):
        - ✅ 통합 대시보드: **8000** (모든 모듈 통합)
        - ~~출산육아: 8501~~ (통합됨)
        - ~~재택근무: 8503~~ (통합됨)
        - ~~급여관리: 8505~~ (통합됨)
        """)
    
    with col2:
        # 데이터베이스 파일 정보
        db_path = Path(__file__).parent.parent.parent / "hr_master.db"
        
        if db_path.exists():
            db_size = os.path.getsize(db_path)
            db_size_mb = db_size / (1024 * 1024)
            
            st.markdown(f"""
            **데이터베이스 정보**:
            - 파일 크기: {db_size_mb:.2f} MB
            - 위치: `{db_path.name}`
            - 상태: ✅ 정상
            """)
        else:
            st.warning("⚠️ 데이터베이스 파일을 찾을 수 없습니다.")
    
    st.divider()
    
    # ========================================================================
    # 데이터베이스 통계
    # ========================================================================
    
    st.markdown("### 📈 데이터베이스 통계")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 각 테이블 레코드 수
        tables_stats = []
        
        try:
            cursor.execute("SELECT COUNT(*) FROM employees")
            emp_count = cursor.fetchone()[0]
            tables_stats.append(("👥 직원", emp_count))
        except:
            tables_stats.append(("👥 직원", 0))
        
        try:
            cursor.execute("SELECT COUNT(*) FROM work_logs")
            log_count = cursor.fetchone()[0]
            tables_stats.append(("🏠 근무 로그", log_count))
        except:
            tables_stats.append(("🏠 근무 로그", 0))
        
        try:
            cursor.execute("SELECT COUNT(*) FROM subsidies")
            subsidy_count = cursor.fetchone()[0]
            tables_stats.append(("💰 지원금", subsidy_count))
        except:
            tables_stats.append(("💰 지원금", 0))
        
        try:
            cursor.execute("SELECT COUNT(*) FROM applications")
            app_count = cursor.fetchone()[0]
            tables_stats.append(("📋 신청 내역", app_count))
        except:
            tables_stats.append(("📋 신청 내역", 0))
        
        try:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            tables_stats.append(("👤 사용자", user_count))
        except:
            tables_stats.append(("👤 사용자", 0))
        
        try:
            cursor.execute("SELECT COUNT(*) FROM system_logs")
            syslog_count = cursor.fetchone()[0]
            tables_stats.append(("📊 시스템 로그", syslog_count))
        except:
            tables_stats.append(("📊 시스템 로그", 0))
    
    # 3열로 표시
    col1, col2, col3 = st.columns(3)
    
    for i, (label, count) in enumerate(tables_stats):
        with [col1, col2, col3][i % 3]:
            st.metric(label, f"{count:,}건")
    
    st.divider()
    
    # ========================================================================
    # v4.0 새로운 기능
    # ========================================================================
    
    st.markdown("### ✨ v4.0 새로운 기능")
    
    st.success("""
    **🎉 완전 통합 완료!**
    
    ✅ **단일 포트 실행**: 모든 모듈이 포트 8000에서 실행됩니다.  
    ✅ **데이터 중복 제거**: 직원 정보를 한 번만 입력하면 모든 모듈에 자동 반영됩니다.  
    ✅ **급여 자동화**: 급여 계산 결과가 명세서에 자동으로 반영됩니다.  
    ✅ **실시간 동기화**: 페이지 전환 시 최신 정보를 자동으로 불러옵니다.  
    """)
    
    st.info("""
    **🔄 마이그레이션 안내**
    
    기존 `employees_data.json` 파일을 사용하던 출산육아 모듈도 이제 통합 데이터베이스를 사용합니다.
    
    마이그레이션이 필요한 경우:
    ```bash
    python3 scripts/migrate_json_to_db.py
    ```
    """)
    
    st.divider()
    
    # ========================================================================
    # 시스템 유지보수
    # ========================================================================
    
    st.markdown("### 🔧 시스템 유지보수")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **백업 관리**:
        - 정기 백업은 `_backups/` 폴더에 저장됩니다
        - 수동 백업: `cp -r . _backups/backup_$(date +%Y%m%d)/`
        """)
    
    with col2:
        st.markdown("""
        **로그 관리**:
        - 시스템 로그는 `system_logs` 테이블에 저장됩니다
        - 최근 활동은 대시보드에서 확인 가능합니다
        """)
    
    st.divider()
    
    # ========================================================================
    # 문의 및 지원
    # ========================================================================
    
    st.markdown("### 💬 문의 및 지원")
    
    st.markdown("""
    **📖 문서**:
    - 사용자 가이드: `🚀_구현_시작_가이드.md`
    - 기술 문서: `planning/hr-automation-integration/`
    
    **🐛 문제 발생 시**:
    1. `system_logs` 테이블 확인
    2. 백업에서 복구: `cp -r _backups/backup_[날짜]/* .`
    3. 롤백: `git checkout main`
    """)


# ============================================================================
# 페이지 실행
# ============================================================================

show()
