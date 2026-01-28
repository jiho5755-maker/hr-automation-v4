"""
holidays.py
한국 법정 공휴일 정의
"""

from datetime import date

# 2025-2026년 한국 법정 공휴일
KOREAN_HOLIDAYS = {
    # 2025년
    date(2025, 1, 1): "신정",
    date(2025, 1, 28): "설날 연휴",
    date(2025, 1, 29): "설날",
    date(2025, 1, 30): "설날 연휴",
    date(2025, 3, 1): "삼일절",
    date(2025, 5, 5): "어린이날",
    date(2025, 5, 6): "부처님오신날",
    date(2025, 6, 6): "현충일",
    date(2025, 8, 15): "광복절",
    date(2025, 10, 5): "추석 연휴",
    date(2025, 10, 6): "추석",
    date(2025, 10, 7): "추석 연휴",
    date(2025, 10, 3): "개천절",
    date(2025, 10, 9): "한글날",
    date(2025, 12, 25): "크리스마스",
    
    # 2026년
    date(2026, 1, 1): "신정",
    date(2026, 2, 16): "설날 연휴",
    date(2026, 2, 17): "설날",
    date(2026, 2, 18): "설날 연휴",
    date(2026, 3, 1): "삼일절",
    date(2026, 5, 5): "어린이날",
    date(2026, 5, 24): "부처님오신날",
    date(2026, 6, 6): "현충일",
    date(2026, 8, 15): "광복절",
    date(2026, 9, 24): "추석 연휴",
    date(2026, 9, 25): "추석",
    date(2026, 9, 26): "추석 연휴",
    date(2026, 10, 3): "개천절",
    date(2026, 10, 9): "한글날",
    date(2026, 12, 25): "크리스마스",
    
    # 2027년
    date(2027, 1, 1): "신정",
    date(2027, 2, 6): "설날 연휴",
    date(2027, 2, 7): "설날",
    date(2027, 2, 8): "설날 연휴",
    date(2027, 3, 1): "삼일절",
    date(2027, 5, 5): "어린이날",
    date(2027, 5, 13): "부처님오신날",
    date(2027, 6, 6): "현충일",
    date(2027, 8, 15): "광복절",
    date(2027, 10, 3): "개천절",
    date(2027, 10, 9): "한글날",
    date(2027, 10, 14): "추석 연휴",
    date(2027, 10, 15): "추석",
    date(2027, 10, 16): "추석 연휴",
    date(2027, 12, 25): "크리스마스",
}


def is_holiday(check_date: date) -> bool:
    """
    Check if a date is a Korean public holiday
    Args:
        check_date: Date to check
    Returns:
        True if holiday, False otherwise
    """
    return check_date in KOREAN_HOLIDAYS


def get_holiday_name(check_date: date) -> str:
    """
    Get holiday name for a date
    Args:
        check_date: Date to check
    Returns:
        Holiday name or empty string if not a holiday
    """
    return KOREAN_HOLIDAYS.get(check_date, "")


def is_workday(check_date: date) -> bool:
    """
    Check if a date is a workday (not weekend and not holiday)
    Args:
        check_date: Date to check
    Returns:
        True if workday (Mon-Fri excluding holidays), False otherwise
    """
    # Check if weekend (Saturday=5, Sunday=6)
    if check_date.weekday() >= 5:
        return False
    
    # Check if holiday
    if is_holiday(check_date):
        return False
    
    return True
