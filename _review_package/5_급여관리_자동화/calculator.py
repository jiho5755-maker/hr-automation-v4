"""
급여관리 자동화 - 급여 계산 엔진
4대보험, 소득세, 실수령액 자동 계산
2026년 기준 법정 검증 포함
"""

from datetime import datetime, timedelta
import math
from typing import Dict, List, Tuple, Optional
import constants as C


class PayrollCalculator:
    """급여 계산 엔진"""
    
    def __init__(self, employee_count=1):
        """
        Args:
            employee_count: 사업장 근로자 수 (고용보험료율 결정)
        """
        self.employee_count = employee_count
    
    def calculate_national_pension(self, base_salary: float) -> Dict[str, float]:
        """
        국민연금 계산
        
        Args:
            base_salary: 기준소득월액
        
        Returns:
            dict: 근로자부담금, 사업주부담금, 합계
        """
        # 기준소득월액 적용 (최저~최고 구간)
        pension_base = base_salary
        if pension_base < C.INSURANCE_RATES["국민연금"]["최저기준"]:
            pension_base = C.INSURANCE_RATES["국민연금"]["최저기준"]
        elif pension_base > C.INSURANCE_RATES["국민연금"]["최고기준"]:
            pension_base = C.INSURANCE_RATES["국민연금"]["최고기준"]
        
        # 근로자/사업주 각 4.5%
        employee_pension = math.floor(pension_base * C.INSURANCE_RATES["국민연금"]["근로자부담"])
        employer_pension = math.floor(pension_base * C.INSURANCE_RATES["국민연금"]["사업주부담"])
        
        return {
            "근로자부담": employee_pension,
            "사업주부담": employer_pension,
            "합계": employee_pension + employer_pension,
            "기준소득": pension_base
        }
    
    def calculate_health_insurance(self, base_salary: float) -> Dict[str, float]:
        """
        건강보험 및 장기요양보험 계산
        
        Args:
            base_salary: 보수월액
        
        Returns:
            dict: 근로자/사업주 부담금, 장기요양보험
        """
        # 건강보험료 (근로자/사업주 각 50%)
        health_insurance = math.floor(base_salary * C.INSURANCE_RATES["건강보험"]["요율"])
        employee_health = math.floor(health_insurance / 2)
        employer_health = health_insurance - employee_health
        
        # 장기요양보험료 (건강보험료의 12.95%)
        longterm_care = math.floor(health_insurance * C.INSURANCE_RATES["건강보험"]["장기요양"])
        employee_longterm = math.floor(longterm_care / 2)
        employer_longterm = longterm_care - employee_longterm
        
        return {
            "건강보험": {
                "근로자부담": employee_health,
                "사업주부담": employer_health,
                "합계": health_insurance
            },
            "장기요양": {
                "근로자부담": employee_longterm,
                "사업주부담": employer_longterm,
                "합계": longterm_care
            },
            "합계": health_insurance + longterm_care
        }
    
    def calculate_employment_insurance(self, base_salary: float) -> Dict[str, float]:
        """
        고용보험 계산
        
        Args:
            base_salary: 보수월액
        
        Returns:
            dict: 근로자부담금, 사업주부담금
        """
        # 실업급여 (근로자 0.9%, 사업주 0.9%)
        employee_unemployment = math.floor(base_salary * C.INSURANCE_RATES["고용보험"]["실업급여"]["근로자"])
        employer_unemployment = math.floor(base_salary * C.INSURANCE_RATES["고용보험"]["실업급여"]["사업주"])
        
        # 고용안정·직업능력개발사업 (사업주만 부담, 사업장 규모별)
        if self.employee_count < 150:
            employer_stability = math.floor(base_salary * C.INSURANCE_RATES["고용보험"]["고용안정"]["150인미만"])
        elif self.employee_count < 1000:
            employer_stability = math.floor(base_salary * C.INSURANCE_RATES["고용보험"]["고용안정"]["150인이상_1000인미만"])
        else:
            employer_stability = math.floor(base_salary * C.INSURANCE_RATES["고용보험"]["고용안정"]["1000인이상"])
        
        return {
            "근로자부담": employee_unemployment,
            "사업주부담": employer_unemployment + employer_stability,
            "합계": employee_unemployment + employer_unemployment + employer_stability,
            "실업급여": {
                "근로자": employee_unemployment,
                "사업주": employer_unemployment
            },
            "고용안정": employer_stability
        }
    
    def calculate_industrial_insurance(self, base_salary: float, industry_rate: float = None) -> Dict[str, float]:
        """
        산재보험 계산 (사업주 전액 부담)
        
        Args:
            base_salary: 보수월액
            industry_rate: 업종별 요율 (미지정 시 기본요율)
        
        Returns:
            dict: 산재보험료
        """
        rate = industry_rate if industry_rate else C.INSURANCE_RATES["산재보험"]["기본요율"]
        industrial_insurance = math.floor(base_salary * rate)
        
        return {
            "근로자부담": 0,
            "사업주부담": industrial_insurance,
            "합계": industrial_insurance,
            "적용요율": rate
        }
    
    def calculate_income_tax_simple(
        self,
        monthly_salary: float,
        dependents: int = 1,
        non_taxable: float = 0
    ) -> float:
        """
        간이세액표 기준 소득세 계산
        
        Args:
            monthly_salary: 월 급여
            dependents: 부양가족 수 (본인 포함)
            non_taxable: 비과세 소득
        
        Returns:
            float: 월 소득세
        """
        # 과세대상 급여
        taxable_income = monthly_salary - non_taxable
        
        # 간이세액표 (매우 단순화된 버전)
        # 실제로는 국세청 간이세액표를 참고해야 함
        if taxable_income <= 1000000:
            return 0
        elif taxable_income <= 2000000:
            base_tax = (taxable_income - 1000000) * 0.04
        elif taxable_income <= 3000000:
            base_tax = 40000 + (taxable_income - 2000000) * 0.06
        elif taxable_income <= 5000000:
            base_tax = 100000 + (taxable_income - 3000000) * 0.08
        else:
            base_tax = 260000 + (taxable_income - 5000000) * 0.10
        
        # 부양가족 공제 (1인당 약 12,500원 감면)
        deduction = (dependents - 1) * 12500
        
        return max(0, math.floor(base_tax - deduction))
    
    def calculate_all(
        self,
        base_salary: float,
        allowances: Dict[str, float],
        tax_free_items: Dict[str, float] = None,
        apply_pension: bool = True,
        apply_health: bool = True,
        apply_longterm: bool = True,
        apply_employment: bool = True,
        fixed_ot_amount: int = 0,
        work_days: int = None,
        month_days: int = None
    ) -> Dict[str, any]:
        """
        급여 전체 계산
        
        Args:
            base_salary: 기본급
            allowances: 각종 수당
            tax_free_items: 비과세 항목
            apply_pension: 국민연금 적용 여부
            apply_health: 건강보험 적용 여부
            apply_longterm: 장기요양 적용 여부
            apply_employment: 고용보험 적용 여부
            fixed_ot_amount: 고정 OT 금액
            work_days: 실 근무일수 (일할계산)
            month_days: 월 총 일수 (일할계산)
        
        Returns:
            dict: 급여명세서 데이터
        """
        tax_free_items = tax_free_items or {}
        
        # 일할계산 적용
        if work_days and month_days and work_days < month_days:
            base_salary = int(base_salary * (work_days / month_days))
            # 수당도 일할 계산
            allowances = {k: int(v * (work_days / month_days)) for k, v in allowances.items()}
            tax_free_items = {k: int(v * (work_days / month_days)) for k, v in tax_free_items.items()}
        
        # 고정 OT 수당 추가
        if fixed_ot_amount > 0:
            if '연장근로수당' not in allowances:
                allowances['연장근로수당'] = fixed_ot_amount
        
        # 총 지급액 계산
        total_allowance = sum(allowances.values())
        total_salary = base_salary + total_allowance
        
        # 비과세 합계
        total_tax_free = sum(tax_free_items.values())
        
        # 과세 대상 급여
        taxable_salary = total_salary - total_tax_free
        
        # 4대보험 계산 (적용 여부에 따라)
        pension = self.calculate_national_pension(taxable_salary) if apply_pension else {"근로자부담": 0, "사업주부담": 0}
        health = self.calculate_health_insurance(taxable_salary) if apply_health else {
            "건강보험": {"근로자부담": 0, "사업주부담": 0},
            "장기요양": {"근로자부담": 0, "사업주부담": 0}
        }
        if not apply_longterm and apply_health:
            health["장기요양"] = {"근로자부담": 0, "사업주부담": 0}
        employment = self.calculate_employment_insurance(taxable_salary) if apply_employment else {"근로자부담": 0, "사업주부담": 0}
        
        # 소득세 및 지방세 (본인 1명 기준)
        income_tax = self.calculate_income_tax_simple(taxable_salary, 1, 0)
        local_tax = math.floor(income_tax * C.LOCAL_TAX_RATE)
        
        # 총 공제액
        total_deduction = (
            pension["근로자부담"] +
            health["건강보험"]["근로자부담"] +
            health["장기요양"]["근로자부담"] +
            employment["근로자부담"] +
            income_tax +
            local_tax
        )
        
        # 실수령액
        net_pay = total_salary - total_deduction
        
        return {
            "기본급": base_salary,
            "수당": allowances,
            "총수당": total_allowance,
            "총지급액": total_salary,
            "비과세": tax_free_items,
            "총비과세": total_tax_free,
            "과세급여": taxable_salary,
            "국민연금": pension["근로자부담"],
            "건강보험": health["건강보험"]["근로자부담"],
            "장기요양": health["장기요양"]["근로자부담"],
            "고용보험": employment["근로자부담"],
            "소득세": income_tax,
            "지방세": local_tax,
            "총공제": total_deduction,
            "실수령액": net_pay,
            "일할계산": {
                "적용": bool(work_days and month_days and work_days < month_days),
                "근무일수": work_days,
                "월총일수": month_days
            } if work_days and month_days else None,
            "상세": {
                "국민연금": pension,
                "건강보험": health,
                "고용보험": employment
            }
        }


class AnnualLeaveCalculator:
    """연차 계산"""
    
    @staticmethod
    def calculate_annual_leave_days(hire_date: datetime) -> int:
        """
        입사일 기준 연차 발생 일수 계산
        
        Args:
            hire_date: 입사일
        
        Returns:
            int: 연차 발생 일수
        """
        today = datetime.now()
        work_period = (today - hire_date).days
        work_years = work_period / 365.25
        
        if work_years < 1:
            # 1년 미만: 월 1개씩 발생
            return int(work_years * 12)
        elif work_years < 3:
            # 1년 이상 ~ 3년 미만: 15개
            return 15
        else:
            # 3년 이상: 2년마다 1개 추가 (최대 25개)
            additional = int((work_years - 1) / 2)
            return min(15 + additional, 25)
    
    @staticmethod
    def calculate_unused_leave_pay(
        unused_days: int,
        daily_wage: float
    ) -> float:
        """
        미사용 연차 수당 계산
        
        Args:
            unused_days: 미사용 연차 일수
            daily_wage: 일 통상임금
        
        Returns:
            float: 미사용 연차 수당
        """
        return unused_days * daily_wage


def calculate_hourly_wage(
    base_pay: float, 
    meal_allowance: float = 0,
    monthly_hours: float = None
) -> float:
    """
    통상시급 계산 (통상임금 기준)
    
    Args:
        base_pay: 월 기본급
        meal_allowance: 식대 (통상임금에 포함)
        monthly_hours: 월 근로시간 (기본값: COMMON_WAGE_DIVISOR)
    
    Returns:
        float: 통상시급
    """
    if monthly_hours is None:
        monthly_hours = C.COMMON_WAGE_DIVISOR
    
    # 통상임금 = 기본급 + 식대
    common_wage = base_pay + meal_allowance
    
    # 통상시급 = 통상임금 / 월 소정근로시간
    return common_wage / monthly_hours


def calculate_overtime_pay(
    base_pay: float,
    meal_allowance: float,
    overtime_hours: float,
    overtime_type: str = "연장",
    monthly_hours: float = None
) -> float:
    """
    연장근로수당 계산
    
    Args:
        base_pay: 월 기본급
        meal_allowance: 식대 (통상임금에 포함)
        overtime_hours: 연장근로 시간
        overtime_type: "연장", "야간", "휴일"
        monthly_hours: 월 근로시간 (기본값: COMMON_WAGE_DIVISOR)
    
    Returns:
        float: 연장근로수당
    """
    if monthly_hours is None:
        monthly_hours = C.COMMON_WAGE_DIVISOR
    
    # 통상시급 계산 (기본급 + 식대)
    hourly_wage = calculate_hourly_wage(base_pay, meal_allowance, monthly_hours)
    
    # 가산율 결정
    if overtime_type == "연장":
        rate = C.OVERTIME_RATE
    elif overtime_type == "야간":
        rate = C.WORK_TIME["야간근로"]["가산율"]
    elif overtime_type == "휴일":
        if overtime_hours <= 8:
            rate = C.WORK_TIME["휴일근로"]["가산율"]
        else:
            rate = C.WORK_TIME["휴일근로"]["초과가산율"]
    else:
        rate = 1.0
    
    # 연장근로수당 = 통상시급 × 연장근로시간 × 가산율
    return hourly_wage * overtime_hours * rate


def calculate_ot_hours_from_pay(
    base_pay: float,
    meal_allowance: float,
    overtime_pay: float,
    overtime_type: str = "연장",
    monthly_hours: float = None
) -> float:
    """
    연장근로수당 금액으로부터 연장근로시간 역산
    
    Args:
        base_pay: 월 기본급
        meal_allowance: 식대 (통상임금에 포함)
        overtime_pay: 연장근로수당 금액
        overtime_type: "연장", "야간", "휴일"
        monthly_hours: 월 근로시간 (기본값: COMMON_WAGE_DIVISOR)
    
    Returns:
        float: 연장근로시간 (소수점 첫째 자리 반올림)
    """
    if monthly_hours is None:
        monthly_hours = C.COMMON_WAGE_DIVISOR
    
    # 통상시급 계산 (기본급 + 식대)
    hourly_wage = calculate_hourly_wage(base_pay, meal_allowance, monthly_hours)
    
    # 가산율 결정
    if overtime_type == "연장":
        rate = C.OVERTIME_RATE
    elif overtime_type == "야간":
        rate = C.WORK_TIME["야간근로"]["가산율"]
    elif overtime_type == "휴일":
        # 휴일은 8시간 기준으로 나누어 계산 (단순화)
        rate = C.WORK_TIME["휴일근로"]["가산율"]
    else:
        rate = 1.0
    
    # 역산: 연장근로시간 = 연장근로수당 / (통상시급 × 가산율)
    if hourly_wage == 0 or rate == 0:
        return 0.0
    
    hours = overtime_pay / (hourly_wage * rate)
    
    # 소수점 첫째 자리 반올림
    return round(hours, 1)


def validate_working_hours(
    regular_hours: float,
    overtime_hours: float,
    week_or_month: str = "week"
) -> Dict[str, any]:
    """
    근로시간 법정 검증 (주 52시간 초과 여부)
    
    Args:
        regular_hours: 정규 근로시간
        overtime_hours: 연장 근로시간
        week_or_month: "week" (주간) 또는 "month" (월간)
    
    Returns:
        dict: 검증 결과
    """
    total_hours = regular_hours + overtime_hours
    
    if week_or_month == "week":
        max_regular = C.WORK_TIME["법정근로시간"]["주"]
        max_overtime = C.WORK_TIME["연장근로"]["주최대"]
        max_total = C.WORK_TIME["법정근로시간"]["주최대"]
    else:  # month
        max_regular = C.WORK_TIME["법정근로시간"]["월"]
        max_overtime = C.WORK_TIME["연장근로"]["주최대"] * 4.345  # 주 12시간 × 월 평균 주수
        max_total = max_regular + max_overtime
    
    is_valid = total_hours <= max_total
    is_overtime_valid = overtime_hours <= max_overtime
    
    return {
        "정규근로": regular_hours,
        "연장근로": overtime_hours,
        "총근로시간": total_hours,
        "법정한도": max_total,
        "적법여부": is_valid and is_overtime_valid,
        "경고메시지": [] if (is_valid and is_overtime_valid) else [
            f"⚠️ 주 52시간 초과 (총 {total_hours}시간)" if not is_valid else "",
            f"⚠️ 연장근로 한도 초과 ({overtime_hours}시간)" if not is_overtime_valid else ""
        ],
        "법적근거": "근로기준법 제50조(근로시간), 제53조(연장근로)"
    }


def validate_minimum_wage(
    monthly_salary: float,
    monthly_hours: float
) -> Dict[str, any]:
    """
    최저임금 준수 검증
    
    Args:
        monthly_salary: 월 급여
        monthly_hours: 월 근로시간
    
    Returns:
        dict: 검증 결과
    """
    hourly_wage = monthly_salary / monthly_hours
    min_hourly = C.MINIMUM_WAGE["시급"]
    min_monthly = C.MINIMUM_WAGE["월급"]
    
    is_valid_hourly = hourly_wage >= min_hourly
    is_valid_monthly = monthly_salary >= min_monthly
    
    return {
        "월급여": monthly_salary,
        "월근로시간": monthly_hours,
        "시간급": round(hourly_wage, 0),
        "최저시급": min_hourly,
        "최저월급": min_monthly,
        "적법여부": is_valid_hourly and is_valid_monthly,
        "경고메시지": [] if (is_valid_hourly and is_valid_monthly) else [
            f"⚠️ 최저시급 미달 (현재: {hourly_wage:,.0f}원, 최저: {min_hourly:,}원)" if not is_valid_hourly else "",
            f"⚠️ 최저월급 미달 (현재: {monthly_salary:,.0f}원, 최저: {min_monthly:,}원)" if not is_valid_monthly else ""
        ],
        "법적근거": "최저임금법 제6조(최저임금의 효력)"
    }


def format_payslip(payroll_data: Dict[str, any]) -> str:
    """
    급여명세서 텍스트 포맷팅
    
    Args:
        payroll_data: 급여 데이터
    
    Returns:
        str: 포맷팅된 급여명세서
    """
    return f"""
    ═══════════════════════════════════════
                급 여 명 세 서
    ═══════════════════════════════════════
    
    ▶ 지급 내역
      - 기본급:        {C.format_currency(payroll_data['기본급'])}
      - 수당 합계:     {C.format_currency(payroll_data['총수당'])}
      ─────────────────────────────────────
      총 지급액:       {C.format_currency(payroll_data['총지급액'])}
    
    ▶ 공제 내역
      - 국민연금:      {C.format_currency(payroll_data['국민연금'])}
      - 건강보험:      {C.format_currency(payroll_data['건강보험'])}
      - 장기요양:      {C.format_currency(payroll_data['장기요양'])}
      - 고용보험:      {C.format_currency(payroll_data['고용보험'])}
      - 소득세:        {C.format_currency(payroll_data['소득세'])}
      - 지방소득세:    {C.format_currency(payroll_data['지방세'])}
      ─────────────────────────────────────
      총 공제액:       {C.format_currency(payroll_data['총공제'])}
    
    ═══════════════════════════════════════
      실수령액:        {C.format_currency(payroll_data['실수령액'])}
    ═══════════════════════════════════════
    """
