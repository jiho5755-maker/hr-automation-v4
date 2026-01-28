"""
통합 DB 기반 직원 데이터 관리 모듈
기존 employee_manager.py를 대체하는 중앙 DB 연동 버전
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import date, datetime, timedelta

# shared 모듈 import
sys.path.append(str(Path(__file__).parent.parent))
from shared.database import (
    get_all_employees,
    get_employee_by_id,
    get_employee_by_name,
    add_employee,
    update_employee,
    get_company_profile
)


class SharedEmployeeDataManager:
    """
    통합 DB 기반 직원 데이터 관리 클래스
    기존 EmployeeDataManager와 동일한 인터페이스 제공
    """
    
    def __init__(self):
        """초기화"""
        pass
    
    def get_all_employee_names(self) -> List[str]:
        """모든 직원 이름 목록 조회"""
        employees = get_all_employees(active_only=True)
        return [emp['name'] for emp in employees]
    
    def load_employee(self, name: str) -> Optional[Dict]:
        """
        직원 데이터 로드 (기존 JSON 형식으로 변환)
        
        Args:
            name: 직원 이름
            
        Returns:
            기존 JSON 형식의 직원 데이터
        """
        employee = get_employee_by_name(name)
        if not employee:
            return None
        
        # 기존 JSON 형식으로 변환
        return self._convert_to_json_format(employee)
    
    def save_employee(self, employee_data: Dict) -> bool:
        """
        직원 데이터 저장
        
        Args:
            employee_data: 직원 데이터 (JSON 형식)
            
        Returns:
            저장 성공 여부
        """
        try:
            # JSON 형식 → DB 형식 변환
            db_format = self._convert_from_json_format(employee_data)
            
            # 기존 직원 확인
            emp_id = db_format.get('emp_id')
            existing = get_employee_by_id(emp_id) if emp_id else None
            
            if existing:
                # 업데이트
                return update_employee(emp_id, db_format)
            else:
                # 새로 추가
                add_employee(db_format)
                return True
                
        except Exception as e:
            print(f"저장 실패: {e}")
            return False
    
    def delete_employee(self, name: str) -> bool:
        """
        직원 데이터 삭제 (소프트 삭제)
        
        Args:
            name: 직원 이름
            
        Returns:
            삭제 성공 여부
        """
        from shared.database import delete_employee as db_delete_employee
        
        employee = get_employee_by_name(name)
        if not employee:
            return False
        
        return db_delete_employee(employee['emp_id'], hard_delete=False)
    
    def _convert_to_json_format(self, db_data: Dict) -> Dict:
        """
        DB 형식 → 기존 JSON 형식 변환
        
        Args:
            db_data: DB에서 가져온 직원 데이터
            
        Returns:
            JSON 형식의 직원 데이터
        """
        import json
        
        # 회사 정보
        company = get_company_profile()
        
        # notes 필드에서 날짜 정보 파싱
        date_info = {}
        if db_data.get('notes'):
            try:
                date_info = json.loads(db_data['notes'])
            except:
                pass
        
        # pregnancy_dates에서 정보 추출
        pregnancy_dates = date_info.get('pregnancy_dates', {})
        maternity = date_info.get('maternity', {})
        parental_leave = date_info.get('parental_leave', {})
        replacement = date_info.get('replacement', {})
        
        # 날짜 문자열을 date 객체로 변환하는 함수
        def parse_date(date_str):
            if date_str:
                try:
                    return datetime.strptime(date_str, "%Y-%m-%d").date()
                except:
                    pass
            return None
        
        json_data = {
            "EMPLOYEE_INFO": {
                "이름": db_data.get('name', ''),
                "주민등록번호": db_data.get('resident_number') or '',
                "연락처": db_data.get('phone') or db_data.get('contact') or '',
                "부서": db_data.get('department', ''),
                "직급": db_data.get('position', '')
            },
            "EMPLOYER_INFO": {
                "회사명": company.get('company_name', '') if company else '',
                "사업자등록번호": company.get('business_number', '') if company else '',
                "대표자명": company.get('ceo_name', '') if company else '',
                "회사규모": f"{company.get('employee_count', 0)}명" if company else '',
                "주소": company.get('location', '') if company else '',
                "연매출": company.get('annual_revenue', 0) if company else 0
            },
            "PREGNANCY_SHORT_WORK": {
                "단축근무_실시여부": "예" if db_data.get('is_pregnant') else "아니오",
                "시작일": parse_date(pregnancy_dates.get('short_work_start')),
                "종료일": parse_date(pregnancy_dates.get('short_work_end')),
                "근무시간": {
                    "시작": pregnancy_dates.get('work_start_time', '10:00'),
                    "종료": pregnancy_dates.get('work_end_time', '18:00'),
                    "휴게시간": "12:00-13:00",
                    "실근로시간": pregnancy_dates.get('work_hours', 7)
                },
                "1일_단축시간": 8 - pregnancy_dates.get('work_hours', 7)
            },
            "CHILDBIRTH_INFO": {
                "출산예정일": parse_date(pregnancy_dates.get('expected_delivery')),
                "출산(예정)일": parse_date(pregnancy_dates.get('expected_delivery')),
                "임신확인일": parse_date(pregnancy_dates.get('confirmed')),
                "출산휴가_시작일": parse_date(maternity.get('start')),
                "출산휴가_종료일": parse_date(maternity.get('end')),
                "출산휴가_일수": maternity.get('days', 90),
                "출산_자녀수": 1,
                "다태아_여부": maternity.get('is_multiple', False)
            },
            "PARENTAL_LEAVE": {
                "육아휴직_사용여부": "예" if db_data.get('is_on_leave') else "아니오",
                "시작일": parse_date(parental_leave.get('start')),
                "종료일": parse_date(parental_leave.get('end')),
                "기간_개월": parental_leave.get('months', 12)
            },
            "REPLACEMENT_WORKER": {
                "대체인력_고용여부": "예" if replacement.get('hire_date') else "아니오",
                "채용일": parse_date(replacement.get('hire_date')),
                "인수인계_시작일": parse_date(replacement.get('handover_start')),
                "인수인계_종료일": parse_date(replacement.get('handover_end')),
                "인수인계_일수": replacement.get('handover_days', 0)
            }
        }
        
        return json_data
    
    def _convert_from_json_format(self, json_data: Dict) -> Dict:
        """
        JSON 형식 → DB 형식 변환
        
        Args:
            json_data: JSON 형식의 직원 데이터
            
        Returns:
            DB 형식의 직원 데이터
        """
        emp_info = json_data.get('EMPLOYEE_INFO', {})
        pregnancy_info = json_data.get('PREGNANCY_SHORT_WORK', {})
        parental_info = json_data.get('PARENTAL_LEAVE', {})
        
        # 주민등록번호에서 emp_id 생성
        resident_num = emp_info.get('주민등록번호', '')
        emp_id = resident_num[:6] if resident_num else f"EMP{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 성별 추출
        gender = None
        if len(resident_num) > 7:
            gender_code = resident_num[7]
            gender = '남성' if gender_code in ['1', '3'] else '여성' if gender_code in ['2', '4'] else None
        
        db_data = {
            'emp_id': emp_id,
            'name': emp_info.get('이름'),
            'resident_number': resident_num,
            'department': emp_info.get('부서'),
            'position': emp_info.get('직급'),
            'gender': gender,
            'is_pregnant': pregnancy_info.get('단축근무_실시여부') == '예',
            'is_on_leave': parental_info.get('육아휴직_사용여부') == '예',
            'created_by': 'maternity_app'
        }
        
        return db_data


# 기존 코드와의 호환성을 위한 래퍼
def create_employee_data_from_form(form_data: Dict) -> Dict:
    """
    폼 데이터를 직원 데이터 형식으로 변환
    (기존 함수와 동일한 인터페이스 유지)
    """
    return form_data
