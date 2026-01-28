"""
회사 프로필 관리 시스템
회사 정보를 저장하고 지원금 매칭에 활용
"""

import json
from datetime import date
from typing import Dict, List, Optional
from pathlib import Path


class CompanyProfile:
    """회사 프로필"""
    
    def __init__(self, data: Optional[Dict] = None):
        if data:
            self.load_from_dict(data)
        else:
            # 기본값
            self.company_name = ""
            self.business_type = ""
            self.employee_count = 0
            self.annual_revenue = 0
            self.location = ""
            self.is_priority_support = False
            self.situations = []
            self.employees = {
                "total": 0,
                "youth_under_34": 0,
                "women": 0,
                "disabled": 0,
                "pregnant": 0,
                "on_leave": 0
            }
    
    def load_from_dict(self, data: Dict):
        """딕셔너리에서 로드"""
        self.company_name = data.get("company_name", "")
        self.business_type = data.get("business_type", "")
        self.employee_count = data.get("employee_count", 0)
        self.annual_revenue = data.get("annual_revenue", 0)
        self.location = data.get("location", "")
        self.is_priority_support = data.get("is_priority_support", False)
        self.situations = data.get("situations", [])
        self.employees = data.get("employees", {
            "total": 0,
            "youth_under_34": 0,
            "women": 0,
            "disabled": 0,
            "pregnant": 0,
            "on_leave": 0
        })
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            "company_name": self.company_name,
            "business_type": self.business_type,
            "employee_count": self.employee_count,
            "annual_revenue": self.annual_revenue,
            "location": self.location,
            "is_priority_support": self.is_priority_support,
            "situations": self.situations,
            "employees": self.employees
        }
    
    def check_priority_support(self) -> bool:
        """우선지원대상기업 자동 판단"""
        criteria = {
            "제조업": 500,
            "광업": 300,
            "건설업": 300,
            "운수창고통신업": 300,
            "도소매업": 200,
            "숙박음식점업": 200,
            "금융보험업": 100,
            "서비스업": 100
        }
        
        limit = criteria.get(self.business_type, 100)
        self.is_priority_support = self.employee_count < limit
        return self.is_priority_support
    
    def add_situation(self, situation: str):
        """현재 상황 추가"""
        if situation not in self.situations:
            self.situations.append(situation)
    
    def remove_situation(self, situation: str):
        """상황 제거"""
        if situation in self.situations:
            self.situations.remove(situation)


class CompanyProfileManager:
    """회사 프로필 저장/로드 관리"""
    
    PROFILE_FILE = "company_profile.json"
    
    @staticmethod
    def save_profile(profile: CompanyProfile) -> bool:
        """프로필 저장"""
        try:
            file_path = Path(__file__).parent / CompanyProfileManager.PROFILE_FILE
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"프로필 저장 실패: {e}")
            return False
    
    @staticmethod
    def load_profile() -> Optional[CompanyProfile]:
        """프로필 로드"""
        try:
            file_path = Path(__file__).parent / CompanyProfileManager.PROFILE_FILE
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return CompanyProfile(data)
        except Exception as e:
            print(f"프로필 로드 실패: {e}")
            return None
    
    @staticmethod
    def profile_exists() -> bool:
        """프로필 존재 여부"""
        file_path = Path(__file__).parent / CompanyProfileManager.PROFILE_FILE
        return file_path.exists()


# 미리 정의된 업종 목록
BUSINESS_TYPES = [
    "제조업",
    "광업",
    "건설업",
    "운수창고통신업",
    "도소매업",
    "숙박음식점업",
    "금융보험업",
    "서비스업",
    "출판영상방송통신정보서비스업",
    "전문과학기술서비스업",
    "사업시설관리사업지원서비스업",
    "교육서비스업",
    "보건업사회복지서비스업",
    "예술스포츠여가서비스업"
]

# 가능한 현재 상황 목록
SITUATION_OPTIONS = [
    "출산육아",
    "청년고용",
    "장애인고용",
    "고령자고용",
    "외국인고용",
    "단시간근로자고용",
    "일자리나누기",
    "교육훈련",
    "R&D",
    "스마트공장"
]
