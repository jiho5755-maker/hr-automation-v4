"""
TAX-EASY AI - PDF 스마트 파서
국세청 간소화 PDF를 읽어 데이터를 자동으로 추출합니다.
"""

import pdfplumber
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import json


@dataclass
class ParsedData:
    """파싱된 데이터"""
    medical_expenses: List[Dict] = None
    medical_total: int = 0  # 의료비 총액
    insurance_reimbursement: int = 0  # 실손의료보험금 수령액
    insurance: List[Dict] = None
    card_usage: Dict = None
    donations: List[Dict] = None
    education: List[Dict] = None
    jeonse_loan_repayment: int = 0  # 전세자금 대출 상환액
    housing_subscription: int = 0  # 주택청약저축 납입액
    raw_text: str = ""
    
    def __post_init__(self):
        if self.medical_expenses is None:
            self.medical_expenses = []
        if self.insurance is None:
            self.insurance = []
        if self.card_usage is None:
            self.card_usage = {
                'credit_card': 0,
                'debit_card': 0,
                'traditional_market': 0,
                'public_transport': 0,
                'books_culture': 0
            }
        if self.donations is None:
            self.donations = []
        if self.education is None:
            self.education = []


class TaxPDFParser:
    """국세청 연말정산 간소화 PDF 파서"""
    
    def __init__(self):
        self.parsed_data = ParsedData()
    
    def parse_pdf(self, pdf_path: str) -> ParsedData:
        """
        PDF 파일을 읽어서 데이터 추출
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            ParsedData: 파싱된 데이터
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                self.parsed_data.raw_text = full_text
                
                # 각 항목별 파싱
                self._parse_medical_expenses(full_text)
                self._parse_insurance_reimbursement(full_text)
                self._parse_insurance(full_text)
                self._parse_card_usage(full_text)
                self._parse_donations(full_text)
                self._parse_education(full_text)
                self._parse_housing(full_text)
                
            return self.parsed_data
        
        except Exception as e:
            raise Exception(f"PDF 파싱 오류: {str(e)}")
    
    def _parse_medical_expenses(self, text: str):
        """의료비 파싱 - 실손의료보험금과 의료비 지출내역 모두 파싱"""
        amount_pattern = r'(\d{1,3}(?:,\d{3})*)'
        lines = text.split('\n')
        
        # 1. 의료비 지출액 찾기 - "의료비 인별합계금액" 라인
        medical_expense = 0
        for line in lines:
            if '의료비 인별합계금액' in line:
                amounts = re.findall(amount_pattern, line)
                if amounts:
                    try:
                        amount = int(amounts[-1].replace(',', ''))
                        if amount > 1000:
                            medical_expense = amount
                            break
                    except ValueError:
                        continue
        
        # 2. 실손의료보험금 찾기 - "[실손의료보험금]" 섹션의 "인별합계금액" 라인
        insurance_reimbursement = 0
        if '실손의료보험금' in text:
            # 실손의료보험금 섹션 찾기
            insurance_start = text.find('[실손의료보험금]')
            if insurance_start == -1:
                insurance_start = text.find('실손의료보험금')
            
            insurance_end = text.find('건강보험료', insurance_start)
            if insurance_end == -1:
                insurance_end = text.find('고용보험료', insurance_start)
            if insurance_end == -1:
                insurance_end = len(text)
            
            insurance_section = text[insurance_start:insurance_end]
            insurance_lines = insurance_section.split('\n')
            
            for line in insurance_lines:
                # "인별합계금액" 라인 (의료비가 아닌)
                if '인별합계금액' in line and '의료비' not in line:
                    amounts = re.findall(amount_pattern, line)
                    if amounts:
                        try:
                            amount = int(amounts[-1].replace(',', ''))
                            if amount > 1000:
                                insurance_reimbursement = amount
                                break
                        except ValueError:
                            continue
        
        # 3. 결과 저장
        if medical_expense > 0:
            self.parsed_data.medical_expenses.append({
                'institution': '의료비 총 지출액',
                'amount': medical_expense,
                'insurance_reimbursement': insurance_reimbursement
            })
        
        # 실손보험금만 있는 경우도 저장
        if insurance_reimbursement > 0 and medical_expense == 0:
            self.parsed_data.medical_expenses.append({
                'institution': '실손의료보험금',
                'amount': 0,
                'insurance_reimbursement': insurance_reimbursement
            })
        
        # 의료비 인별합계금액을 찾지 못한 경우, 개별 항목 파싱
        if medical_expense == 0:
            for line in lines:
                # 사업자번호 패턴이 있는 라인 (의료기관)
                if re.search(r'\*\*-\d{2}-\d{2}\*\*\*', line) or re.search(r'\d{3}-\d{2}-\d{5}', line):
                    amounts = re.findall(amount_pattern, line)
                    if amounts:
                        try:
                            amount = int(amounts[-1].replace(',', ''))
                            if amount > 1000:
                                # 의료기관명 추출 (사업자번호 앞부분)
                                institution = line.split('**')[0].strip() if '**' in line else line[:30].strip()
                                self.parsed_data.medical_expenses.append({
                                    'institution': institution,
                                    'amount': amount,
                                    'insurance_reimbursement': 0
                                })
                        except ValueError:
                            continue
    
    def _parse_insurance_reimbursement(self, text: str):
        """실손의료보험금 파싱"""
        # 실손의료보험금 섹션 찾기
        reimbursement_section = self._extract_section(text, "[실손의료보험금]", "[국민연금")
        if not reimbursement_section:
            reimbursement_section = self._extract_section(text, "실손의료보험금", "국민연금")
        if not reimbursement_section:
            reimbursement_section = self._extract_section(text, "실손의료보험금", "건강보험료")
        
        if not reimbursement_section:
            return
        
        amount_pattern = r'(\d{1,3}(?:,\d{3})*)'
        lines = reimbursement_section.split('\n')
        
        # '인별합계금액' 찾기
        for line in lines:
            if '인별합계금액' in line or ('합계금액' in line and '수령금액' in reimbursement_section[:reimbursement_section.find(line)+500]):
                amounts = re.findall(amount_pattern, line)
                if amounts:
                    try:
                        amount = int(amounts[-1].replace(',', ''))
                        if amount > 1000:
                            self.parsed_data.insurance_reimbursement = amount
                            break
                    except ValueError:
                        continue
    
    def _parse_insurance(self, text: str):
        """보험료 파싱 - 국세청 간소화 서비스 형식"""
        amount_pattern = r'(\d{1,3}(?:,\d{3})*)'
        lines = text.split('\n')
        
        # 1. 건강보험료 파싱
        health_section = self._extract_section(text, "[건강보험료]", "[고용보험료]")
        if not health_section:
            health_start = text.find("건강보험료")
            if health_start != -1:
                health_end = text.find("고용보험료", health_start)
                if health_end == -1:
                    health_end = text.find("국민연금", health_start)
                if health_end != -1:
                    health_section = text[health_start:health_end]
        
        if health_section:
            health_lines = health_section.split('\n')
            for line in health_lines:
                if '총합계' in line:
                    amounts = re.findall(amount_pattern, line)
                    if amounts:
                        try:
                            amount_str = amounts[-1].replace(',', '')
                            amount = int(amount_str)
                            if amount > 10000:
                                if not any(ins['type'] == '건강보험료' for ins in self.parsed_data.insurance):
                                    self.parsed_data.insurance.append({
                                        'type': '건강보험료',
                                        'amount': amount
                                    })
                                break
                        except (ValueError, IndexError):
                            continue
        
        # 2. 고용보험료 파싱
        employment_section = self._extract_section(text, "[고용보험료]", "[국민연금")
        if not employment_section:
            emp_start = text.find("고용보험료")
            if emp_start != -1:
                emp_end = text.find("국민연금", emp_start)
                if emp_end == -1:
                    emp_end = text.find("주택임차", emp_start)
                if emp_end != -1:
                    employment_section = text[emp_start:emp_end]
        
        if employment_section:
            emp_lines = employment_section.split('\n')
            for line in emp_lines:
                if '합계' in line and '고용보험료' in employment_section[:employment_section.find(line)]:
                    amounts = re.findall(amount_pattern, line)
                    if amounts:
                        try:
                            amount_str = amounts[-1].replace(',', '')
                            amount = int(amount_str)
                            if amount > 100:
                                if not any(ins['type'] == '고용보험료' for ins in self.parsed_data.insurance):
                                    self.parsed_data.insurance.append({
                                        'type': '고용보험료',
                                        'amount': amount
                                    })
                                break
                        except (ValueError, IndexError):
                            continue
        
        # 3. 국민연금보험료 파싱
        pension_section = self._extract_section(text, "[국민연금", "[주택임차")
        if not pension_section:
            pension_start = text.find("국민연금")
            if pension_start != -1:
                pension_end = text.find("주택임차", pension_start)
                if pension_end == -1:
                    pension_end = text.find("주택마련", pension_start)
                if pension_end != -1:
                    pension_section = text[pension_start:pension_end]
        
        if pension_section:
            pension_lines = pension_section.split('\n')
            found_pension_header = False
            for line in pension_lines:
                if '국민연금' in line and ('내역' in line or '보험료' in line):
                    found_pension_header = True
                elif found_pension_header and '합계' in line:
                    amounts = re.findall(amount_pattern, line)
                    if amounts:
                        try:
                            amount_str = amounts[-1].replace(',', '')
                            amount = int(amount_str)
                            if amount > 10000:
                                if not any(ins['type'] == '국민연금보험료' for ins in self.parsed_data.insurance):
                                    self.parsed_data.insurance.append({
                                        'type': '국민연금보험료',
                                        'amount': amount
                                    })
                                break
                        except (ValueError, IndexError):
                            continue
    
    def _parse_card_usage(self, text: str):
        """신용카드 사용액 파싱"""
        card_section = self._extract_section(text, "신용카드", "의료비")
        if not card_section:
            card_start = text.find("신용카드")
            if card_start == -1:
                card_start = text.find("카드 사용")
            if card_start != -1:
                card_end = text.find("의료비", card_start)
                if card_end == -1:
                    card_end = text.find("기부금", card_start)
                if card_end == -1:
                    card_end = len(text)
                card_section = text[card_start:card_end]
        
        if not card_section:
            return
        
        amount_pattern = r'(\d{1,3}(?:,\d{3})*)'
        lines = card_section.split('\n')
        
        # 합계 라인 찾기
        for line in lines:
            if '합계' in line or '총계' in line or '합 계' in line:
                amounts = re.findall(amount_pattern, line)
                if amounts:
                    amount_str = amounts[-1].replace(',', '')
                    try:
                        amount = int(amount_str)
                        if amount > 1000:
                            self.parsed_data.card_usage['credit_card'] = amount
                            break
                    except ValueError:
                        continue
    
    def _parse_donations(self, text: str):
        """기부금 파싱"""
        donation_section = self._extract_section(text, "기부금", "교육비")
        
        if not donation_section:
            return
        
        amount_pattern = r'(\d{1,3}(?:,\d{3})*)\s*원?'
        lines = donation_section.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ['기부', '후원', '종교', '법정', '지정']):
                amounts = re.findall(amount_pattern, line)
                if amounts:
                    amount_str = amounts[0].replace(',', '')
                    try:
                        amount = int(amount_str)
                        donation_type = '종교' if '종교' in line else '일반'
                        self.parsed_data.donations.append({
                            'type': donation_type,
                            'amount': amount,
                            'institution': line[:30].strip()
                        })
                    except ValueError:
                        continue
    
    def _parse_education(self, text: str):
        """교육비 파싱"""
        education_section = self._extract_section(text, "교육비", "연금")
        
        if not education_section:
            return
        
        amount_pattern = r'(\d{1,3}(?:,\d{3})*)\s*원?'
        lines = education_section.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ['대학교', '유치원', '어린이집', '초등학교', '중학교', '고등학교', '학원']):
                amounts = re.findall(amount_pattern, line)
                if amounts:
                    amount_str = amounts[0].replace(',', '')
                    try:
                        amount = int(amount_str)
                        
                        if '대학' in line:
                            education_level = '대학'
                        elif any(k in line for k in ['유치원', '어린이집']):
                            education_level = '취학전'
                        elif any(k in line for k in ['초등', '중학', '고등']):
                            education_level = '초중고'
                        else:
                            education_level = '기타'
                        
                        self.parsed_data.education.append({
                            'level': education_level,
                            'amount': amount,
                            'institution': line[:30].strip()
                        })
                    except ValueError:
                        continue
    
    def _parse_housing(self, text: str):
        """주택 관련 항목 파싱"""
        from housing_parser import parse_housing_data
        
        housing_data = parse_housing_data(text)
        
        if housing_data['jeonse_loan']['found']:
            self.parsed_data.jeonse_loan_repayment = housing_data['jeonse_loan']['total_repayment']
        
        if housing_data['housing_subscription']['found']:
            self.parsed_data.housing_subscription = housing_data['housing_subscription']['total_payment']
    
    def _extract_section(self, text: str, start_keyword: str, end_keyword: str) -> Optional[str]:
        """텍스트에서 특정 섹션 추출"""
        start_idx = text.find(start_keyword)
        if start_idx == -1:
            return None
        
        end_idx = text.find(end_keyword, start_idx)
        if end_idx == -1:
            return text[start_idx:]
        
        return text[start_idx:end_idx]
    
    def to_json(self) -> str:
        """파싱 결과를 JSON으로 변환"""
        data = {
            'medical_expenses': self.parsed_data.medical_expenses,
            'medical_total': self.parsed_data.medical_total,
            'insurance_reimbursement': self.parsed_data.insurance_reimbursement,
            'insurance': self.parsed_data.insurance,
            'card_usage': self.parsed_data.card_usage,
            'donations': self.parsed_data.donations,
            'education': self.parsed_data.education,
            'jeonse_loan': self.parsed_data.jeonse_loan_repayment,
            'housing_subscription': self.parsed_data.housing_subscription
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def export_summary(self) -> Dict:
        """요약 정보 추출"""
        # 의료비는 총액에서 실손보험금 차감
        net_medical = max(0, self.parsed_data.medical_total - self.parsed_data.insurance_reimbursement)
        
        total_insurance = sum(item['amount'] for item in self.parsed_data.insurance)
        total_card = sum(self.parsed_data.card_usage.values())
        total_donation = sum(item['amount'] for item in self.parsed_data.donations)
        total_education = sum(item['amount'] for item in self.parsed_data.education)
        
        return {
            'summary': {
                'medical_total': self.parsed_data.medical_total,
                'insurance_reimbursement': self.parsed_data.insurance_reimbursement,
                'net_medical': net_medical,
                'insurance_total': total_insurance,
                'card_total': total_card,
                'donation_total': total_donation,
                'education_total': total_education,
                'jeonse_loan': self.parsed_data.jeonse_loan_repayment,
                'housing_subscription': self.parsed_data.housing_subscription
            },
            'detail': {
                'medical_count': len(self.parsed_data.medical_expenses),
                'insurance_count': len(self.parsed_data.insurance),
                'donation_count': len(self.parsed_data.donations),
                'education_count': len(self.parsed_data.education),
                'insurance_types': [item['type'] for item in self.parsed_data.insurance]
            }
        }


def parse_tax_pdf(pdf_path: str) -> ParsedData:
    """간편한 PDF 파싱 함수"""
    parser = TaxPDFParser()
    return parser.parse_pdf(pdf_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        try:
            parser = TaxPDFParser()
            data = parser.parse_pdf(pdf_file)
            
            print("=" * 60)
            print("📄 PDF 파싱 완료!")
            print("=" * 60)
            
            summary = parser.export_summary()
            
            print(f"\n💰 의료비: {summary['summary']['medical_total']:,}원")
            print(f"   - 실손보험금: {summary['summary']['insurance_reimbursement']:,}원")
            print(f"   - 실제 공제 가능: {summary['summary']['net_medical']:,}원")
            print(f"🛡️ 보험료: {summary['summary']['insurance_total']:,}원 ({summary['detail']['insurance_count']}건)")
            print(f"💳 신용카드: {summary['summary']['card_total']:,}원")
            print(f"🏠 전세자금: {summary['summary']['jeonse_loan']:,}원")
            print(f"🏦 주택청약: {summary['summary']['housing_subscription']:,}원")
            
        except Exception as e:
            print(f"❌ 오류: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("사용법: python pdf_parser.py [PDF파일경로]")
