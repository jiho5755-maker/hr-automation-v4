"""
스마트 지원금 크롤러
회사 프로필 기반으로 적합한 지원금만 자동 수집
"""

from typing import Dict, List, Optional
from datetime import datetime, date
import json
import time

# Optional imports (크롤링 기능은 패키지 설치 후 사용 가능)
try:
    import requests
    from bs4 import BeautifulSoup
    CRAWLING_AVAILABLE = True
except ImportError:
    CRAWLING_AVAILABLE = False
    print("⚠️  requests, beautifulsoup4 패키지가 설치되지 않았습니다.")
    print("   크롤링 기능을 사용하려면 다음 명령을 실행하세요:")
    print("   python3 -m pip install requests beautifulsoup4 --user")

from company_profile import CompanyProfile


class SmartSubsidyCrawler:
    """회사 맞춤형 지원금 크롤러"""
    
    def __init__(self, company_profile: CompanyProfile):
        self.profile = company_profile
        self.matched_subsidies = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def crawl_all_sources(self) -> List[Dict]:
        """모든 정부 사이트 크롤링"""
        print("🔍 정부 지원금 크롤링 시작...")
        
        all_subsidies = []
        
        # 1. 고용노동부
        print("  → 고용노동부 크롤링 중...")
        moel_subsidies = self._crawl_moel()
        all_subsidies.extend(moel_subsidies)
        
        # 2. 중소벤처기업부
        print("  → 중소벤처기업부 크롤링 중...")
        mss_subsidies = self._crawl_mss()
        all_subsidies.extend(mss_subsidies)
        
        # 3. 더미 데이터 (실제 크롤링 대신 임시)
        print("  → 로컬 지원금 DB 로드 중...")
        local_subsidies = self._load_local_database()
        all_subsidies.extend(local_subsidies)
        
        # 회사 프로필 기반 필터링
        print("  → 회사 프로필 기반 매칭 중...")
        matched = self._filter_by_company_profile(all_subsidies)
        
        print(f"✅ 총 {len(all_subsidies)}개 중 {len(matched)}개 매칭!")
        
        self.matched_subsidies = matched
        return matched
    
    def _crawl_moel(self) -> List[Dict]:
        """고용노동부 크롤링"""
        subsidies = []
        
        if not CRAWLING_AVAILABLE:
            return subsidies
        
        try:
            # TODO: 실제 크롤링 구현
            # 현재는 에러 없이 빈 리스트 반환
            pass
        except Exception as e:
            print(f"    ⚠️  고용노동부 크롤링 오류: {e}")
        
        return subsidies
    
    def _crawl_mss(self) -> List[Dict]:
        """중소벤처기업부 크롤링"""
        subsidies = []
        
        if not CRAWLING_AVAILABLE:
            return subsidies
        
        try:
            # TODO: 실제 크롤링 구현
            pass
        except Exception as e:
            print(f"    ⚠️  중소벤처기업부 크롤링 오류: {e}")
        
        return subsidies
    
    def _load_local_database(self) -> List[Dict]:
        """로컬 지원금 데이터베이스 로드"""
        # 현재는 하드코딩된 지원금 데이터
        return [
            {
                "code": "MOEL-001",
                "name": "출산전후휴가 대체인력 지원금",
                "category": "출산육아",
                "target": "사업주",
                "monthly_amount": 1_400_000,
                "max_months": 15,
                "company_size_requirement": "우선지원대상",
                "target_situations": ["출산육아"],
                "description": "출산전후휴가·육아휴직 사용 근로자의 업무를 대신할 대체인력 채용 시 지원",
                "deadline": "대체인력 채용일로부터 30일 이내",
                "application_url": "https://www.moel.go.kr",
                "contact": "고용노동부 고용센터 ☎1350",
                "required_documents": [
                    "대체인력 지원금 신청서",
                    "대체인력 근로계약서 사본",
                    "휴직자 휴직 확인서",
                    "4대보험 가입 확인서"
                ]
            },
            {
                "code": "MOEL-002",
                "name": "임신기 근로시간 단축 지원금 (위라밸일자리)",
                "category": "출산육아",
                "target": "사업주",
                "monthly_amount": 400_000,
                "max_months": 12,
                "company_size_requirement": "전체",
                "target_situations": ["출산육아"],
                "description": "임신 중인 여성 근로자의 근로시간을 1일 2시간 단축 시 지원",
                "deadline": "근로시간 단축 종료일로부터 3개월 이내",
                "application_url": "https://www.moel.go.kr",
                "contact": "고용노동부 고용센터 ☎1350",
                "required_documents": [
                    "임신기 근로시간 단축 신청서",
                    "임신사유 근로시간 단축 확인서",
                    "임신 확인 진단서",
                    "근로계약서 변경 확인서"
                ]
            },
            {
                "code": "MOEL-003",
                "name": "일자리 함께하기 지원금 (업무분담)",
                "category": "출산육아",
                "target": "사업주",
                "monthly_amount": 600_000,
                "max_months": 6,
                "company_size_requirement": "우선지원대상",
                "target_situations": ["출산육아"],
                "description": "출산휴가·육아휴직자의 업무를 기존 근로자에게 분담 시 지원",
                "deadline": "업무분담 시작일로부터 1개월 이내",
                "application_url": "https://www.moel.go.kr",
                "contact": "고용노동부 고용센터 ☎1350",
                "required_documents": [
                    "일자리 함께하기 지원금 신청서",
                    "업무분담 계획서",
                    "업무분담 확인서",
                    "보상금 지급 증빙"
                ]
            },
            {
                "code": "MOEL-004",
                "name": "청년 내일채움공제",
                "category": "청년고용",
                "target": "사업주",
                "monthly_amount": 0,
                "max_months": 24,
                "company_size_requirement": "우선지원대상",
                "target_situations": ["청년고용"],
                "description": "청년(15~34세) 정규직 채용 시 2년간 적립금 지원",
                "deadline": "청년 채용일로부터 6개월 이내",
                "application_url": "https://www.work.go.kr/naeillchaioom",
                "contact": "고용노동부 고용센터 ☎1350",
                "required_documents": [
                    "청년내일채움공제 참여신청서",
                    "근로계약서 사본",
                    "4대보험 가입확인서"
                ]
            },
            {
                "code": "MOEL-005",
                "name": "청년 일자리 도약장려금",
                "category": "청년고용",
                "target": "사업주",
                "monthly_amount": 800_000,
                "max_months": 12,
                "company_size_requirement": "우선지원대상",
                "target_situations": ["청년고용"],
                "description": "청년(15~34세) 정규직 신규 채용 시 1년간 인건비 지원",
                "deadline": "청년 채용일로부터 3개월 이내",
                "application_url": "https://www.work.go.kr",
                "contact": "고용노동부 고용센터 ☎1350",
                "required_documents": [
                    "청년일자리도약장려금 신청서",
                    "근로계약서 사본",
                    "임금대장"
                ]
            },
            {
                "code": "MSS-001",
                "name": "소상공인 일자리 안정자금",
                "category": "기업경영",
                "target": "사업주",
                "monthly_amount": 200_000,
                "max_months": 12,
                "company_size_requirement": "소상공인",
                "target_situations": [],
                "description": "30인 미만 소상공인의 인건비 부담 완화",
                "deadline": "매월 신청",
                "application_url": "https://www.sbiz.or.kr",
                "contact": "소상공인시장진흥공단 ☎1588-5302",
                "required_documents": [
                    "일자리안정자금 신청서",
                    "사업자등록증 사본",
                    "근로자 명부"
                ]
            }
        ]
    
    def _filter_by_company_profile(self, subsidies: List[Dict]) -> List[Dict]:
        """회사 프로필 기반 필터링"""
        matched = []
        
        for subsidy in subsidies:
            # 기업 규모 체크
            if not self._check_company_size(subsidy):
                continue
            
            # 상황 매칭 체크
            if not self._check_situation_match(subsidy):
                continue
            
            # 매칭 점수 계산
            match_score = self._calculate_match_score(subsidy)
            
            # 왜 매칭되었는지 설명
            why_matched = self._explain_match(subsidy)
            
            # 예상 금액 계산
            estimated_amount = self._estimate_amount(subsidy)
            
            matched.append({
                **subsidy,
                "match_score": match_score,
                "why_matched": why_matched,
                "estimated_amount": estimated_amount
            })
        
        # 매칭 점수 순으로 정렬
        matched.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matched
    
    def _check_company_size(self, subsidy: Dict) -> bool:
        """기업 규모 조건 체크"""
        required_size = subsidy.get("company_size_requirement", "전체")
        
        if required_size == "전체":
            return True
        elif required_size == "우선지원대상":
            return self.profile.is_priority_support
        elif required_size == "중소기업":
            return self.profile.employee_count < 1000
        elif required_size == "소상공인":
            return self.profile.employee_count < 10
        
        return True
    
    def _check_situation_match(self, subsidy: Dict) -> bool:
        """현재 상황 매칭"""
        required_situations = subsidy.get("target_situations", [])
        
        # 상황 조건이 없으면 모두 매칭
        if not required_situations:
            return True
        
        # 교집합이 있으면 매칭
        return bool(set(required_situations) & set(self.profile.situations))
    
    def _calculate_match_score(self, subsidy: Dict) -> float:
        """매칭 점수 계산 (0~100)"""
        score = 0
        
        # 기업 규모 완벽 매칭
        if self._check_company_size(subsidy):
            score += 30
        
        # 상황 매칭 개수
        required_situations = subsidy.get("target_situations", [])
        situation_matches = len(
            set(required_situations) & set(self.profile.situations)
        )
        score += situation_matches * 25
        
        # 예상 지원금액 (금액이 클수록 높은 점수)
        estimated = self._estimate_amount(subsidy)
        score += min(estimated / 200000, 45)
        
        return min(score, 100)
    
    def _explain_match(self, subsidy: Dict) -> List[str]:
        """왜 매칭되었는지 설명"""
        reasons = []
        
        # 기업 규모
        if self.profile.is_priority_support:
            if subsidy.get("company_size_requirement") == "우선지원대상":
                reasons.append("✓ 우선지원대상기업 요건 충족")
        
        # 상황 매칭
        required_situations = subsidy.get("target_situations", [])
        for situation in self.profile.situations:
            if situation in required_situations:
                reasons.append(f"✓ {situation} 관련 지원금")
        
        # 상황 조건 없음
        if not required_situations:
            reasons.append("✓ 모든 기업 신청 가능")
        
        return reasons
    
    def _estimate_amount(self, subsidy: Dict) -> int:
        """예상 수령액 계산"""
        monthly = subsidy.get("monthly_amount", 0)
        months = subsidy.get("max_months", 1)
        
        return monthly * months


def test_crawler():
    """크롤러 테스트"""
    # 테스트용 회사 프로필
    profile = CompanyProfile({
        "company_name": "테스트 회사",
        "business_type": "서비스업",
        "employee_count": 25,
        "is_priority_support": True,
        "situations": ["출산육아", "청년고용"]
    })
    
    crawler = SmartSubsidyCrawler(profile)
    results = crawler.crawl_all_sources()
    
    print(f"\n📊 매칭 결과: {len(results)}개")
    for i, subsidy in enumerate(results[:5], 1):
        print(f"\n{i}. {subsidy['name']}")
        print(f"   매칭도: {subsidy['match_score']:.0f}%")
        print(f"   예상 금액: {subsidy['estimated_amount']:,}원")
        for reason in subsidy['why_matched']:
            print(f"   {reason}")


if __name__ == "__main__":
    test_crawler()
