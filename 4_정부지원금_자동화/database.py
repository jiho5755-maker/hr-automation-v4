"""
데이터베이스 관리 시스템
SQLite 기반 직원, 지원금, 신청 내역 관리

통합 DB 연동: 직원/회사 정보는 shared 모듈 사용
"""

import sqlite3
import sys
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json

# shared 모듈 import (직원/회사 관리용)
sys.path.append(str(Path(__file__).parent.parent))
from shared import database as shared_db


class Database:
    """데이터베이스 연결 및 관리"""
    
    DB_FILE = "hr_automation.db"
    
    def __init__(self, db_path: Optional[str] = None):
        """
        데이터베이스 초기화
        
        Args:
            db_path: 데이터베이스 파일 경로 (None이면 로컬 DB 사용)
        """
        if db_path:
            self.db_path = Path(db_path)
        else:
            # 로컬 DB 사용 (이 앱 전용)
            self.db_path = Path(__file__).parent / "hr_automation.db"
        
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """데이터베이스 연결"""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
        self.cursor = self.conn.cursor()
    
    def close(self):
        """연결 종료"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        if self.conn:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
        self.close()
    
    def create_tables(self):
        """테이블 생성"""
        self.connect()
        
        # 직원 정보 테이블
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            resident_number TEXT,
            department TEXT,
            position TEXT,
            hire_date DATE,
            gender TEXT,
            age INTEGER,
            is_pregnant BOOLEAN DEFAULT 0,
            is_on_leave BOOLEAN DEFAULT 0,
            is_youth BOOLEAN DEFAULT 0,
            is_disabled BOOLEAN DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 지원금 정보 테이블
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS subsidies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            estimated_amount INTEGER,
            max_months INTEGER,
            match_score REAL,
            deadline TEXT,
            contact TEXT,
            application_url TEXT,
            required_documents TEXT,
            why_matched TEXT,
            searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 신청 내역 테이블
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            subsidy_id INTEGER,
            application_date DATE,
            status TEXT DEFAULT '준비중',
            expected_amount INTEGER,
            actual_amount INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (subsidy_id) REFERENCES subsidies(id)
        )
        """)
        
        # 회사 정보 테이블
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            business_type TEXT,
            employee_count INTEGER,
            annual_revenue INTEGER,
            location TEXT,
            is_priority_support BOOLEAN DEFAULT 0,
            situations TEXT,
            employee_stats TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        self.conn.commit()
        print("✅ 데이터베이스 테이블이 생성되었습니다.")
    
    def insert_sample_data(self):
        """샘플 데이터 삽입 (테스트용)"""
        # 샘플 직원 데이터
        employees = [
            ("김민지", "901231-2******", "디자인팀", "주임", "2023-03-15", "여성", 34, 1, 0, 1, 0),
            ("이준호", "851010-1******", "개발팀", "과장", "2020-01-10", "남성", 40, 0, 0, 0, 0),
            ("박서연", "950505-2******", "마케팅팀", "대리", "2021-06-20", "여성", 31, 0, 0, 1, 0),
        ]
        
        for emp in employees:
            try:
                self.cursor.execute("""
                INSERT INTO employees 
                (name, resident_number, department, position, hire_date, gender, age, 
                 is_pregnant, is_on_leave, is_youth, is_disabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, emp)
            except sqlite3.IntegrityError:
                pass  # 이미 존재하면 스킵
        
        self.conn.commit()
        print("✅ 샘플 데이터가 삽입되었습니다.")


class EmployeeManager:
    """
    직원 정보 관리 (통합 DB 연동)
    주의: 이 클래스는 이제 shared.database를 사용합니다!
    """
    
    @staticmethod
    def add_employee(db: Database, employee_data: Dict) -> int:
        """
        직원 추가 (통합 DB 사용)
        
        Args:
            db: Database 인스턴스 (사용하지 않음, 호환성 유지)
            employee_data: 직원 정보 딕셔너리
        
        Returns:
            추가된 직원 ID
        """
        # emp_id 생성
        resident_num = employee_data.get("resident_number", "")
        emp_id = resident_num[:6] if resident_num else f"EMP{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        employee_data['emp_id'] = emp_id
        employee_data['created_by'] = 'subsidy_app'
        
        return shared_db.add_employee(employee_data)
    
    @staticmethod
    def get_all_employees(db: Database) -> List[Dict]:
        """
        전체 직원 조회 (통합 DB 사용)
        
        Returns:
            직원 리스트
        """
        return shared_db.get_all_employees(active_only=True)
    
    @staticmethod
    def get_employee(db: Database, employee_id: int) -> Optional[Dict]:
        """
        특정 직원 조회 (통합 DB 사용)
        
        Args:
            employee_id: 직원 ID (또는 emp_id 문자열)
        
        Returns:
            직원 정보 딕셔너리
        """
        # id가 정수면 조회 불가 (통합 DB는 emp_id 사용)
        # 전체 조회 후 id로 필터링
        employees = shared_db.get_all_employees(active_only=False)
        for emp in employees:
            if emp.get('id') == employee_id:
                return emp
        return None
    
    @staticmethod
    def update_employee(db: Database, employee_id: int, employee_data: Dict):
        """직원 정보 수정 (통합 DB 사용)"""
        # id로 emp_id 찾기
        employee = EmployeeManager.get_employee(db, employee_id)
        if employee:
            emp_id = employee.get('emp_id')
            shared_db.update_employee(emp_id, employee_data)
    
    @staticmethod
    def delete_employee(db: Database, employee_id: int):
        """직원 삭제 (통합 DB 사용, 소프트 삭제)"""
        employee = EmployeeManager.get_employee(db, employee_id)
        if employee:
            emp_id = employee.get('emp_id')
            shared_db.delete_employee(emp_id, hard_delete=False)
    
    @staticmethod
    def search_employees(db: Database, keyword: str) -> List[Dict]:
        """직원 검색 (통합 DB 사용)"""
        return shared_db.search_employees(keyword)


class SubsidyManager:
    """지원금 정보 관리"""
    
    @staticmethod
    def add_subsidy(db: Database, subsidy_data: Dict) -> int:
        """지원금 추가"""
        db.cursor.execute("""
        INSERT OR REPLACE INTO subsidies 
        (code, name, category, description, estimated_amount, max_months,
         match_score, deadline, contact, application_url, required_documents, why_matched)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            subsidy_data.get("code"),
            subsidy_data.get("name"),
            subsidy_data.get("category"),
            subsidy_data.get("description"),
            subsidy_data.get("estimated_amount"),
            subsidy_data.get("max_months"),
            subsidy_data.get("match_score"),
            subsidy_data.get("deadline"),
            subsidy_data.get("contact"),
            subsidy_data.get("application_url"),
            json.dumps(subsidy_data.get("required_documents", []), ensure_ascii=False),
            json.dumps(subsidy_data.get("why_matched", []), ensure_ascii=False)
        ))
        db.conn.commit()
        return db.cursor.lastrowid
    
    @staticmethod
    def bulk_add_subsidies(db: Database, subsidies: List[Dict]):
        """지원금 일괄 추가"""
        for subsidy in subsidies:
            SubsidyManager.add_subsidy(db, subsidy)
    
    @staticmethod
    def get_all_subsidies(db: Database) -> List[Dict]:
        """전체 지원금 조회"""
        db.cursor.execute("SELECT * FROM subsidies ORDER BY match_score DESC, searched_at DESC")
        rows = db.cursor.fetchall()
        
        result = []
        for row in rows:
            subsidy = dict(row)
            # JSON 필드 파싱
            subsidy['required_documents'] = json.loads(subsidy.get('required_documents', '[]'))
            subsidy['why_matched'] = json.loads(subsidy.get('why_matched', '[]'))
            result.append(subsidy)
        
        return result
    
    @staticmethod
    def get_subsidy(db: Database, subsidy_id: int) -> Optional[Dict]:
        """특정 지원금 조회"""
        db.cursor.execute("SELECT * FROM subsidies WHERE id = ?", (subsidy_id,))
        row = db.cursor.fetchone()
        
        if row:
            subsidy = dict(row)
            subsidy['required_documents'] = json.loads(subsidy.get('required_documents', '[]'))
            subsidy['why_matched'] = json.loads(subsidy.get('why_matched', '[]'))
            return subsidy
        
        return None
    
    @staticmethod
    def search_subsidies(db: Database, keyword: str = None, category: str = None) -> List[Dict]:
        """지원금 검색"""
        query = "SELECT * FROM subsidies WHERE 1=1"
        params = []
        
        if keyword:
            query += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY match_score DESC"
        
        db.cursor.execute(query, params)
        rows = db.cursor.fetchall()
        
        result = []
        for row in rows:
            subsidy = dict(row)
            subsidy['required_documents'] = json.loads(subsidy.get('required_documents', '[]'))
            subsidy['why_matched'] = json.loads(subsidy.get('why_matched', '[]'))
            result.append(subsidy)
        
        return result


class ApplicationManager:
    """신청 내역 관리"""
    
    @staticmethod
    def add_application(db: Database, application_data: Dict) -> int:
        """신청 내역 추가"""
        db.cursor.execute("""
        INSERT INTO applications 
        (employee_id, subsidy_id, application_date, status, expected_amount, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            application_data.get("employee_id"),
            application_data.get("subsidy_id"),
            application_data.get("application_date", date.today().isoformat()),
            application_data.get("status", "준비중"),
            application_data.get("expected_amount"),
            application_data.get("notes", "")
        ))
        db.conn.commit()
        return db.cursor.lastrowid
    
    @staticmethod
    def get_all_applications(db: Database) -> List[Dict]:
        """전체 신청 내역 조회"""
        db.cursor.execute("""
        SELECT 
            a.*,
            e.name as employee_name,
            e.department,
            s.name as subsidy_name,
            s.category
        FROM applications a
        LEFT JOIN employees e ON a.employee_id = e.id
        LEFT JOIN subsidies s ON a.subsidy_id = s.id
        ORDER BY a.application_date DESC
        """)
        rows = db.cursor.fetchall()
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_employee_applications(db: Database, employee_id: int) -> List[Dict]:
        """특정 직원의 신청 내역"""
        db.cursor.execute("""
        SELECT 
            a.*,
            s.name as subsidy_name,
            s.category,
            s.estimated_amount
        FROM applications a
        LEFT JOIN subsidies s ON a.subsidy_id = s.id
        WHERE a.employee_id = ?
        ORDER BY a.application_date DESC
        """, (employee_id,))
        rows = db.cursor.fetchall()
        return [dict(row) for row in rows]
    
    @staticmethod
    def update_application_status(db: Database, application_id: int, status: str, actual_amount: int = None):
        """신청 상태 업데이트"""
        if actual_amount is not None:
            db.cursor.execute("""
            UPDATE applications 
            SET status = ?, actual_amount = ?, updated_at = ?
            WHERE id = ?
            """, (status, actual_amount, datetime.now().isoformat(), application_id))
        else:
            db.cursor.execute("""
            UPDATE applications 
            SET status = ?, updated_at = ?
            WHERE id = ?
            """, (status, datetime.now().isoformat(), application_id))
        
        db.conn.commit()
    
    @staticmethod
    def get_statistics(db: Database) -> Dict:
        """신청 통계"""
        stats = {}
        
        # 총 신청 건수
        db.cursor.execute("SELECT COUNT(*) as count FROM applications")
        stats['total_applications'] = db.cursor.fetchone()['count']
        
        # 상태별 건수
        db.cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM applications 
        GROUP BY status
        """)
        stats['by_status'] = {row['status']: row['count'] for row in db.cursor.fetchall()}
        
        # 예상 총 금액
        db.cursor.execute("SELECT SUM(expected_amount) as total FROM applications")
        stats['total_expected'] = db.cursor.fetchone()['total'] or 0
        
        # 실제 수령 금액
        db.cursor.execute("SELECT SUM(actual_amount) as total FROM applications WHERE status = '승인'")
        stats['total_received'] = db.cursor.fetchone()['total'] or 0
        
        return stats


# 초기화 함수
def initialize_database(db_path: Optional[str] = None):
    """
    데이터베이스 초기화
    
    Args:
        db_path: 데이터베이스 파일 경로
    """
    with Database(db_path) as db:
        db.create_tables()
        print("✅ 데이터베이스가 초기화되었습니다.")


if __name__ == "__main__":
    # 테스트
    initialize_database()
    
    with Database() as db:
        db.insert_sample_data()
        
        # 직원 조회 테스트
        employees = EmployeeManager.get_all_employees(db)
        print(f"\n📋 전체 직원 수: {len(employees)}")
        for emp in employees:
            print(f"  - {emp['name']} ({emp['department']} {emp['position']})")
