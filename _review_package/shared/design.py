"""
통일된 디자인 시스템
Modern Green Minimal Design System
모든 앱에서 일관된 디자인 제공
"""

import streamlit as st


# ============================================================
# 컬러 시스템 - Modern Green
# ============================================================

COLORS = {
    # Primary Colors (모던 그린)
    "primary": "#059669",      # 진한 초록 (메인)
    "primary_light": "#10b981", # 밝은 초록 (강조)
    "primary_dark": "#047857",  # 어두운 초록 (호버)
    
    # Secondary Colors
    "secondary": "#6366f1",     # 인디고 (보조)
    "secondary_light": "#818cf8",
    
    # Status Colors
    "success": "#10b981",       # 초록
    "warning": "#f59e0b",       # 오렌지
    "error": "#ef4444",         # 빨강
    "info": "#3b82f6",          # 파랑
    
    # Neutral Colors (미니멀)
    "background": "#f8fafc",    # 연한 회색 배경
    "card": "#ffffff",          # 카드 배경
    "border": "#e2e8f0",        # 테두리
    "text": "#1e293b",          # 진한 텍스트
    "text_secondary": "#64748b", # 보조 텍스트
    "text_light": "#94a3b8",    # 연한 텍스트
}


# ============================================================
# 타이포그래피
# ============================================================

TYPOGRAPHY = {
    "font_family": "'Inter', 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif",
    "font_size_base": "16px",
    "font_size_small": "14px",
    "font_size_large": "18px",
    "font_size_xlarge": "24px",
    "font_size_xxlarge": "32px",
    "line_height": "1.6",
}


# ============================================================
# 스페이싱 (미니멀을 위한 충분한 여백)
# ============================================================

SPACING = {
    "xs": "0.25rem",   # 4px
    "sm": "0.5rem",    # 8px
    "md": "1rem",      # 16px
    "lg": "1.5rem",    # 24px
    "xl": "2rem",      # 32px
    "xxl": "3rem",     # 48px
}


# ============================================================
# 보더 & 쉐도우 (플랫 + 소프트)
# ============================================================

STYLES = {
    "border_radius": "12px",
    "border_radius_sm": "8px",
    "border_radius_lg": "16px",
    
    # 소프트 쉐도우 (미니멀하게)
    "shadow_sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "shadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
    "shadow_md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    "shadow_lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
}


# ============================================================
# CSS 생성 함수
# ============================================================

def get_common_css() -> str:
    """
    모든 앱에 공통으로 적용되는 CSS
    
    Returns:
        CSS 문자열
    """
    return f"""
    <style>
    /* ========== 전역 스타일 ========== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* 기본 폰트 및 스타일 */
    html, body, [class*="css"] {{
        font-family: {TYPOGRAPHY['font_family']} !important;
        font-size: {TYPOGRAPHY['font_size_base']};
        line-height: {TYPOGRAPHY['line_height']};
        color: {COLORS['text']};
    }}
    
    /* 메인 컨테이너 배경 */
    .main {{
        background-color: {COLORS['background']};
        padding: {SPACING['lg']};
    }}
    
    /* ========== 타이틀 스타일 ========== */
    h1, h2, h3 {{
        color: {COLORS['text']};
        font-weight: 600;
        margin-bottom: {SPACING['lg']};
    }}
    
    h1 {{
        font-size: {TYPOGRAPHY['font_size_xxlarge']};
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    h2 {{
        font-size: {TYPOGRAPHY['font_size_xlarge']};
        color: {COLORS['primary']};
    }}
    
    h3 {{
        font-size: {TYPOGRAPHY['font_size_large']};
        color: {COLORS['text']};
    }}
    
    /* ========== 카드 스타일 (미니멀) ========== */
    .stCard, .app-card {{
        background: {COLORS['card']};
        border-radius: {STYLES['border_radius']};
        padding: {SPACING['xl']};
        box-shadow: {STYLES['shadow']};
        border: 1px solid {COLORS['border']};
        margin-bottom: {SPACING['lg']};
        transition: all 0.3s ease;
    }}
    
    .stCard:hover, .app-card:hover {{
        box-shadow: {STYLES['shadow_md']};
        transform: translateY(-2px);
    }}
    
    /* ========== 버튼 스타일 ========== */
    .stButton > button {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
        color: white;
        border: none;
        border-radius: {STYLES['border_radius_sm']};
        padding: {SPACING['sm']} {SPACING['lg']};
        font-weight: 500;
        font-size: {TYPOGRAPHY['font_size_base']};
        transition: all 0.3s ease;
        box-shadow: {STYLES['shadow_sm']};
    }}
    
    .stButton > button:hover {{
        box-shadow: {STYLES['shadow_md']};
        transform: translateY(-1px);
        background: linear-gradient(135deg, {COLORS['primary_dark']} 0%, {COLORS['primary']} 100%);
    }}
    
    .stButton > button:active {{
        transform: translateY(0);
    }}
    
    /* Secondary 버튼 */
    .stButton > button[kind="secondary"] {{
        background: {COLORS['card']};
        color: {COLORS['primary']};
        border: 2px solid {COLORS['primary']};
    }}
    
    .stButton > button[kind="secondary"]:hover {{
        background: {COLORS['primary']};
        color: white;
    }}
    
    /* ========== Input 스타일 ========== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {{
        border-radius: {STYLES['border_radius_sm']};
        border: 2px solid {COLORS['border']};
        padding: {SPACING['sm']};
        font-size: {TYPOGRAPHY['font_size_base']};
        transition: all 0.3s ease;
    }}
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {COLORS['primary']};
        box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
    }}
    
    /* ========== Metric 카드 스타일 ========== */
    [data-testid="stMetricValue"] {{
        font-size: {TYPOGRAPHY['font_size_xlarge']};
        font-weight: 600;
        color: {COLORS['primary']};
    }}
    
    [data-testid="stMetricLabel"] {{
        font-size: {TYPOGRAPHY['font_size_base']};
        color: {COLORS['text_secondary']};
        font-weight: 500;
    }}
    
    /* ========== Alert 스타일 ========== */
    .stSuccess {{
        background-color: rgba(16, 185, 129, 0.1);
        color: {COLORS['success']};
        border-left: 4px solid {COLORS['success']};
        border-radius: {STYLES['border_radius_sm']};
        padding: {SPACING['md']};
    }}
    
    .stWarning {{
        background-color: rgba(245, 158, 11, 0.1);
        color: {COLORS['warning']};
        border-left: 4px solid {COLORS['warning']};
        border-radius: {STYLES['border_radius_sm']};
        padding: {SPACING['md']};
    }}
    
    .stError {{
        background-color: rgba(239, 68, 68, 0.1);
        color: {COLORS['error']};
        border-left: 4px solid {COLORS['error']};
        border-radius: {STYLES['border_radius_sm']};
        padding: {SPACING['md']};
    }}
    
    .stInfo {{
        background-color: rgba(59, 130, 246, 0.1);
        color: {COLORS['info']};
        border-left: 4px solid {COLORS['info']};
        border-radius: {STYLES['border_radius_sm']};
        padding: {SPACING['md']};
    }}
    
    /* ========== Dataframe 스타일 ========== */
    .stDataFrame {{
        border-radius: {STYLES['border_radius']};
        overflow: hidden;
        box-shadow: {STYLES['shadow']};
    }}
    
    /* ========== Sidebar 스타일 ========== */
    [data-testid="stSidebar"] {{
        background-color: {COLORS['card']};
        border-right: 1px solid {COLORS['border']};
    }}
    
    [data-testid="stSidebar"] .stButton > button {{
        width: 100%;
    }}
    
    /* ========== Divider 스타일 ========== */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, {COLORS['border']}, transparent);
        margin: {SPACING['lg']} 0;
    }}
    
    /* ========== Tab 스타일 ========== */
    .stTabs [data-baseweb="tab-list"] {{
        gap: {SPACING['sm']};
        background-color: transparent;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        border-radius: {STYLES['border_radius_sm']};
        color: {COLORS['text_secondary']};
        font-weight: 500;
        padding: {SPACING['sm']} {SPACING['lg']};
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: rgba(5, 150, 105, 0.1);
        color: {COLORS['primary']};
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['primary']} !important;
        color: white !important;
    }}
    
    /* ========== Progress Bar 스타일 ========== */
    .stProgress > div > div > div > div {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
        border-radius: {STYLES['border_radius_sm']};
    }}
    
    /* ========== Checkbox/Radio 스타일 ========== */
    .stCheckbox > label {{
        font-weight: 500;
        color: {COLORS['text']};
    }}
    
    /* ========== 모바일 반응형 ========== */
    @media (max-width: 768px) {{
        .main {{
            padding: {SPACING['md']};
        }}
        
        h1 {{
            font-size: {TYPOGRAPHY['font_size_xlarge']};
        }}
        
        .stCard, .app-card {{
            padding: {SPACING['md']};
        }}
    }}
    
    /* ========== 애니메이션 ========== */
    @keyframes fadeIn {{
        from {{
            opacity: 0;
            transform: translateY(10px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    .stCard, .app-card, .stButton {{
        animation: fadeIn 0.3s ease-out;
    }}
    
    /* ========== 스크롤바 스타일 ========== */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {COLORS['background']};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {COLORS['primary_light']};
        border-radius: {STYLES['border_radius_sm']};
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS['primary']};
    }}
    </style>
    """


def apply_design():
    """
    현재 앱에 디자인 시스템 적용
    모든 앱의 시작 부분에서 호출
    """
    st.markdown(get_common_css(), unsafe_allow_html=True)


def get_gradient_text(text: str, size: str = "xxlarge") -> str:
    """
    그라데이션 텍스트 생성
    
    Args:
        text: 표시할 텍스트
        size: 크기 (xxlarge, xlarge, large, base)
    
    Returns:
        HTML 문자열
    """
    font_sizes = {
        "xxlarge": TYPOGRAPHY['font_size_xxlarge'],
        "xlarge": TYPOGRAPHY['font_size_xlarge'],
        "large": TYPOGRAPHY['font_size_large'],
        "base": TYPOGRAPHY['font_size_base'],
    }
    
    return f"""
    <h1 style="
        font-size: {font_sizes.get(size, TYPOGRAPHY['font_size_xxlarge'])};
        font-weight: 600;
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: {SPACING['lg']};
    ">{text}</h1>
    """
