#!/usr/bin/env python3
"""
데이터 마이그레이션 스크립트
Migration Script: JSON → SQLite Database

employees_data.json 파일의 직원 데이터를 hr_master.db로 마이그레이션합니다.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.database import (
    init_master_database, 
    get_db, 
    get_employee_by_name,
    add_employee
)


def load_json_data(json_path):
    """JSON 파일에서 직원 데이터 로드"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ JSON 파일 로드 완료: {len(data)}명")
        return data
    except FileNotFoundError:
        print(f"❌ JSON 파일을 찾을 수 없습니다: {json_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파일 파싱 오류: {e}")
        return None


def migrate_employee(employee_data):
    """단일 직원 데이터 마이그레이션"""
    try:
        name = employee_data.get('name')
        
        # 이미 존재하는지 확인
        existing = get_employee_by_name(name)
        if existing:
            print(f"  ⏩ 건너뜀: {name} (이미 존재)")
            return 'skipped'
        
        # 데이터 변환
        migrated_data = {
            'name': name,
            'department': employee_data.get('department'),
            'position': employee_data.get('position', '직원'),
            'hire_date': employee_data.get('hire_date'),
            'resident_number': employee_data.get('resident_number'),
            'gender': employee_data.get('gender'),
            'age': employee_data.get('age'),
            'email': employee_data.get('email'),
            'phone': employee_data.get('phone'),
            'is_pregnant': employee_data.get('is_pregnant', False),
            'is_on_leave': employee_data.get('is_on_leave', False),
            'is_youth': employee_data.get('is_youth', False),
            'is_disabled': employee_data.get('is_disabled', False),
            'notes': employee_data.get('notes'),
            'created_by': 'migration_script'
        }
        
        # DB에 추가
        emp_id = add_employee(migrated_data)
        
        if emp_id:
            print(f"  ✅ 마이그레이션 완료: {name} (ID: {emp_id})")
            return 'success'
        else:
            print(f"  ❌ 마이그레이션 실패: {name}")
            return 'failed'
    
    except Exception as e:
        print(f"  ❌ 오류 발생: {name} - {str(e)}")
        return 'error'


def main():
    """메인 마이그레이션 함수"""
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📦 데이터 마이그레이션: JSON → SQLite Database")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("")
    
    # Step 1: 데이터베이스 초기화
    print("🗄️  Step 1: 데이터베이스 초기화...")
    init_master_database()
    print("  ✅ 데이터베이스 준비 완료")
    print("")
    
    # Step 2: JSON 파일 로드
    print("📂 Step 2: JSON 파일 로드...")
    json_path = project_root / "1_출산육아_자동화" / "employees_data.json"
    
    employees_data = load_json_data(json_path)
    
    if not employees_data:
        print("❌ 마이그레이션 중단: JSON 파일 로드 실패")
        return
    
    print("")
    
    # Step 3: 마이그레이션 실행
    print("🔄 Step 3: 마이그레이션 실행...")
    print("")
    
    results = {
        'success': 0,
        'skipped': 0,
        'failed': 0,
        'error': 0
    }
    
    total = len(employees_data)
    
    for i, emp_data in enumerate(employees_data, 1):
        print(f"[{i}/{total}] {emp_data.get('name', 'Unknown')}:")
        result = migrate_employee(emp_data)
        results[result] += 1
    
    print("")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 마이그레이션 결과")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ 성공: {results['success']}명")
    print(f"⏩ 건너뜀 (이미 존재): {results['skipped']}명")
    print(f"❌ 실패: {results['failed']}명")
    print(f"⚠️  오류: {results['error']}명")
    print(f"📦 총 처리: {total}명")
    print("")
    
    # Step 4: 검증
    print("🔍 Step 4: 마이그레이션 검증...")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees")
        db_count = cursor.fetchone()[0]
    
    print(f"  DB에 저장된 직원 수: {db_count}명")
    
    expected_count = results['success'] + results['skipped']
    if db_count >= expected_count:
        print("  ✅ 검증 성공: 데이터 건수 일치")
    else:
        print(f"  ⚠️  검증 경고: 예상 {expected_count}명, 실제 {db_count}명")
    
    print("")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✨ 마이그레이션 완료!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("")
    print("📝 다음 단계:")
    print("  1. python3 scripts/verify_migration.py (상세 검증)")
    print("  2. 통합 대시보드에서 직원 목록 확인")
    print("  3. employees_data.json 백업 후 제거 (선택)")
    print("")


if __name__ == "__main__":
    main()
