"""
출산·육아기 행정 업무 자동화 툴
핵심 계산 엔진
"""

import random
from datetime import date, datetime, timedelta
from typing import List, Dict, Tuple
from io import BytesIO
import pandas as pd

from constants import (
    PREGNANCY_SHORT_WORK,
    HOLIDAYS_2026,
    DESIGN_TASKS,
    REPLACEMENT_SUBSIDY,
    SHORT_WORK_SUBSIDY,
    WORKLOAD_SHARING_SUBSIDY,
    CHILDBIRTH_INFO,
    PARENTAL_LEAVE,
    REPLACEMENT_WORKER,
)

# PDF 생성 모듈 임포트
try:
    from pdf_generator import generate_pregnancy_forms
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# ============================================================
# 1. 재택근무 증빙 로그 생성기 (Smart Work Log)
# ============================================================

class SmartWorkLogGenerator:
    """재택근무 증빙 로그 생성 엔진"""
    
    @staticmethod
    def is_workday(target_date: date) -> bool:
        """
        평일인지 확인 (주말 및 공휴일 제외)
        
        Args:
            target_date: 확인할 날짜
            
        Returns:
            평일이면 True, 주말/공휴일이면 False
        """
        # 주말 체크 (0=월요일, 6=일요일)
        if target_date.weekday() >= 5:  # 토요일(5) 또는 일요일(6)
            return False
        
        # 공휴일 체크
        if target_date in HOLIDAYS_2026:
            return False
        
        return True
    
    @staticmethod
    def generate_random_time(base_time: str, delta_min: int, delta_max: int) -> str:
        """
        랜덤 시간 생성
        
        Args:
            base_time: 기준 시간 (HH:MM 형식)
            delta_min: 최소 변동 분 (음수 가능)
            delta_max: 최대 변동 분
            
        Returns:
            랜덤 시간 (HH:MM 형식)
        """
        hour, minute = map(int, base_time.split(':'))
        base_datetime = datetime(2026, 1, 1, hour, minute)
        
        random_delta = random.randint(delta_min, delta_max)
        new_datetime = base_datetime + timedelta(minutes=random_delta)
        
        return new_datetime.strftime("%H:%M")
    
    @staticmethod
    def generate_work_log(start_date: date, end_date: date, tasks: List[str]) -> pd.DataFrame:
        """
        재택근무 로그 생성
        
        Args:
            start_date: 시작일
            end_date: 종료일
            tasks: 업무 리스트
            
        Returns:
            재택근무 로그 DataFrame
        """
        logs = []
        current_date = start_date
        
        while current_date <= end_date:
            if SmartWorkLogGenerator.is_workday(current_date):
                # 시작 시간: 11:00 기준 -5분 ~ +5분
                start_time = SmartWorkLogGenerator.generate_random_time("11:00", -5, 5)
                
                # 종료 시간: 18:00 기준 0분 ~ +10분
                end_time = SmartWorkLogGenerator.generate_random_time("18:00", 0, 10)
                
                # 업무 내용 랜덤 선택
                task = random.choice(tasks)
                
                logs.append({
                    "날짜": current_date.strftime("%Y-%m-%d"),
                    "요일": ["월", "화", "수", "목", "금", "토", "일"][current_date.weekday()],
                    "근무 시작": start_time,
                    "근무 종료": end_time,
                    "휴게시간": "12:00-13:00",
                    "실근로시간": "6시간",
                    "업무 내용": task,
                    "비고": "재택근무(임신 중 근로시간 단축)",
                })
            
            current_date += timedelta(days=1)
        
        return pd.DataFrame(logs)
    
    @staticmethod
    def generate_pregnancy_log() -> pd.DataFrame:
        """
        임신 중 단축근무 기간 로그 생성 (constants.py 기준)
        
        Returns:
            재택근무 로그 DataFrame
        """
        start = PREGNANCY_SHORT_WORK["시작일"]
        end = PREGNANCY_SHORT_WORK["종료일"]
        tasks = DESIGN_TASKS
        
        return SmartWorkLogGenerator.generate_work_log(start, end, tasks)


# ============================================================
# 2. 2026 개정법 기준 지원금 시뮬레이터
# ============================================================

class SubsidyCalculator:
    """지원금 계산 엔진"""
    
    @staticmethod
    def calculate_replacement_subsidy() -> Dict:
        """
        대체인력 지원금 계산
        
        Returns:
            계산 결과 딕셔너리
        """
        # 인수인계 기간 지원금
        handover_days = REPLACEMENT_WORKER["인수인계_일수"]
        handover_months = handover_days / 30  # 대략적 월 환산
        handover_amount = int(REPLACEMENT_SUBSIDY["월지원금"] * handover_months)
        
        # 출산휴가 기간 지원금 (90일 = 3개월)
        maternity_months = CHILDBIRTH_INFO["출산휴가_일수"] / 30
        maternity_amount = int(REPLACEMENT_SUBSIDY["월지원금"] * maternity_months)
        
        # 육아휴직 기간 지원금 (12개월)
        parental_months = PARENTAL_LEAVE["기간_개월"]
        parental_amount = REPLACEMENT_SUBSIDY["월지원금"] * parental_months
        
        # 총 지원금
        total_amount = handover_amount + maternity_amount + parental_amount
        
        return {
            "인수인계기간": {
                "기간": f"{handover_days}일 (약 {handover_months:.1f}개월)",
                "시작일": REPLACEMENT_WORKER["인수인계_시작일"],
                "종료일": REPLACEMENT_WORKER["인수인계_종료일"],
                "지원금": handover_amount,
            },
            "출산휴가기간": {
                "기간": f"{CHILDBIRTH_INFO['출산휴가_일수']}일 (약 {maternity_months:.1f}개월)",
                "시작일": CHILDBIRTH_INFO["출산휴가_시작일"],
                "종료일": CHILDBIRTH_INFO["출산휴가_종료일"],
                "지원금": maternity_amount,
            },
            "육아휴직기간": {
                "기간": f"{parental_months}개월",
                "시작일": PARENTAL_LEAVE["시작일"],
                "종료일": PARENTAL_LEAVE["종료일"],
                "지원금": parental_amount,
            },
            "총지원금": total_amount,
            "월평균": REPLACEMENT_SUBSIDY["월지원금"],
            "비고": REPLACEMENT_SUBSIDY["비고"],
        }
    
    @staticmethod
    def calculate_short_work_subsidy() -> Dict:
        """
        육아기 근로시간 단축 장려금 계산
        
        Returns:
            계산 결과 딕셔너리
        """
        start = PREGNANCY_SHORT_WORK["시작일"]
        end = PREGNANCY_SHORT_WORK["종료일"]
        
        # 기간 계산 (일수)
        days = (end - start).days + 1  # +1은 시작일 포함
        
        # 근무일 수 계산
        workdays = 0
        current = start
        while current <= end:
            if SmartWorkLogGenerator.is_workday(current):
                workdays += 1
            current += timedelta(days=1)
        
        # 대략적 월 수 (근무일 기준)
        months = workdays / 22  # 월 평균 근무일 22일로 계산
        
        # 지원금 계산
        monthly_subsidy = SHORT_WORK_SUBSIDY["월지원금"]
        total_amount = int(monthly_subsidy * months)
        
        return {
            "시작일": start,
            "종료일": end,
            "총일수": days,
            "근무일수": workdays,
            "환산개월수": round(months, 2),
            "월지원금": monthly_subsidy,
            "총지원금": total_amount,
            "비고": SHORT_WORK_SUBSIDY["비고"],
        }
    
    @staticmethod
    def calculate_workload_sharing_subsidy() -> Dict:
        """
        업무분담 지원금 시뮬레이션
        
        Returns:
            계산 결과 딕셔너리
        """
        monthly_max = WORKLOAD_SHARING_SUBSIDY["월최대지원금"]
        max_months = WORKLOAD_SHARING_SUBSIDY["지원기간_개월"]
        
        total_max = monthly_max * max_months
        
        return {
            "월최대지원금": monthly_max,
            "최대지원기간": f"{max_months}개월",
            "최대총지원금": total_max,
            "비고": WORKLOAD_SHARING_SUBSIDY["비고"],
            "설명": "동료 직원에게 업무를 분담하고 보상하는 제도",
        }
    
    @staticmethod
    def calculate_all_subsidies() -> Dict:
        """
        모든 지원금 종합 계산
        
        Returns:
            전체 지원금 계산 결과
        """
        replacement = SubsidyCalculator.calculate_replacement_subsidy()
        short_work = SubsidyCalculator.calculate_short_work_subsidy()
        workload = SubsidyCalculator.calculate_workload_sharing_subsidy()
        
        total = (
            replacement["총지원금"] +
            short_work["총지원금"] +
            workload["최대총지원금"]
        )
        
        return {
            "대체인력지원금": replacement,
            "근로시간단축장려금": short_work,
            "업무분담지원금": workload,
            "총합계": total,
        }


# ============================================================
# 3. 정부 서식 데이터 맵핑
# ============================================================

class GovernmentFormMapper:
    """정부 서식 데이터 매핑 엔진"""
    
    @staticmethod
    def map_form_22_2(employee_info: Dict, employer_info: Dict) -> Dict:
        """
        별지 제22호의2 서식 (임신사유 근로시간 단축 확인서) 매핑
        
        Args:
            employee_info: 근로자 정보
            employer_info: 사업주 정보
            
        Returns:
            서식 데이터 딕셔너리
        """
        return {
            "서식명": "임신사유 근로시간 단축 확인서 (별지 제22호의2 서식)",
            "근로자정보": {
                "성명": employee_info["이름"],
                "주민등록번호": employee_info["주민등록번호"],
                "부서": employee_info["부서"],
                "직급": employee_info["직급"],
            },
            "임신정보": {
                "출산예정일": CHILDBIRTH_INFO["출산예정일"].strftime("%Y년 %m월 %d일"),
            },
            "단축근무정보": {
                "단축시작일": PREGNANCY_SHORT_WORK["시작일"].strftime("%Y년 %m월 %d일"),
                "단축종료일": PREGNANCY_SHORT_WORK["종료일"].strftime("%Y년 %m월 %d일"),
                "단축전_근로시간": "09:00 ~ 18:00 (휴게 1시간 제외, 실근로 8시간)",
                "단축후_근로시간": f"{PREGNANCY_SHORT_WORK['근무시간']['시작']} ~ {PREGNANCY_SHORT_WORK['근무시간']['종료']} (휴게 1시간 제외, 실근로 {PREGNANCY_SHORT_WORK['근무시간']['실근로시간']}시간)",
                "단축시간": "2시간",
            },
            "사업주정보": {
                "사업장명칭": employer_info.get("회사명", ""),
                "대표자성명": employer_info["대표자명"],
                "사업자등록번호": employer_info.get("사업자등록번호", ""),
            }
        }
    
    @staticmethod
    def map_form_7_2(employee_info: Dict, employer_info: Dict) -> Dict:
        """
        별지 제7호의2 서식 (출산전후휴가·육아휴직 통합 신청서) 매핑
        
        Args:
            employee_info: 근로자 정보
            employer_info: 사업주 정보
            
        Returns:
            서식 데이터 딕셔너리
        """
        return {
            "서식명": "출산전후휴가·육아휴직 통합 신청서 (별지 제7호의2 서식)",
            "근로자정보": {
                "성명": employee_info["이름"],
                "주민등록번호": employee_info["주민등록번호"],
                "부서": employee_info["부서"],
                "직급": employee_info["직급"],
            },
            "출산정보": {
                "출산예정일": CHILDBIRTH_INFO["출산예정일"].strftime("%Y년 %m월 %d일"),
            },
            "출산휴가정보": {
                "시작일": CHILDBIRTH_INFO["출산휴가_시작일"].strftime("%Y년 %m월 %d일"),
                "종료일": CHILDBIRTH_INFO["출산휴가_종료일"].strftime("%Y년 %m월 %d일"),
                "기간": f"{CHILDBIRTH_INFO['출산휴가_일수']}일",
                "비고": "법정 출산휴가 90일 사용",
            },
            "육아휴직정보": {
                "시작일": PARENTAL_LEAVE["시작일"].strftime("%Y년 %m월 %d일"),
                "종료일": PARENTAL_LEAVE["종료일"].strftime("%Y년 %m월 %d일"),
                "기간": f"{PARENTAL_LEAVE['기간_개월']}개월",
                "비고": "육아휴직 1년 사용",
            },
            "대체인력정보": {
                "채용일": REPLACEMENT_WORKER["채용일"].strftime("%Y년 %m월 %d일"),
                "인수인계시작일": REPLACEMENT_WORKER["인수인계_시작일"].strftime("%Y년 %m월 %d일"),
                "인수인계종료일": REPLACEMENT_WORKER["인수인계_종료일"].strftime("%Y년 %m월 %d일"),
                "인수인계기간": f"{REPLACEMENT_WORKER['인수인계_일수']}일",
                "비고": "대체인력 채용 완료 (인수인계 기간 지원금 타겟)",
            },
            "사업주정보": {
                "사업장명칭": employer_info.get("회사명", ""),
                "대표자성명": employer_info["대표자명"],
                "사업자등록번호": employer_info.get("사업자등록번호", ""),
            }
        }
    
    @staticmethod
    def generate_summary_table() -> pd.DataFrame:
        """
        전체 일정 요약 테이블 생성
        
        Returns:
            요약 DataFrame
        """
        data = [
            {
                "구분": "임신 중 단축근무",
                "시작일": PREGNANCY_SHORT_WORK["시작일"].strftime("%Y-%m-%d"),
                "종료일": PREGNANCY_SHORT_WORK["종료일"].strftime("%Y-%m-%d"),
                "기간": f"{(PREGNANCY_SHORT_WORK['종료일'] - PREGNANCY_SHORT_WORK['시작일']).days + 1}일",
                "비고": f"{PREGNANCY_SHORT_WORK['근무시간']['시작']}~{PREGNANCY_SHORT_WORK['근무시간']['종료']} 근무",
            },
            {
                "구분": "출산 휴가",
                "시작일": CHILDBIRTH_INFO["출산휴가_시작일"].strftime("%Y-%m-%d"),
                "종료일": CHILDBIRTH_INFO["출산휴가_종료일"].strftime("%Y-%m-%d"),
                "기간": f"{CHILDBIRTH_INFO['출산휴가_일수']}일",
                "비고": f"출산예정일: {CHILDBIRTH_INFO['출산예정일'].strftime('%Y-%m-%d')}",
            },
            {
                "구분": "육아 휴직",
                "시작일": PARENTAL_LEAVE["시작일"].strftime("%Y-%m-%d"),
                "종료일": PARENTAL_LEAVE["종료일"].strftime("%Y-%m-%d"),
                "기간": f"{PARENTAL_LEAVE['기간_개월']}개월",
                "비고": "1년 풀 사용",
            },
            {
                "구분": "대체인력 인수인계",
                "시작일": REPLACEMENT_WORKER["인수인계_시작일"].strftime("%Y-%m-%d"),
                "종료일": REPLACEMENT_WORKER["인수인계_종료일"].strftime("%Y-%m-%d"),
                "기간": f"{REPLACEMENT_WORKER['인수인계_일수']}일",
                "비고": f"채용일: {REPLACEMENT_WORKER['채용일'].strftime('%Y-%m-%d')}",
            },
        ]
        
        return pd.DataFrame(data)


# ============================================================
# 유틸리티 함수
# ============================================================

def format_currency(amount: int) -> str:
    """금액 포맷팅"""
    return f"{amount:,}원"


def calculate_date_range_days(start: date, end: date, workdays_only: bool = False) -> int:
    """
    날짜 범위 일수 계산
    
    Args:
        start: 시작일
        end: 종료일
        workdays_only: True면 근무일만 계산
        
    Returns:
        일수
    """
    if not workdays_only:
        return (end - start).days + 1
    
    days = 0
    current = start
    while current <= end:
        if SmartWorkLogGenerator.is_workday(current):
            days += 1
        current += timedelta(days=1)
    
    return days


# ============================================================
# 4. PDF 서식 생성 함수
# ============================================================

def generate_pdf_forms(employee_info: Dict = None, employer_info: Dict = None) -> Dict[str, BytesIO]:
    """
    임신 관련 PDF 서식 생성 (통합 함수)
    
    Args:
        employee_info: 근로자 정보 (None이면 constants.py에서 사용)
        employer_info: 사업주 정보 (None이면 constants.py에서 사용)
        
    Returns:
        서식명을 키로 하는 PDF BytesIO 딕셔너리
    """
    if not PDF_AVAILABLE:
        raise ImportError("PDF 생성 모듈을 불러올 수 없습니다. reportlab 설치가 필요합니다.")
    
    return generate_pregnancy_forms(employee_info, employer_info)
