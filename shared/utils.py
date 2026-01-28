"""
공통 유틸리티 함수
모든 앱에서 사용하는 공통 기능 제공
"""

import streamlit as st
from datetime import datetime, date
from typing import Optional


# ============================================================
# Toast 알림 함수 (모던 그린 디자인)
# ============================================================

def show_success(message: str, icon: str = "✅"):
    """
    성공 메시지 표시 (Toast 알림)
    
    Args:
        message: 표시할 메시지
        icon: 표시할 아이콘 (기본: ✅)
    """
    st.toast(f'{icon} {message}', icon=icon)


def show_info(message: str, icon: str = "ℹ️"):
    """
    정보 메시지 표시 (Toast 알림)
    
    Args:
        message: 표시할 메시지
        icon: 표시할 아이콘
    """
    st.toast(f'{icon} {message}', icon=icon)


def show_warning(message: str, icon: str = "⚠️"):
    """
    경고 메시지 표시 (Toast 알림)
    
    Args:
        message: 표시할 메시지
        icon: 표시할 아이콘
    """
    st.toast(f'{icon} {message}', icon=icon)


def show_error(message: str, icon: str = "❌"):
    """
    오류 메시지 표시 (Toast 알림)
    
    Args:
        message: 표시할 메시지
        icon: 표시할 아이콘
    """
    st.toast(f'{icon} {message}', icon=icon)


# ============================================================
# 포맷팅 유틸리티
# ============================================================

def format_currency(amount: Optional[int]) -> str:
    """
    금액 포맷팅
    
    Args:
        amount: 금액
        
    Returns:
        포맷팅된 금액 문자열 (예: ₩1,000,000)
    """
    if amount is None or amount == 0:
        return "₩0"
    return f"₩{amount:,.0f}"


def format_date(date_obj: Optional[date], format_str: str = "%Y-%m-%d") -> str:
    """
    날짜 포맷팅
    
    Args:
        date_obj: 날짜 객체
        format_str: 포맷 문자열
        
    Returns:
        포맷팅된 날짜 문자열
    """
    if date_obj is None:
        return "-"
    
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
        except:
            return date_obj
    
    return date_obj.strftime(format_str)


def get_korean_weekday(date_obj: Optional[date] = None) -> str:
    """
    한글 요일 반환
    
    Args:
        date_obj: 날짜 객체 (None이면 오늘)
        
    Returns:
        한글 요일 (예: 월, 화, 수...)
    """
    if date_obj is None:
        date_obj = date.today()
    
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
        except:
            return ""
    
    weekday_map = {
        0: "월",
        1: "화",
        2: "수",
        3: "목",
        4: "금",
        5: "토",
        6: "일"
    }
    
    return weekday_map.get(date_obj.weekday(), "")


def get_current_year_month() -> str:
    """
    현재 년-월 반환 (YYYY-MM 형식)
    
    Returns:
        현재 년-월 문자열
    """
    return datetime.now().strftime("%Y-%m")
