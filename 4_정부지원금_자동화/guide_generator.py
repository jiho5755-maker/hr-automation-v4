"""
스마트 가이드 생성기
서식 작성에 필요한 데이터를 자동으로 판단하고 가이드 제공
"""

from typing import Dict, List, Any, Optional
from datetime import date


class SmartGuideGenerator:
    """스마트 가이드 생성기"""
    
    # 서식별 필드 정의
    FORM_SCHEMAS = {
        "임신기_근로시간_단축_신청서": {
            "fields": [
                {"name": "이름", "type": "text", "source": "employee", "required": True},
                {"name": "주민등록번호", "type": "text", "source": "employee", "required": True},
                {"name": "부서", "type": "text", "source": "employee", "required": True},
                {"name": "직급", "type": "text", "source": "employee", "required": True},
                {"name": "출산예정일", "type": "date", "source": "manual", "required": True,
                 "description": "병원에서 확인한 출산 예정일을 입력하세요"},
                {"name": "단축근무_시작일", "type": "date", "source": "manual", "required": True,
                 "description": "근로시간 단축을 시작할 날짜"},
                {"name": "단축근무_종료일", "type": "date", "source": "manual", "required": True,
                 "description": "근로시간 단축이 종료되는 날짜"},
                {"name": "근무시간_시작", "type": "time", "source": "manual", "required": True,
                 "description": "단축 후 근무 시작 시각 (예: 11:00)"},
                {"name": "근무시간_종료", "type": "time", "source": "manual", "required": True,
                 "description": "단축 후 근무 종료 시각 (예: 18:00)"},
                {"name": "대표자명", "type": "text", "source": "company", "required": True},
            ],
            "attachments": [
                {
                    "name": "임신확인 진단서",
                    "description": "병원에서 발급받은 임신 확인 진단서 (임신 주수 명시 필수)",
                    "format": "PDF 또는 이미지",
                    "required": True
                }
            ]
        },
        "임신사유_근로시간_단축_확인서": {
            "fields": [
                {"name": "이름", "type": "text", "source": "employee", "required": True},
                {"name": "주민등록번호", "type": "text", "source": "employee", "required": True},
                {"name": "연락처", "type": "text", "source": "employee", "required": True},
                {"name": "임신확인일", "type": "date", "source": "manual", "required": True,
                 "description": "임신 확인 진단서 발급일"},
                {"name": "단축근무_시작일", "type": "date", "source": "manual", "required": True},
                {"name": "단축근무_종료일", "type": "date", "source": "manual", "required": True},
                {"name": "대표자명", "type": "text", "source": "company", "required": True},
            ],
            "attachments": []
        },
        "대체인력_지원금_신청서": {
            "fields": [
                {"name": "회사명", "type": "text", "source": "company", "required": True},
                {"name": "대표자명", "type": "text", "source": "company", "required": True},
                {"name": "사업자등록번호", "type": "text", "source": "company", "required": True},
                {"name": "휴직자_이름", "type": "text", "source": "employee", "required": True},
                {"name": "휴직_시작일", "type": "date", "source": "manual", "required": True,
                 "description": "출산휴가 또는 육아휴직 시작일"},
                {"name": "휴직_종료일", "type": "date", "source": "manual", "required": True,
                 "description": "출산휴가 또는 육아휴직 종료 예정일"},
                {"name": "대체인력_이름", "type": "text", "source": "manual", "required": True,
                 "description": "채용한 대체인력의 이름"},
                {"name": "대체인력_채용일", "type": "date", "source": "manual", "required": True,
                 "description": "대체인력을 채용한 날짜"},
            ],
            "attachments": [
                {
                    "name": "대체인력 근로계약서",
                    "description": "채용한 대체인력의 근로계약서 사본",
                    "format": "PDF",
                    "required": True
                },
                {
                    "name": "휴직 확인서",
                    "description": "휴직자의 휴직 확인서",
                    "format": "PDF",
                    "required": True
                },
                {
                    "name": "4대보험 가입 확인서",
                    "description": "대체인력의 4대보험 가입 확인서",
                    "format": "PDF",
                    "required": True
                }
            ]
        }
    }
    
    def __init__(self, subsidy: Dict, employee_db: Dict, company_db: Dict):
        self.subsidy = subsidy
        self.employee_db = employee_db
        self.company_db = company_db
    
    def generate_guide(self) -> Dict:
        """완전 자동화된 가이드 생성"""
        
        # 필요한 서식 판단
        required_forms = self._identify_required_forms()
        
        guide = {
            "subsidy_name": self.subsidy["name"],
            "subsidy_code": self.subsidy["code"],
            "forms": []
        }
        
        for form_name in required_forms:
            form_guide = self._generate_form_guide(form_name)
            guide["forms"].append(form_guide)
        
        return guide
    
    def _identify_required_forms(self) -> List[str]:
        """지원금에 필요한 서식 자동 판단"""
        # 지원금 코드나 카테고리에 따라 필요한 서식 결정
        subsidy_code = self.subsidy.get("code", "")
        category = self.subsidy.get("category", "")
        
        if "MOEL-001" in subsidy_code:  # 대체인력 지원금
            return ["대체인력_지원금_신청서"]
        elif "MOEL-002" in subsidy_code:  # 임신기 근로시간 단축
            return [
                "임신기_근로시간_단축_신청서",
                "임신사유_근로시간_단축_확인서"
            ]
        elif category == "출산육아":
            return [
                "임신기_근로시간_단축_신청서",
                "임신사유_근로시간_단축_확인서"
            ]
        
        return []
    
    def _generate_form_guide(self, form_name: str) -> Dict:
        """개별 서식 가이드 생성"""
        
        if form_name not in self.FORM_SCHEMAS:
            return {
                "form_name": form_name,
                "error": "서식 정보를 찾을 수 없습니다"
            }
        
        schema = self.FORM_SCHEMAS[form_name]
        
        guide = {
            "form_name": form_name,
            "display_name": self._get_display_name(form_name),
            "fields": [],
            "auto_filled": [],
            "need_input": [],
            "attachments": schema.get("attachments", [])
        }
        
        # 각 필드 분석
        for field in schema["fields"]:
            field_info = self._analyze_field(field)
            guide["fields"].append(field_info)
            
            if field_info["auto_filled"]:
                guide["auto_filled"].append(field_info)
            else:
                guide["need_input"].append(field_info)
        
        return guide
    
    def _analyze_field(self, field: Dict) -> Dict:
        """필드 분석: 자동 입력 가능 vs 사용자 입력 필요"""
        
        field_name = field["name"]
        source = field["source"]
        
        result = {
            "name": field_name,
            "type": field["type"],
            "required": field.get("required", False),
            "description": field.get("description", ""),
            "auto_filled": False,
            "value": None,
            "source_db": None
        }
        
        # 직원 DB에서 자동 입력
        if source == "employee":
            value = self.employee_db.get(field_name)
            if value:
                result["auto_filled"] = True
                result["value"] = value
                result["source_db"] = "직원 정보"
        
        # 회사 DB에서 자동 입력
        elif source == "company":
            value = self.company_db.get(field_name)
            if value:
                result["auto_filled"] = True
                result["value"] = value
                result["source_db"] = "회사 정보"
        
        return result
    
    def _get_display_name(self, form_name: str) -> str:
        """서식명을 사용자 친화적으로 변환"""
        display_names = {
            "임신기_근로시간_단축_신청서": "임신기 근로시간 단축 신청서",
            "임신사유_근로시간_단축_확인서": "임신사유 근로시간 단축 확인서 (근로자용)",
            "대체인력_지원금_신청서": "대체인력 지원금 신청서"
        }
        return display_names.get(form_name, form_name)
    
    def get_completion_percentage(self, guide: Dict) -> float:
        """서식 작성 완료율 계산"""
        total_fields = 0
        filled_fields = 0
        
        for form in guide.get("forms", []):
            total_fields += len(form.get("fields", []))
            filled_fields += len(form.get("auto_filled", []))
        
        if total_fields == 0:
            return 0.0
        
        return (filled_fields / total_fields) * 100


def test_guide_generator():
    """가이드 생성기 테스트"""
    
    # 테스트 데이터
    subsidy = {
        "code": "MOEL-002",
        "name": "임신기 근로시간 단축 지원금",
        "category": "출산육아"
    }
    
    employee_db = {
        "이름": "송미",
        "주민등록번호": "910828-2xxxxxx",
        "부서": "디자인 기획팀",
        "직급": "대리",
        "연락처": "010-1234-5678"
    }
    
    company_db = {
        "회사명": "(주)테스트회사",
        "대표자명": "이진선",
        "사업자등록번호": "123-45-67890"
    }
    
    generator = SmartGuideGenerator(subsidy, employee_db, company_db)
    guide = generator.generate_guide()
    
    print(f"\n📋 {guide['subsidy_name']} 가이드")
    print(f"필요한 서식: {len(guide['forms'])}개\n")
    
    for form in guide['forms']:
        print(f"\n📄 {form['display_name']}")
        
        if form.get('auto_filled'):
            print(f"  ✅ 자동 입력 ({len(form['auto_filled'])}개)")
            for field in form['auto_filled']:
                print(f"     • {field['name']}: {field['value']} (출처: {field['source_db']})")
        
        if form.get('need_input'):
            print(f"  📝 입력 필요 ({len(form['need_input'])}개)")
            for field in form['need_input']:
                print(f"     • {field['name']}: {field['description']}")
        
        if form.get('attachments'):
            print(f"  📎 첨부 서류 ({len(form['attachments'])}개)")
            for att in form['attachments']:
                req = "필수" if att['required'] else "선택"
                print(f"     • [{req}] {att['name']}")
    
    completion = generator.get_completion_percentage(guide)
    print(f"\n📊 자동 입력 완료율: {completion:.1f}%")


if __name__ == "__main__":
    test_guide_generator()
