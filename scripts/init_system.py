"""
시스템 초기화 스크립트
Initialize HR Automation System

기본 사용자 및 샘플 데이터 생성
"""

import sys
from pathlib import Path

# 상위 디렉토리의 shared 모듈 import
sys.path.append(str(Path(__file__).parent.parent))
from shared.database import init_master_database, get_db, update_company_profile
from shared.auth import create_user, get_user_by_username


def create_default_users():
    """기본 사용자 생성"""
    print("\n👤 기본 사용자 생성 중...")
    
    # Admin 사용자
    if not get_user_by_username('admin'):
        if create_user('admin', 'admin1234', role='admin'):
            print("  ✅ 관리자 계정 생성 완료")
            print("     ID: admin, PW: admin1234")
        else:
            print("  ❌ 관리자 계정 생성 실패")
    else:
        print("  ℹ️  관리자 계정이 이미 존재합니다")
    
    # Test 사용자
    if not get_user_by_username('test'):
        if create_user('test', 'test1234', role='employee'):
            print("  ✅ 테스트 계정 생성 완료")
            print("     ID: test, PW: test1234")
        else:
            print("  ❌ 테스트 계정 생성 실패")
    else:
        print("  ℹ️  테스트 계정이 이미 존재합니다")


def create_sample_company():
    """샘플 회사 정보 생성"""
    print("\n🏢 회사 정보 생성 중...")
    
    company_data = {
        'company_name': '(주)예시회사',
        'ceo_name': '이진선',
        'business_number': '123-45-67890',
        'business_type': 'IT서비스업',
        'employee_count': 25,
        'annual_revenue': 500000000,
        'location': '서울시 강남구',
        'is_priority_support': 1,
        'situations': ['청년고용', '출산육아지원'],
        'employee_stats': {
            'total': 25,
            'youth': 15,
            'female': 10,
            'pregnant': 2
        }
    }
    
    update_company_profile(company_data)
    print("  ✅ 회사 정보 생성 완료")


def create_sample_employees():
    """샘플 직원 생성"""
    print("\n👥 샘플 직원 생성 중...")
    
    employees = [
        ('EMP001', '송미', '디자인 기획팀', '대리', None, '여성', 35, 1, 0, 0, 0),
        ('EMP002', '김민지', '개발팀', '주임', None, '여성', 27, 0, 0, 1, 0),
        ('EMP003', '이준호', '마케팅팀', '과장', None, '남성', 32, 0, 0, 1, 0),
    ]
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        for emp in employees:
            try:
                cursor.execute("""
                INSERT OR IGNORE INTO employees 
                (emp_id, name, department, position, resident_number, gender, age,
                 is_pregnant, is_on_leave, is_youth, is_disabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, emp)
            except Exception as e:
                print(f"  ⚠️  {emp[1]} 생성 실패: {e}")
        
        conn.commit()
    
    print("  ✅ 샘플 직원 3명 생성 완료")


def main():
    """메인 함수"""
    print("=" * 60)
    print("🚀 인사팀 자동화 시스템 초기화")
    print("=" * 60)
    
    # 1. 데이터베이스 초기화
    print("\n📦 데이터베이스 초기화 중...")
    init_master_database()
    
    # 2. 기본 사용자 생성
    create_default_users()
    
    # 3. 회사 정보 생성
    create_sample_company()
    
    # 4. 샘플 직원 생성
    create_sample_employees()
    
    print("\n" + "=" * 60)
    print("✅ 시스템 초기화 완료!")
    print("=" * 60)
    print("\n💡 다음 단계:")
    print("   1. 통합 대시보드 실행:")
    print("      cd 0_통합_대시보드")
    print("      streamlit run app.py --server.port 8000")
    print()
    print("   2. 로그인 정보:")
    print("      관리자: admin / admin1234")
    print("      테스트: test / test1234")
    print()


if __name__ == "__main__":
    main()
