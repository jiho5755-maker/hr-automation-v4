"""
work_schedules.py
시차 출퇴근제 및 근무 시간대 정의
"""

from datetime import time

# 시차 출퇴근제 프리셋
WORK_SCHEDULE_PRESETS = {
    "정규근무": {
        "name": "정규근무 (09:00~18:00)",
        "start_time": time(9, 0),
        "end_time": time(18, 0),
        "break_time": "12:00-13:00",
        "random_start_min": -5,
        "random_start_max": 5,
        "random_end_min": 0,
        "random_end_max": 10
    },
    "A조": {
        "name": "A조 시차제 (08:00~17:00)",
        "start_time": time(8, 0),
        "end_time": time(17, 0),
        "break_time": "12:00-13:00",
        "random_start_min": -5,
        "random_start_max": 5,
        "random_end_min": 0,
        "random_end_max": 10
    },
    "B조": {
        "name": "B조 시차제 (10:00~19:00)",
        "start_time": time(10, 0),
        "end_time": time(19, 0),
        "break_time": "13:00-14:00",
        "random_start_min": -5,
        "random_start_max": 5,
        "random_end_min": 0,
        "random_end_max": 10
    },
    "임신단축": {
        "name": "임신 단축근무 (11:00~18:00)",
        "start_time": time(11, 0),
        "end_time": time(18, 0),
        "break_time": "12:00-13:00",
        "random_start_min": -5,
        "random_start_max": 5,
        "random_end_min": 0,
        "random_end_max": 7
    },
    "육아단축": {
        "name": "육아기 단축근무 (09:00~16:00)",
        "start_time": time(9, 0),
        "end_time": time(16, 0),
        "break_time": "12:00-13:00",
        "random_start_min": -5,
        "random_start_max": 5,
        "random_end_min": 0,
        "random_end_max": 5
    },
    "선택근무1": {
        "name": "선택근무제1 (07:00~16:00)",
        "start_time": time(7, 0),
        "end_time": time(16, 0),
        "break_time": "12:00-13:00",
        "random_start_min": -5,
        "random_start_max": 5,
        "random_end_min": 0,
        "random_end_max": 10
    },
    "선택근무2": {
        "name": "선택근무제2 (11:00~20:00)",
        "start_time": time(11, 0),
        "end_time": time(20, 0),
        "break_time": "14:00-15:00",
        "random_start_min": -5,
        "random_start_max": 5,
        "random_end_min": 0,
        "random_end_max": 10
    },
    "맞춤": {
        "name": "맞춤형 (직접 입력)",
        "start_time": time(9, 0),
        "end_time": time(18, 0),
        "break_time": "12:00-13:00",
        "random_start_min": -5,
        "random_start_max": 5,
        "random_end_min": 0,
        "random_end_max": 10
    }
}


def get_schedule_preset(preset_name: str):
    """Get work schedule preset by name"""
    return WORK_SCHEDULE_PRESETS.get(preset_name, WORK_SCHEDULE_PRESETS["정규근무"])


def get_schedule_names():
    """Get list of schedule names"""
    return [preset["name"] for preset in WORK_SCHEDULE_PRESETS.values()]
