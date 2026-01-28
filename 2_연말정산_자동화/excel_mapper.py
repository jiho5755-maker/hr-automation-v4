"""
TAX-EASY AI - Excel 자동 매핑
파싱된 데이터를 4.근로소득세액공제신고서.xlsx에 자동으로 입력합니다.
"""

import openpyxl
from typing import Dict, List
import os


class ExcelMapper:
    """Excel 자동 매핑 클래스"""
    
    def __init__(self, template_path: str):
        """
        Args:
            template_path: Excel 템플릿 파일 경로
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {template_path}")
        
        self.workbook = openpyxl.load_workbook(template_path)
        self.sheet = self.workbook.active
    
    def map_basic_info(self, data: Dict):
        """기본 정보 입력"""
        # 예시 매핑 (실제 엑셀 파일에 맞게 조정 필요)
        pass
    
    def map_medical_expenses(self, medical_total: int, insurance_reimbursement: int):
        """의료비 입력"""
        # 실제 공제 가능 금액 계산
        net_medical = max(0, medical_total - insurance_reimbursement)
        # 엑셀 셀에 입력 (실제 셀 위치는 파일에 맞게 조정)
        # self.sheet['B10'] = net_medical
        pass
    
    def map_insurance(self, insurance_list: List[Dict]):
        """보험료 입력"""
        # 엑셀 셀에 입력
        pass
    
    def map_card_usage(self, card_data: Dict):
        """신용카드 사용액 입력"""
        # 엑셀 셀에 입력
        pass
    
    def map_housing(self, jeonse_loan: int, housing_subscription: int):
        """주택 관련 항목 입력"""
        # 엑셀 셀에 입력
        pass
    
    def save(self, output_path: str):
        """저장"""
        self.workbook.save(output_path)
        return output_path


def map_to_excel(parsed_data, template_path: str, output_path: str) -> str:
    """
    파싱된 데이터를 Excel에 자동으로 입력
    
    Args:
        parsed_data: ParsedData 객체
        template_path: 템플릿 파일 경로
        output_path: 출력 파일 경로
        
    Returns:
        str: 저장된 파일 경로
    """
    mapper = ExcelMapper(template_path)
    
    # 각 항목 매핑
    mapper.map_medical_expenses(
        parsed_data.medical_total,
        parsed_data.insurance_reimbursement
    )
    mapper.map_insurance(parsed_data.insurance)
    mapper.map_card_usage(parsed_data.card_usage)
    mapper.map_housing(
        parsed_data.jeonse_loan_repayment,
        parsed_data.housing_subscription
    )
    
    return mapper.save(output_path)
