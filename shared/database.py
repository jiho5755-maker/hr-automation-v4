"""
통합 데이터베이스 모듈
Integrated Database Module for HR Automation System

SQLite 기반 통합 데이터베이스 관리
- 직원 마스터 데이터
- 근무 기록
- 지원금 정보
- 연말정산 데이터
- 시스템 로그
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import json


# 데이터베이스 경로 (프로젝트 루트)
DB_PATH = Path(__file__).parent.parent / "hr_master.db"


@contextmanager
def get_db():
    """
    데이터베이스 연결 컨텍스트 매니저
    
    사용 예:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employees")
            results = cursor.fetchall()
    """
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 반환
    conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
    conn.execute("PRAGMA foreign_keys=ON")   # 외래키 제약조건 활성화
    try:
        yield conn
    finally:
        conn.close()


def init_master_database():
    """
    통합 데이터베이스 초기화
    모든 테이블 생성
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        print("🔧 통합 데이터베이스 초기화 중...")
        
        # ==================== 1. 직원 마스터 테이블 ====================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            resident_number TEXT,
            department TEXT,
            position TEXT,
            hire_date DATE,
            gender TEXT CHECK(gender IN ('남성', '여성', NULL)),
            age INTEGER,
            email TEXT,
            phone TEXT,
            
            -- 상태 정보
            is_active BOOLEAN DEFAULT 1,
            is_pregnant BOOLEAN DEFAULT 0,
            is_on_leave BOOLEAN DEFAULT 0,
            is_youth BOOLEAN DEFAULT 0,
            is_disabled BOOLEAN DEFAULT 0,
            
            -- 감사 정보
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            
            -- 메모
            notes TEXT
        )
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_emp_id ON employees(emp_id)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_emp_name ON employees(name)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_emp_dept ON employees(department)
        """)
        
        # ==================== 2. 사용자 인증 테이블 ====================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            emp_id TEXT,
            role TEXT CHECK(role IN ('admin', 'hr', 'manager', 'employee')) DEFAULT 'employee',
            is_active BOOLEAN DEFAULT 1,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE SET NULL
        )
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_username ON users(username)
        """)
        
        # ==================== 3. 근무 기록 테이블 (재택근무) ====================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS work_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            work_date DATE NOT NULL,
            work_type TEXT DEFAULT '재택근무',
            start_time TIME,
            end_time TIME,
            break_time TEXT DEFAULT '12:00-13:00',
            work_hours REAL,
            work_description TEXT,
            status TEXT DEFAULT 'approved' CHECK(status IN ('pending', 'approved', 'rejected')),
            is_manual BOOLEAN DEFAULT 1,
            
            -- 감사 정보
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            modified_at TIMESTAMP,
            modified_by TEXT,
            
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
        )
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_work_date ON work_logs(work_date)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_work_emp_date ON work_logs(emp_id, work_date)
        """)
        
        # ==================== 4. 지원금 마스터 테이블 ====================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS subsidies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            estimated_amount INTEGER,
            max_months INTEGER,
            deadline DATE,
            contact TEXT,
            url TEXT,
            required_documents TEXT,  -- JSON 형태
            why_matched TEXT,         -- JSON 형태
            match_score REAL,
            is_active BOOLEAN DEFAULT 1,
            
            -- 감사 정보
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_subsidy_code ON subsidies(code)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_subsidy_category ON subsidies(category)
        """)
        
        # ==================== 5. 지원금 신청 내역 테이블 ====================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT,
            subsidy_id INTEGER,
            application_date DATE DEFAULT CURRENT_DATE,
            status TEXT DEFAULT '준비중' CHECK(status IN ('준비중', '신청완료', '심사중', '승인', '반려')),
            expected_amount INTEGER,
            actual_amount INTEGER,
            notes TEXT,
            
            -- 감사 정보
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE SET NULL,
            FOREIGN KEY (subsidy_id) REFERENCES subsidies(id) ON DELETE CASCADE
        )
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_app_emp ON applications(emp_id)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_app_subsidy ON applications(subsidy_id)
        """)
        
        # ==================== 6. 연말정산 데이터 테이블 ====================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS year_end_tax (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            year INTEGER NOT NULL,
            
            -- 의료비
            medical_total INTEGER DEFAULT 0,
            medical_insurance_refund INTEGER DEFAULT 0,
            medical_net INTEGER DEFAULT 0,
            
            -- 보험료
            health_insurance INTEGER DEFAULT 0,
            employment_insurance INTEGER DEFAULT 0,
            pension_insurance INTEGER DEFAULT 0,
            
            -- 신용카드
            credit_card_usage INTEGER DEFAULT 0,
            
            -- 주택
            housing_loan INTEGER DEFAULT 0,
            housing_savings INTEGER DEFAULT 0,
            
            -- 기타
            donation INTEGER DEFAULT 0,
            education INTEGER DEFAULT 0,
            
            -- 원본 파일 정보
            pdf_file_path TEXT,
            pdf_file_name TEXT,
            
            -- 감사 정보
            parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            parsed_by TEXT,
            
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE,
            UNIQUE(emp_id, year)
        )
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tax_emp_year ON year_end_tax(emp_id, year)
        """)
        
        # ==================== 7. 회사 정보 테이블 ====================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            ceo_name TEXT,
            business_number TEXT,
            business_type TEXT,
            employee_count INTEGER,
            annual_revenue INTEGER,
            location TEXT,
            is_priority_support BOOLEAN DEFAULT 0,
            
            -- 추가 정보 (JSON)
            situations TEXT,
            employee_stats TEXT,
            
            -- 감사 정보
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by TEXT
        )
        """)
        
        # ==================== 8. 시스템 로그 테이블 ====================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            username TEXT,
            action TEXT NOT NULL,
            module TEXT,
            details TEXT,
            ip_address TEXT,
            
            -- 로그 레벨
            level TEXT DEFAULT 'INFO' CHECK(level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
        )
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_log_timestamp ON system_logs(timestamp)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_log_username ON system_logs(username)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_log_module ON system_logs(module)
        """)
        
        conn.commit()
        print("✅ 통합 데이터베이스 초기화 완료!")
        print(f"📁 데이터베이스 위치: {DB_PATH}")


def add_system_log(username: str, action: str, module: str = None, 
                   details: str = None, level: str = "INFO"):
    """
    시스템 로그 추가
    
    Args:
        username: 사용자명
        action: 수행한 작업
        module: 모듈명 (예: '출산육아', '연말정산')
        details: 상세 내용
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO system_logs (username, action, module, details, level)
        VALUES (?, ?, ?, ?, ?)
        """, (username, action, module, details, level))
        conn.commit()


def get_company_profile() -> Optional[Dict]:
    """
    회사 정보 조회
    
    Returns:
        회사 정보 딕셔너리 또는 None
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM company_profile ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            profile = dict(row)
            # JSON 필드 파싱
            if profile.get('situations'):
                profile['situations'] = json.loads(profile['situations'])
            if profile.get('employee_stats'):
                profile['employee_stats'] = json.loads(profile['employee_stats'])
            return profile
        return None


def update_company_profile(profile_data: Dict):
    """
    회사 정보 업데이트
    
    Args:
        profile_data: 회사 정보 딕셔너리
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # JSON 필드 변환
        situations = json.dumps(profile_data.get('situations', []), ensure_ascii=False)
        employee_stats = json.dumps(profile_data.get('employee_stats', {}), ensure_ascii=False)
        
        # 기존 데이터 확인
        cursor.execute("SELECT id FROM company_profile LIMIT 1")
        existing = cursor.fetchone()
        
        if existing:
            # 업데이트
            cursor.execute("""
            UPDATE company_profile SET
                company_name = ?,
                ceo_name = ?,
                business_number = ?,
                business_type = ?,
                industry = ?,
                employee_count = ?,
                annual_revenue = ?,
                location = ?,
                phone = ?,
                establishment_date = ?,
                is_priority_support = ?,
                situations = ?,
                employee_stats = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (
                profile_data.get('company_name'),
                profile_data.get('ceo_name'),
                profile_data.get('business_number'),
                profile_data.get('business_type'),
                profile_data.get('industry'),
                profile_data.get('employee_count'),
                profile_data.get('annual_revenue'),
                profile_data.get('location'),
                profile_data.get('phone'),
                profile_data.get('establishment_date'),
                profile_data.get('is_priority_support', 0),
                situations,
                employee_stats,
                profile_data.get('notes'),
                existing['id']
            ))
        else:
            # 신규 삽입
            cursor.execute("""
            INSERT INTO company_profile (
                company_name, ceo_name, business_number, business_type, industry,
                employee_count, annual_revenue, location, phone, establishment_date,
                is_priority_support, situations, employee_stats, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_data.get('company_name'),
                profile_data.get('ceo_name'),
                profile_data.get('business_number'),
                profile_data.get('business_type'),
                profile_data.get('industry'),
                profile_data.get('employee_count'),
                profile_data.get('annual_revenue'),
                profile_data.get('location'),
                profile_data.get('phone'),
                profile_data.get('establishment_date'),
                profile_data.get('is_priority_support', 0),
                situations,
                employee_stats,
                profile_data.get('notes')
            ))
        
        conn.commit()


# ==================== 직원 관리 함수 (공유 API) ====================

def get_all_employees(active_only: bool = True) -> List[Dict]:
    """
    모든 직원 조회
    
    Args:
        active_only: True면 재직 중인 직원만, False면 전체
    
    Returns:
        직원 정보 리스트
    """
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM employees"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY department, name"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]


def get_employee_by_id(emp_id: str) -> Optional[Dict]:
    """
    직원 ID로 조회
    
    Args:
        emp_id: 직원 ID
    
    Returns:
        직원 정보 딕셔너리 또는 None
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE emp_id = ?", (emp_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_employee_by_name(name: str) -> Optional[Dict]:
    """
    직원 이름으로 조회
    
    Args:
        name: 직원 이름
    
    Returns:
        직원 정보 딕셔너리 또는 None
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE name = ?", (name,))
        row = cursor.fetchone()
        return dict(row) if row else None


def search_employees(keyword: str, search_fields: List[str] = None) -> List[Dict]:
    """
    직원 검색
    
    Args:
        keyword: 검색 키워드
        search_fields: 검색할 필드 리스트 (기본: name, department, position)
    
    Returns:
        검색된 직원 리스트
    """
    if search_fields is None:
        search_fields = ['name', 'department', 'position', 'email']
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 동적 쿼리 생성
        conditions = [f"{field} LIKE ?" for field in search_fields]
        query = f"SELECT * FROM employees WHERE ({' OR '.join(conditions)}) AND is_active = 1"
        params = [f"%{keyword}%" for _ in search_fields]
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def add_employee(employee_data: Dict) -> int:
    """
    직원 추가
    
    Args:
        employee_data: 직원 정보 딕셔너리
        
    Returns:
        생성된 직원의 ID
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO employees (
            emp_id, name, resident_number, department, position,
            hire_date, gender, age, email, phone,
            is_active, is_pregnant, is_on_leave, is_youth, is_disabled,
            created_by, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            employee_data.get('emp_id'),
            employee_data.get('name'),
            employee_data.get('resident_number'),
            employee_data.get('department'),
            employee_data.get('position'),
            employee_data.get('hire_date'),
            employee_data.get('gender'),
            employee_data.get('age'),
            employee_data.get('email'),
            employee_data.get('phone'),
            employee_data.get('is_active', 1),
            employee_data.get('is_pregnant', 0),
            employee_data.get('is_on_leave', 0),
            employee_data.get('is_youth', 0),
            employee_data.get('is_disabled', 0),
            employee_data.get('created_by', 'system'),
            employee_data.get('notes')
        ))
        conn.commit()
        
        # 시스템 로그
        add_system_log(
            employee_data.get('created_by', 'system'),
            f"직원 추가: {employee_data.get('name')}",
            "employee_management",
            f"직원 ID: {employee_data.get('emp_id')}"
        )
        
        return cursor.lastrowid


def update_employee(emp_id: str, employee_data: Dict) -> bool:
    """
    직원 정보 수정 (부분 업데이트 지원)
    
    Args:
        emp_id: 직원 ID
        employee_data: 수정할 직원 정보 (제공된 필드만 업데이트)
        
    Returns:
        성공 여부
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 동적으로 UPDATE 쿼리 생성 (제공된 필드만)
            set_clauses = []
            params = []
            
            field_mapping = {
                'name': 'name',
                'resident_number': 'resident_number',
                'department': 'department',
                'position': 'position',
                'hire_date': 'hire_date',
                'gender': 'gender',
                'age': 'age',
                'email': 'email',
                'phone': 'phone',
                'is_active': 'is_active',
                'is_pregnant': 'is_pregnant',
                'is_on_leave': 'is_on_leave',
                'is_youth': 'is_youth',
                'is_disabled': 'is_disabled',
                'notes': 'notes'
            }
            
            for key, column in field_mapping.items():
                if key in employee_data:
                    set_clauses.append(f"{column} = ?")
                    params.append(employee_data[key])
            
            if not set_clauses:
                print("업데이트할 필드가 없습니다.")
                return False
            
            # updated_at은 항상 업데이트
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            
            # WHERE 절을 위한 emp_id 추가
            params.append(emp_id)
            
            query = f"UPDATE employees SET {', '.join(set_clauses)} WHERE emp_id = ?"
            
            cursor.execute(query, params)
            conn.commit()
            
            # 시스템 로그
            updated_fields = ', '.join(employee_data.keys())
            add_system_log(
                employee_data.get('updated_by', 'system'),
                f"직원 정보 수정: {employee_data.get('name', emp_id)}",
                "employee_management",
                f"직원 ID: {emp_id}, 수정 필드: {updated_fields}"
            )
            
            return cursor.rowcount > 0
    except Exception as e:
        print(f"직원 정보 수정 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def delete_employee(emp_id: str, hard_delete: bool = False) -> bool:
    """
    직원 삭제 (소프트 삭제 기본)
    
    Args:
        emp_id: 직원 ID
        hard_delete: True면 완전 삭제, False면 is_active만 변경
        
    Returns:
        성공 여부
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            if hard_delete:
                cursor.execute("DELETE FROM employees WHERE emp_id = ?", (emp_id,))
            else:
                cursor.execute("""
                UPDATE employees SET is_active = 0, updated_at = CURRENT_TIMESTAMP 
                WHERE emp_id = ?
                """, (emp_id,))
            
            conn.commit()
            
            # 시스템 로그
            add_system_log(
                'system',
                f"직원 삭제: {emp_id}",
                "employee_management",
                f"완전 삭제: {hard_delete}"
            )
            
            return True
    except Exception as e:
        print(f"직원 삭제 실패: {e}")
        return False


def get_employees_by_department(department: str) -> List[Dict]:
    """
    부서별 직원 조회
    
    Args:
        department: 부서명
        
    Returns:
        직원 리스트
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM employees 
        WHERE department = ? AND is_active = 1
        ORDER BY position, name
        """, (department,))
        return [dict(row) for row in cursor.fetchall()]


def get_employee_count() -> int:
    """
    전체 직원 수 조회 (재직 중인 직원만)
    
    Returns:
        직원 수
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees WHERE is_active = 1")
        return cursor.fetchone()[0]


def get_departments() -> List[str]:
    """
    모든 부서 목록 조회
    
    Returns:
        부서 리스트
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT DISTINCT department FROM employees 
        WHERE department IS NOT NULL AND is_active = 1
        ORDER BY department
        """)
        return [row[0] for row in cursor.fetchall()]


# ==================== 데이터 동기화 유틸리티 ====================

def sync_employee_from_dict(employee_dict: Dict, source: str = "unknown") -> bool:
    """
    외부 데이터를 중앙 DB로 동기화
    
    Args:
        employee_dict: 직원 정보 딕셔너리
        source: 데이터 출처 (json, other_db, etc)
        
    Returns:
        성공 여부
    """
    try:
        emp_id = employee_dict.get('emp_id')
        
        # 기존 직원 확인
        existing = get_employee_by_id(emp_id) if emp_id else None
        
        if existing:
            # 업데이트
            return update_employee(emp_id, employee_dict)
        else:
            # 새로 추가
            employee_dict['created_by'] = f'sync_{source}'
            add_employee(employee_dict)
            return True
    except Exception as e:
        print(f"동기화 실패: {e}")
        return False


if __name__ == "__main__":
    # 테스트: 데이터베이스 초기화
    init_master_database()
    
    # 테스트: 로그 추가
    add_system_log("system", "데이터베이스 초기화", "database", "통합 DB 생성 완료")
    
    # 테스트: 직원 관리 함수
    print("\n=== 직원 관리 함수 테스트 ===")
    
    # 직원 수 조회
    count = get_employee_count()
    print(f"현재 직원 수: {count}명")
    
    # 부서 목록 조회
    departments = get_departments()
    print(f"부서 목록: {departments}")
    
    print("\n✅ 통합 데이터베이스 모듈 테스트 완료!")
