"""
데이터 마이그레이션 스크립트
Migrate data from existing databases to integrated database

기존 DB들의 데이터를 통합 DB로 이전
"""

import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime

# 상위 디렉토리의 shared 모듈 import
sys.path.append(str(Path(__file__).parent.parent))
from shared.database import get_db, add_system_log


def migrate_from_remote_work_db():
    """
    재택근무 관리시스템 DB에서 마이그레이션
    - employees
    - users
    - work_logs
    """
    old_db_path = Path(__file__).parent.parent / "3_재택근무_관리시스템" / "work_logs.db"
    
    if not old_db_path.exists():
        print("⚠️  재택근무 DB 파일이 없습니다. 스킵합니다.")
        return 0
    
    print("\n📦 재택근무 DB 마이그레이션 시작...")
    
    old_conn = sqlite3.connect(str(old_db_path))
    old_conn.row_factory = sqlite3.Row
    old_cursor = old_conn.cursor()
    
    count = 0
    
    with get_db() as new_conn:
        new_cursor = new_conn.cursor()
        
        # 1. Employees 마이그레이션
        try:
            old_cursor.execute("SELECT * FROM employees WHERE is_active = 1")
            employees = old_cursor.fetchall()
            
            for emp in employees:
                try:
                    new_cursor.execute("""
                    INSERT OR IGNORE INTO employees 
                    (emp_id, name, department, position, hire_date, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        emp['emp_id'],
                        emp['name'],
                        emp.get('department'),
                        emp.get('position'),
                        emp.get('hire_date'),
                        emp.get('is_active', 1),
                        emp.get('created_at')
                    ))
                    count += 1
                except Exception as e:
                    print(f"  ⚠️  직원 마이그레이션 실패 ({emp['name']}): {e}")
            
            print(f"  ✅ 직원 {count}명 마이그레이션 완료")
        
        except Exception as e:
            print(f"  ❌ 직원 테이블 마이그레이션 실패: {e}")
        
        # 2. Users 마이그레이션
        user_count = 0
        try:
            old_cursor.execute("SELECT * FROM users WHERE is_active = 1")
            users = old_cursor.fetchall()
            
            for user in users:
                try:
                    new_cursor.execute("""
                    INSERT OR IGNORE INTO users 
                    (username, password_hash, role, is_active, created_at, last_login)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        user['username'],
                        user['password_hash'],
                        user.get('role', 'employee'),
                        user.get('is_active', 1),
                        user.get('created_at'),
                        user.get('last_login')
                    ))
                    user_count += 1
                except Exception as e:
                    print(f"  ⚠️  사용자 마이그레이션 실패 ({user['username']}): {e}")
            
            print(f"  ✅ 사용자 {user_count}명 마이그레이션 완료")
        
        except Exception as e:
            print(f"  ❌ 사용자 테이블 마이그레이션 실패: {e}")
        
        # 3. Work Logs 마이그레이션
        log_count = 0
        try:
            old_cursor.execute("SELECT * FROM work_logs ORDER BY work_date DESC LIMIT 1000")
            logs = old_cursor.fetchall()
            
            for log in logs:
                try:
                    new_cursor.execute("""
                    INSERT OR IGNORE INTO work_logs 
                    (emp_id, work_date, start_time, end_time, break_time, work_hours,
                     work_description, work_type, status, is_manual, created_at, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        log['emp_id'],
                        log['work_date'],
                        log.get('start_time'),
                        log.get('end_time'),
                        log.get('break_time', '12:00-13:00'),
                        log.get('work_hours'),
                        log.get('work_description'),
                        log.get('work_type', '재택근무'),
                        log.get('status', 'approved'),
                        log.get('is_manual', 1),
                        log.get('created_at'),
                        log.get('created_by')
                    ))
                    log_count += 1
                except Exception as e:
                    print(f"  ⚠️  근무 로그 마이그레이션 실패: {e}")
            
            print(f"  ✅ 근무 로그 {log_count}건 마이그레이션 완료")
        
        except Exception as e:
            print(f"  ❌ 근무 로그 테이블 마이그레이션 실패: {e}")
        
        new_conn.commit()
    
    old_conn.close()
    
    total = count + user_count + log_count
    print(f"📦 재택근무 DB 마이그레이션 완료: 총 {total}건")
    return total


def migrate_from_subsidy_db():
    """
    정부지원금 자동화 DB에서 마이그레이션
    - employees (추가 정보)
    - subsidies
    - applications
    """
    old_db_path = Path(__file__).parent.parent / "4_정부지원금_자동화" / "hr_automation.db"
    
    if not old_db_path.exists():
        print("⚠️  정부지원금 DB 파일이 없습니다. 스킵합니다.")
        return 0
    
    print("\n💼 정부지원금 DB 마이그레이션 시작...")
    
    old_conn = sqlite3.connect(str(old_db_path))
    old_conn.row_factory = sqlite3.Row
    old_cursor = old_conn.cursor()
    
    count = 0
    
    with get_db() as new_conn:
        new_cursor = new_conn.cursor()
        
        # 1. Employees 추가 정보 업데이트
        emp_count = 0
        try:
            old_cursor.execute("SELECT * FROM employees")
            employees = old_cursor.fetchall()
            
            for emp in employees:
                try:
                    # 기존 직원이면 UPDATE, 없으면 INSERT
                    new_cursor.execute("""
                    INSERT INTO employees 
                    (name, resident_number, department, position, hire_date, gender, age,
                     is_pregnant, is_on_leave, is_youth, is_disabled, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(emp_id) DO UPDATE SET
                        resident_number = excluded.resident_number,
                        gender = excluded.gender,
                        age = excluded.age,
                        is_pregnant = excluded.is_pregnant,
                        is_on_leave = excluded.is_on_leave,
                        is_youth = excluded.is_youth,
                        is_disabled = excluded.is_disabled,
                        notes = excluded.notes,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE emp_id IS NULL
                    """, (
                        emp['name'],
                        emp.get('resident_number'),
                        emp.get('department'),
                        emp.get('position'),
                        emp.get('hire_date'),
                        emp.get('gender'),
                        emp.get('age'),
                        emp.get('is_pregnant', 0),
                        emp.get('is_on_leave', 0),
                        emp.get('is_youth', 0),
                        emp.get('is_disabled', 0),
                        emp.get('notes')
                    ))
                    emp_count += 1
                except Exception as e:
                    print(f"  ⚠️  직원 정보 업데이트 실패: {e}")
            
            print(f"  ✅ 직원 정보 {emp_count}건 처리 완료")
        
        except Exception as e:
            print(f"  ❌ 직원 테이블 마이그레이션 실패: {e}")
        
        # 2. Subsidies 마이그레이션
        subsidy_count = 0
        try:
            old_cursor.execute("SELECT * FROM subsidies")
            subsidies = old_cursor.fetchall()
            
            for sub in subsidies:
                try:
                    new_cursor.execute("""
                    INSERT OR REPLACE INTO subsidies 
                    (code, name, category, description, estimated_amount, max_months,
                     deadline, contact, url, required_documents, why_matched, match_score,
                     is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        sub['code'],
                        sub['name'],
                        sub.get('category'),
                        sub.get('description'),
                        sub.get('estimated_amount'),
                        sub.get('max_months'),
                        sub.get('deadline'),
                        sub.get('contact'),
                        sub.get('application_url'),
                        sub.get('required_documents'),
                        sub.get('why_matched'),
                        sub.get('match_score'),
                        1,
                        sub.get('searched_at')
                    ))
                    subsidy_count += 1
                except Exception as e:
                    print(f"  ⚠️  지원금 마이그레이션 실패 ({sub['name']}): {e}")
            
            print(f"  ✅ 지원금 {subsidy_count}건 마이그레이션 완료")
        
        except Exception as e:
            print(f"  ❌ 지원금 테이블 마이그레이션 실패: {e}")
        
        # 3. Applications 마이그레이션
        app_count = 0
        try:
            old_cursor.execute("SELECT * FROM applications")
            applications = old_cursor.fetchall()
            
            for app in applications:
                try:
                    new_cursor.execute("""
                    INSERT OR IGNORE INTO applications 
                    (emp_id, subsidy_id, application_date, status, expected_amount,
                     actual_amount, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        None,  # emp_id는 나중에 매핑 필요
                        app.get('subsidy_id'),
                        app.get('application_date'),
                        app.get('status', '준비중'),
                        app.get('expected_amount'),
                        app.get('actual_amount'),
                        app.get('notes'),
                        app.get('created_at')
                    ))
                    app_count += 1
                except Exception as e:
                    print(f"  ⚠️  신청 내역 마이그레이션 실패: {e}")
            
            print(f"  ✅ 신청 내역 {app_count}건 마이그레이션 완료")
        
        except Exception as e:
            print(f"  ❌ 신청 내역 테이블 마이그레이션 실패: {e}")
        
        new_conn.commit()
    
    old_conn.close()
    
    total = emp_count + subsidy_count + app_count
    print(f"💼 정부지원금 DB 마이그레이션 완료: 총 {total}건")
    return total


def migrate_from_maternity_json():
    """
    출산육아 JSON 파일에서 마이그레이션
    - employees_data.json
    """
    json_file = Path(__file__).parent.parent / "1_출산육아_자동화" / "employees_data.json"
    
    if not json_file.exists():
        print("⚠️  출산육아 JSON 파일이 없습니다. 스킵합니다.")
        return 0
    
    print("\n👶 출산육아 JSON 마이그레이션 시작...")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    count = 0
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Employees 마이그레이션
        if 'employees' in data:
            for emp_id, emp_data in data['employees'].items():
                try:
                    cursor.execute("""
                    INSERT OR IGNORE INTO employees 
                    (emp_id, name, department, position, is_pregnant, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        emp_id,
                        emp_data.get('name'),
                        emp_data.get('department'),
                        emp_data.get('position'),
                        emp_data.get('is_pregnant', 0),
                        json.dumps(emp_data, ensure_ascii=False)
                    ))
                    count += 1
                except Exception as e:
                    print(f"  ⚠️  직원 마이그레이션 실패 ({emp_data.get('name')}): {e}")
        
        conn.commit()
    
    print(f"👶 출산육아 JSON 마이그레이션 완료: {count}건")
    return count


def create_sample_data():
    """
    샘플 데이터 생성 (테스트용)
    """
    print("\n🎨 샘플 데이터 생성 시작...")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 회사 정보
        try:
            cursor.execute("""
            INSERT OR REPLACE INTO company_profile 
            (id, company_name, ceo_name, business_number, business_type, employee_count,
             annual_revenue, location, is_priority_support)
            VALUES (1, '(주)예시회사', '이진선', '123-45-67890', 'IT서비스업', 25,
                    500000000, '서울시 강남구', 1)
            """)
            print("  ✅ 회사 정보 생성 완료")
        except Exception as e:
            print(f"  ❌ 회사 정보 생성 실패: {e}")
        
        conn.commit()
    
    print("🎨 샘플 데이터 생성 완료")


def main():
    """
    메인 마이그레이션 실행
    """
    print("=" * 60)
    print("🔄 데이터 마이그레이션 시작")
    print("=" * 60)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    total = 0
    
    # 1. 재택근무 DB 마이그레이션
    total += migrate_from_remote_work_db()
    
    # 2. 정부지원금 DB 마이그레이션
    total += migrate_from_subsidy_db()
    
    # 3. 출산육아 JSON 마이그레이션
    total += migrate_from_maternity_json()
    
    # 4. 샘플 데이터 생성
    create_sample_data()
    
    # 5. 시스템 로그 추가
    add_system_log("system", "데이터 마이그레이션 완료", "migration", 
                   f"총 {total}건의 데이터 마이그레이션")
    
    print()
    print("=" * 60)
    print(f"✅ 모든 마이그레이션 완료!")
    print(f"   총 마이그레이션 건수: {total}건")
    print(f"   종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    print("💡 다음 단계:")
    print("   1. 통합 DB 확인: sqlite3 hr_master.db")
    print("   2. 통합 대시보드 실행")
    print("   3. 각 앱 테스트")


if __name__ == "__main__":
    main()
