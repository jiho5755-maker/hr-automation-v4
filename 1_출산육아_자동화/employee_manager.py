"""
직원 데이터 관리 모듈
JSON 파일을 사용하여 여러 직원의 데이터를 저장하고 불러오기
"""

import json
import os
from datetime import date, datetime
from typing import Dict, List, Optional
from pathlib import Path


class EmployeeDataManager:
    """직원 데이터 관리 클래스"""
    
    def __init__(self, data_file: str = "employees_data.json"):
        """
        Args:
            data_file: 직원 데이터를 저장할 JSON 파일 경로
        """
        self.data_file = Path(data_file)
        self.employees = self._load_all_employees()
    
    def _load_all_employees(self) -> Dict:
        """모든 직원 데이터 로드"""
        if not self.data_file.exists():
            return {}
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 날짜 문자열을 date 객체로 변환
                for emp_name, emp_data in data.items():
                    emp_data = self._convert_str_to_date(emp_data)
                    data[emp_name] = emp_data
                return data
        except Exception as e:
            print(f"데이터 로드 실패: {e}")
            return {}
    
    def _convert_str_to_date(self, data: Dict) -> Dict:
        """JSON에서 로드한 날짜 문자열을 date 객체로 변환"""
        date_fields = [
            "PREGNANCY_SHORT_WORK.시작일",
            "PREGNANCY_SHORT_WORK.종료일",
            "CHILDBIRTH_INFO.임신확인일",
            "CHILDBIRTH_INFO.출산예정일",
            "CHILDBIRTH_INFO.출산휴가_시작일",
            "CHILDBIRTH_INFO.출산휴가_종료일",
            "PARENTAL_LEAVE.시작일",
            "PARENTAL_LEAVE.종료일",
            "REPLACEMENT_WORKER.채용일",
            "REPLACEMENT_WORKER.인수인계_시작일",
            "REPLACEMENT_WORKER.인수인계_종료일",
        ]
        
        for field in date_fields:
            parts = field.split('.')
            if len(parts) == 2:
                section, key = parts
                if section in data and key in data[section]:
                    date_str = data[section][key]
                    if isinstance(date_str, str):
                        try:
                            data[section][key] = datetime.strptime(date_str, "%Y-%m-%d").date()
                        except:
                            pass
        
        return data
    
    def _convert_date_to_str(self, data: Dict) -> Dict:
        """date 객체를 문자열로 변환 (JSON 저장용)"""
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self._convert_date_to_str(value)
            elif isinstance(value, date):
                result[key] = value.strftime("%Y-%m-%d")
            else:
                result[key] = value
        return result
    
    def save_employee(self, employee_data: Dict) -> bool:
        """
        직원 데이터 저장
        
        Args:
            employee_data: 저장할 직원 데이터
            
        Returns:
            성공 여부
        """
        try:
            employee_name = employee_data["EMPLOYEE_INFO"]["이름"]
            
            # 기존 데이터 로드
            all_data = self._load_all_employees()
            
            # 새 데이터 추가
            all_data[employee_name] = employee_data
            
            # JSON으로 변환 (날짜를 문자열로)
            json_data = {}
            for name, data in all_data.items():
                json_data[name] = self._convert_date_to_str(data)
            
            # 파일에 저장
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            # 메모리 업데이트
            self.employees = all_data
            
            return True
        except Exception as e:
            print(f"저장 실패: {e}")
            return False
    
    def load_employee(self, employee_name: str) -> Optional[Dict]:
        """
        특정 직원 데이터 로드
        
        Args:
            employee_name: 직원 이름
            
        Returns:
            직원 데이터 또는 None
        """
        return self.employees.get(employee_name)
    
    def delete_employee(self, employee_name: str) -> bool:
        """
        직원 데이터 삭제
        
        Args:
            employee_name: 삭제할 직원 이름
            
        Returns:
            성공 여부
        """
        try:
            if employee_name in self.employees:
                del self.employees[employee_name]
                
                # JSON으로 변환하여 저장
                json_data = {}
                for name, data in self.employees.items():
                    json_data[name] = self._convert_date_to_str(data)
                
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                
                return True
            return False
        except Exception as e:
            print(f"삭제 실패: {e}")
            return False
    
    def get_all_employee_names(self) -> List[str]:
        """모든 직원 이름 목록 반환"""
        return list(self.employees.keys())
    
    def employee_exists(self, employee_name: str) -> bool:
        """직원 데이터 존재 여부 확인"""
        return employee_name in self.employees


def create_employee_data_from_form(
    # 직원 정보
    name: str,
    ssn: str,
    phone: str,
    department: str,
    position: str,
    # 사업주 정보
    employer_name: str,
    company_name: str,
    business_number: str,
    company_size: str,
    # 임신 단축근무
    short_work_start: date,
    short_work_end: date,
    work_start_time: str,
    work_end_time: str,
    work_break_time: str,
    actual_work_hours: int,
    # 출산 정보
    pregnancy_confirm_date: date,
    due_date: date,
    maternity_leave_start: date,
    maternity_leave_end: date,
    maternity_leave_days: int,
    # 육아 휴직
    parental_leave_start: date,
    parental_leave_end: date,
    parental_leave_months: int,
    # 대체 인력
    replacement_hire_date: date,
    handover_start: date,
    handover_end: date,
    handover_days: int,
) -> Dict:
    """
    폼 입력값으로부터 직원 데이터 생성
    
    Returns:
        완전한 직원 데이터 딕셔너리
    """
    return {
        "EMPLOYEE_INFO": {
            "이름": name,
            "주민등록번호": ssn,
            "연락처": phone,
            "부서": department,
            "직급": position,
        },
        "EMPLOYER_INFO": {
            "대표자명": employer_name,
            "회사명": company_name,
            "사업자등록번호": business_number,
            "회사규모": company_size,
        },
        "PREGNANCY_SHORT_WORK": {
            "시작일": short_work_start,
            "종료일": short_work_end,
            "근무시간": {
                "시작": work_start_time,
                "종료": work_end_time,
                "휴게시간": work_break_time,
                "실근로시간": actual_work_hours,
            }
        },
        "CHILDBIRTH_INFO": {
            "임신확인일": pregnancy_confirm_date,
            "출산예정일": due_date,
            "출산휴가_시작일": maternity_leave_start,
            "출산휴가_종료일": maternity_leave_end,
            "출산휴가_일수": maternity_leave_days,
        },
        "PARENTAL_LEAVE": {
            "시작일": parental_leave_start,
            "종료일": parental_leave_end,
            "기간_개월": parental_leave_months,
        },
        "REPLACEMENT_WORKER": {
            "채용일": replacement_hire_date,
            "인수인계_시작일": handover_start,
            "인수인계_종료일": handover_end,
            "인수인계_일수": handover_days,
        }
    }
