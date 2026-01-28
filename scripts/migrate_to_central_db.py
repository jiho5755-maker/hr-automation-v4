#!/usr/bin/env python3
"""
데이터 마이그레이션: 개별 DB → 중앙 통합 DB
Migration Script: Individual DBs → Central hr_master.db

기존 개별 앱의 데이터를 중앙 통합 DB로 이전합니다.
"""

import sys
from pathlib import Path
import json
import sqlite3
from datetime import datetime

# 상위 디렉토리의 shared 모듈 import
sys.path.append(str(Path(__file__).parent.parent))
from shared.database import (
    add_employee, 
    update_employee,
    get_employee_by_id,
    update_company_profile,
    get_company_profile,
    add_system_log
)


def migrate_from_maternity_json():
    """
    1_출산육아_자동화/employees_data.json → 중앙 DB
    """
    print("\n" + "="*60)
    print("📋 출산육아 앱 데이터 마이그레이션 (JSON)")
    print("="*60)
    
    json_file = Path(__file__).parent.parent / "1_출산육아_자동화/employees_data.json"
    
    if not json_file.exists():
        print("⚠️  employees_data.json 파일이 없습니다.")
        return 0
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        success_count = 0
        fail_count = 0
        
        for name, emp_data in data.items():
            try:
                emp_info = emp_data.get('EMPLOYEE_INFO', {})
                pregnancy_info = emp_data.get('PREGNANCY_SHORT_WORK', {})
                
                # 주민등록번호에서 emp_id 생성
                resident_num = emp_info.get('주민등록번호', '')
                emp_id = resident_num[:6] if resident_num else f"EMP{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # 성별 추출 (주민등록번호 뒷자리 첫 번째)
                gender = None
                if len(resident_num) > 7:
                    gender_code = resident_num[7]
                    gender = '남성' if gender_code in ['1', '3'] else '여성' if gender_code in ['2', '4'] else None
                
                employee = {
                    'emp_id': emp_id,
                    'name': name,
                    'resident_number': resident_num,
                    'department': emp_info.get('부서'),
                    'position': emp_info.get('직급'),
                    'gender': gender,
                    'is_pregnant': pregnancy_info.get('단축근무_실시여부') == '예',
                    'is_on_leave': False,
                    'created_by': 'migration_json'
                }
                
                # 중복 확인
                existing = get_employee_by_id(emp_id)
                
                if existing:
                    # 업데이트
                    if update_employee(emp_id, employee):
                        print(f"✅ {name} - 업데이트 완료")
                        success_count += 1
                    else:
                        print(f"❌ {name} - 업데이트 실패")
                        fail_count += 1
                else:
                    # 새로 추가
                    add_employee(employee)
                    print(f"✅ {name} - 추가 완료")
                    success_count += 1
                    
            except Exception as e:
                print(f"❌ {name} - 실패: {e}")
                fail_count += 1
        
        print(f"\n📊 결과: 성공 {success_count}명, 실패 {fail_count}명")
        return success_count
        
    except Exception as e:
        print(f"❌ JSON 파일 읽기 실패: {e}")
        return 0


def migrate_from_work_logs_db():
    """
    3_재택근무_관리시스템/work_logs.db → 중앙 DB
    """
    print("\n" + "="*60)
    print("🏠 재택근무 앱 데이터 마이그레이션 (SQLite)")
    print("="*60)
    
    db_file = Path(__file__).parent.parent / "3_재택근무_관리시스템/work_logs.db"
    
    if not db_file.exists():
        print("⚠️  work_logs.db 파일이 없습니다.")
        return 0
    
    try:
        conn = sqlite3.connect(str(db_file))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # employees 테이블 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
        if not cursor.fetchone():
            print("⚠️  employees 테이블이 없습니다.")
            conn.close()
            return 0
        
        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()
        
        success_count = 0
        fail_count = 0
        
        for emp in employees:
            try:
                emp_dict = dict(emp)  # Row를 dict로 변환
                employee = {
                    'emp_id': emp_dict['emp_id'],
                    'name': emp_dict['name'],
                    'department': emp_dict.get('department'),
                    'position': emp_dict.get('position'),
                    'email': emp_dict.get('email'),
                    'phone': emp_dict.get('phone'),
                    'hire_date': emp_dict.get('hire_date'),
                    'is_active': emp_dict.get('is_active', 1),
                    'created_by': 'migration_work_logs'
                }
                
                # 중복 확인
                existing = get_employee_by_id(employee['emp_id'])
                
                if existing:
                    # 기존 데이터와 병합 (기존 데이터 우선)
                    for key, value in employee.items():
                        if value and not existing.get(key):
                            existing[key] = value
                    
                    if update_employee(employee['emp_id'], existing):
                        print(f"✅ {emp_dict['name']} - 업데이트 완료")
                        success_count += 1
                    else:
                        print(f"❌ {emp_dict['name']} - 업데이트 실패")
                        fail_count += 1
                else:
                    # 새로 추가
                    add_employee(employee)
                    print(f"✅ {emp_dict['name']} - 추가 완료")
                    success_count += 1
                    
            except Exception as e:
                print(f"❌ {emp_dict.get('name', 'Unknown')} - 실패: {e}")
                fail_count += 1
        
        conn.close()
        print(f"\n📊 결과: 성공 {success_count}명, 실패 {fail_count}명")
        return success_count
        
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")
        return 0


def migrate_from_subsidy_db():
    """
    4_정부지원금_자동화/hr_automation.db → 중앙 DB
    """
    print("\n" + "="*60)
    print("💼 정부지원금 앱 데이터 마이그레이션 (SQLite)")
    print("="*60)
    
    db_file = Path(__file__).parent.parent / "4_정부지원금_자동화/hr_automation.db"
    
    if not db_file.exists():
        print("⚠️  hr_automation.db 파일이 없습니다.")
        return 0
    
    try:
        conn = sqlite3.connect(str(db_file))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        success_count = 0
        fail_count = 0
        
        # employees 테이블 마이그레이션
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
        if cursor.fetchone():
            cursor.execute("SELECT * FROM employees")
            employees = cursor.fetchall()
            
            for emp in employees:
                try:
                    emp_dict = dict(emp)  # Row를 dict로 변환
                    employee = {
                        'emp_id': emp_dict.get('emp_id'),
                        'name': emp_dict.get('name'),
                        'resident_number': emp_dict.get('resident_number'),
                        'department': emp_dict.get('department'),
                        'position': emp_dict.get('position'),
                        'hire_date': emp_dict.get('hire_date'),
                        'gender': emp_dict.get('gender'),
                        'age': emp_dict.get('age'),
                        'is_youth': emp_dict.get('is_youth', 0),
                        'is_disabled': emp_dict.get('is_disabled', 0),
                        'created_by': 'migration_subsidy'
                    }
                    
                    # 중복 확인
                    existing = get_employee_by_id(employee['emp_id'])
                    
                    if existing:
                        # 병합 (기존 데이터 우선)
                        for key, value in employee.items():
                            if value and not existing.get(key):
                                existing[key] = value
                        
                        if update_employee(employee['emp_id'], existing):
                            print(f"✅ {emp_dict.get('name')} - 업데이트 완료")
                            success_count += 1
                        else:
                            print(f"❌ {emp_dict.get('name')} - 업데이트 실패")
                            fail_count += 1
                    else:
                        add_employee(employee)
                        print(f"✅ {emp_dict.get('name')} - 추가 완료")
                        success_count += 1
                        
                except Exception as e:
                    print(f"❌ {emp_dict.get('name', 'Unknown')} - 실패: {e}")
                    fail_count += 1
        
        # company_info 테이블 마이그레이션
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_info'")
        if cursor.fetchone():
            cursor.execute("SELECT * FROM company_info ORDER BY id DESC LIMIT 1")
            company = cursor.fetchone()
            
            if company:
                existing_company = get_company_profile()
                
                if not existing_company:
                    company_data = {
                        'company_name': company.get('company_name'),
                        'business_number': company.get('business_number'),
                        'ceo_name': company.get('ceo_name'),
                        'business_type': company.get('business_type'),
                        'employee_count': company.get('employee_count'),
                        'annual_revenue': company.get('annual_revenue'),
                        'location': company.get('address'),
                    }
                    
                    update_company_profile(company_data)
                    print(f"✅ 회사 정보 마이그레이션 완료")
        
        conn.close()
        print(f"\n📊 결과: 성공 {success_count}명, 실패 {fail_count}명")
        return success_count
        
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")
        return 0


def main():
    """메인 함수"""
    print("="*60)
    print("🔄 데이터 마이그레이션 시작")
    print("개별 DB → 중앙 통합 DB (hr_master.db)")
    print("="*60)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_count = 0
    
    # 1. 출산육아 JSON 마이그레이션
    total_count += migrate_from_maternity_json()
    
    # 2. 재택근무 DB 마이그레이션
    total_count += migrate_from_work_logs_db()
    
    # 3. 정부지원금 DB 마이그레이션
    total_count += migrate_from_subsidy_db()
    
    # 완료
    print("\n" + "="*60)
    print("✅ 마이그레이션 완료!")
    print("="*60)
    print(f"총 {total_count}명의 직원 데이터가 중앙 DB로 이전되었습니다.")
    print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 시스템 로그
    add_system_log(
        'migration_script',
        f'데이터 마이그레이션 완료',
        'data_migration',
        f'총 {total_count}명 이전 완료'
    )
    
    print("\n💡 다음 단계:")
    print("1. 중앙 DB 데이터 확인")
    print("2. 개별 앱을 중앙 DB 연동으로 수정")
    print("3. 기존 로컬 DB 백업 후 보관")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
