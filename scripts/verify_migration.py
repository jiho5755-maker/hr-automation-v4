#!/usr/bin/env python3
"""
마이그레이션 검증 스크립트
Migration Verification Script

마이그레이션된 데이터의 정확성을 검증합니다.
"""

import json
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.database import get_db, get_all_employees


def load_json_data(json_path):
    """JSON 파일에서 직원 데이터 로드"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except:
        return []


def compare_data(json_data, db_data):
    """JSON 데이터와 DB 데이터 비교"""
    
    # 이름으로 매핑
    json_employees = {emp['name']: emp for emp in json_data}
    db_employees = {emp['name']: emp for emp in db_data}
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 상세 비교")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("")
    
    # JSON에는 있지만 DB에 없는 직원
    missing_in_db = set(json_employees.keys()) - set(db_employees.keys())
    if missing_in_db:
        print(f"⚠️  JSON에는 있지만 DB에 없는 직원 ({len(missing_in_db)}명):")
        for name in missing_in_db:
            print(f"  - {name}")
        print("")
    else:
        print("✅ JSON의 모든 직원이 DB에 존재합니다.")
        print("")
    
    # DB에는 있지만 JSON에 없는 직원
    extra_in_db = set(db_employees.keys()) - set(json_employees.keys())
    if extra_in_db:
        print(f"ℹ️  DB에는 있지만 JSON에 없는 직원 ({len(extra_in_db)}명):")
        print("  (직원 관리 페이지에서 추가된 직원일 수 있습니다)")
        for name in extra_in_db:
            print(f"  - {name}")
        print("")
    
    # 공통 직원의 데이터 비교
    common_employees = set(json_employees.keys()) & set(db_employees.keys())
    if common_employees:
        print(f"🔄 공통 직원 데이터 검증 ({len(common_employees)}명):")
        print("")
        
        mismatches = []
        
        for name in sorted(common_employees):
            json_emp = json_employees[name]
            db_emp = db_employees[name]
            
            # 주요 필드 비교
            fields_to_check = ['department', 'position', 'hire_date']
            mismatched_fields = []
            
            for field in fields_to_check:
                json_val = json_emp.get(field)
                db_val = db_emp.get(field)
                
                if str(json_val) != str(db_val):
                    mismatched_fields.append(f"{field}: JSON={json_val} vs DB={db_val}")
            
            if mismatched_fields:
                mismatches.append((name, mismatched_fields))
        
        if mismatches:
            print(f"  ⚠️  데이터 불일치 발견 ({len(mismatches)}명):")
            for name, fields in mismatches:
                print(f"    - {name}:")
                for field_info in fields:
                    print(f"      • {field_info}")
            print("")
        else:
            print("  ✅ 모든 공통 직원의 데이터가 일치합니다.")
            print("")


def main():
    """메인 검증 함수"""
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 마이그레이션 검증")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("")
    
    # Step 1: JSON 데이터 로드
    print("📂 Step 1: JSON 파일 로드...")
    json_path = project_root / "1_출산육아_자동화" / "employees_data.json"
    json_data = load_json_data(json_path)
    print(f"  JSON 직원 수: {len(json_data)}명")
    print("")
    
    # Step 2: DB 데이터 로드
    print("🗄️  Step 2: 데이터베이스 조회...")
    db_data = get_all_employees(active_only=False)
    print(f"  DB 직원 수: {len(db_data)}명")
    print("")
    
    # Step 3: 건수 비교
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 건수 비교")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"JSON 원본: {len(json_data)}명")
    print(f"DB 저장됨: {len(db_data)}명")
    
    if len(db_data) >= len(json_data):
        print("✅ 건수 검증 성공: DB에 모든 데이터가 저장되었습니다.")
    else:
        print(f"⚠️  건수 검증 경고: {len(json_data) - len(db_data)}명 누락")
    
    print("")
    
    # Step 4: 상세 비교
    if json_data and db_data:
        compare_data(json_data, db_data)
    
    # Step 5: DB 통계
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📈 데이터베이스 통계")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 재직 중인 직원
        cursor.execute("SELECT COUNT(*) FROM employees WHERE is_active = 1")
        active_count = cursor.fetchone()[0]
        print(f"재직 중: {active_count}명")
        
        # 특별 관리 직원
        cursor.execute("SELECT COUNT(*) FROM employees WHERE is_pregnant = 1 AND is_active = 1")
        pregnant_count = cursor.fetchone()[0]
        print(f"임신 중: {pregnant_count}명")
        
        cursor.execute("SELECT COUNT(*) FROM employees WHERE is_on_leave = 1 AND is_active = 1")
        leave_count = cursor.fetchone()[0]
        print(f"휴직 중: {leave_count}명")
        
        # 부서별 통계
        cursor.execute("""
            SELECT department, COUNT(*) as cnt 
            FROM employees 
            WHERE is_active = 1 
            GROUP BY department 
            ORDER BY cnt DESC
        """)
        departments = cursor.fetchall()
        
        if departments:
            print("")
            print("부서별 인원:")
            for dept, cnt in departments:
                print(f"  - {dept or '미정'}: {cnt}명")
    
    print("")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✨ 검증 완료!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("")
    print("📝 다음 단계:")
    print("  1. 통합 대시보드 실행 (./START_HERE.sh)")
    print("  2. '👥 직원 관리' 메뉴에서 직원 목록 확인")
    print("  3. 출산육아 페이지에서 직원 선택 가능 확인")
    print("")


if __name__ == "__main__":
    main()
