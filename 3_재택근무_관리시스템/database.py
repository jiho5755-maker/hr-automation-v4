"""
database.py
Remote Work Management System - Database Engine
SQLite with WAL mode for better concurrency

통합 DB 연동: 직원 관련 함수는 shared 모듈 사용
"""

import sqlite3
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from pathlib import Path

# shared 모듈 import (직원 관리용)
sys.path.append(str(Path(__file__).parent.parent))
from shared import database as shared_db

# 로컬 DB 사용 (이 앱 전용 - 근무 로그만)
DB_FILE = str(Path(__file__).parent / "work_logs.db")


@contextmanager
def get_db_connection():
    """Database connection context manager with WAL mode"""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize all database tables"""
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Users table (Authentication)
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Employees table
        c.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                department TEXT,
                position TEXT,
                hire_date TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Work logs table (Core data)
        c.execute("""
            CREATE TABLE IF NOT EXISTS work_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id TEXT NOT NULL,
                work_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                break_time TEXT DEFAULT '12:00-13:00',
                work_hours REAL NOT NULL,
                work_description TEXT,
                work_type TEXT DEFAULT '재택근무',
                status TEXT DEFAULT 'Approved',
                is_manual INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                modified_at TEXT,
                modified_by TEXT,
                FOREIGN KEY (emp_id) REFERENCES employees (emp_id)
            )
        """)
        
        # Company settings
        c.execute("""
            CREATE TABLE IF NOT EXISTS company_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # System logs (Internal audit trail)
        c.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                username TEXT,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT
            )
        """)
        
        # Create indexes for performance
        c.execute("CREATE INDEX IF NOT EXISTS idx_work_logs_emp_date ON work_logs(emp_id, work_date)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_work_logs_date ON work_logs(work_date)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp)")
        
        conn.commit()
        print("✅ Database initialized with WAL mode")


def seed_initial_data(admin_password_hash: str, user_password_hash: str):
    """Seed initial admin user and default employee"""
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Check if admin exists
        c.execute("SELECT id FROM users WHERE username = 'admin'")
        if not c.fetchone():
            c.execute("""
                INSERT INTO users (username, password_hash, full_name, role)
                VALUES (?, ?, ?, ?)
            """, ('admin', admin_password_hash, '시스템 관리자', 'admin'))
            print("✅ Admin user created")
        
        # Check if default employee exists
        c.execute("SELECT id FROM employees WHERE emp_id = 'EMP001'")
        if not c.fetchone():
            c.execute("""
                INSERT INTO employees (emp_id, name, department, position, hire_date)
                VALUES (?, ?, ?, ?, ?)
            """, ('EMP001', '송미', '디자인 기획팀', '대리', '2025-01-01'))
            print("✅ Default employee (송미) created")
        
        # Check if user account for 송미 exists
        c.execute("SELECT id FROM users WHERE username = 'songmi'")
        if not c.fetchone():
            c.execute("""
                INSERT INTO users (username, password_hash, full_name, role)
                VALUES (?, ?, ?, ?)
            """, ('songmi', user_password_hash, '송미', 'user'))
            print("✅ User account (송미) created")
        
        # Insert default company settings
        default_settings = [
            ('company_name', '(주)예시회사'),
            ('representative', '이진선'),
            ('business_number', '123-45-67890'),
            ('system_version', '2.0')
        ]
        
        for key, value in default_settings:
            c.execute("INSERT OR IGNORE INTO company_settings (setting_key, setting_value) VALUES (?, ?)",
                     (key, value))
        
        conn.commit()


# ============= CRUD Operations =============

# Users
def add_user(username: str, password_hash: str, full_name: str, role: str = 'user') -> bool:
    """Add new user account"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO users (username, password_hash, full_name, role)
                VALUES (?, ?, ?, ?)
            """, (username, password_hash, full_name, role))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
        row = c.fetchone()
        return dict(row) if row else None


# ==================== 직원 관리 (통합 DB 사용) ====================
# 주의: 이 함수들은 이제 shared.database를 사용합니다!

def get_all_employees(active_only: bool = True) -> List[Dict]:
    """Get all employees from central DB"""
    return shared_db.get_all_employees(active_only=active_only)


def add_employee(emp_id: str, name: str, department: str, position: str, hire_date: str, email: str = None, phone: str = None) -> bool:
    """Add new employee to central DB"""
    try:
        employee_data = {
            'emp_id': emp_id,
            'name': name,
            'department': department,
            'position': position,
            'hire_date': hire_date,
            'email': email,
            'phone': phone,
            'created_by': 'work_system'
        }
        
        # 기존 직원 확인
        existing = shared_db.get_employee_by_id(emp_id)
        if existing:
            if not existing.get('is_active'):
                # 재활성화
                employee_data['is_active'] = 1
                return shared_db.update_employee(emp_id, employee_data)
            return False  # 이미 활성 직원
        else:
            # 새로 추가
            shared_db.add_employee(employee_data)
            return True
    except Exception as e:
        print(f"Add employee error: {e}")
        return False


def update_employee(emp_id: str, name: str, department: str, position: str, hire_date: str, email: str = None, phone: str = None) -> bool:
    """Update employee information in central DB"""
    try:
        employee_data = {
            'emp_id': emp_id,
            'name': name,
            'department': department,
            'position': position,
            'hire_date': hire_date,
            'email': email,
            'phone': phone
        }
        return shared_db.update_employee(emp_id, employee_data)
    except Exception as e:
        print(f"Update employee error: {e}")
        return False


def delete_employee(emp_id: str) -> bool:
    """Soft delete employee in central DB"""
    try:
        return shared_db.delete_employee(emp_id, hard_delete=False)
    except Exception as e:
        print(f"Delete employee error: {e}")
        return False


def get_employee_by_id(emp_id: str) -> Optional[Dict]:
    """Get employee by emp_id from central DB"""
    return shared_db.get_employee_by_id(emp_id)


# Work Logs
def get_work_logs(emp_id: Optional[str] = None, start_date: Optional[str] = None, 
                  end_date: Optional[str] = None) -> List[Dict]:
    """Get work logs with optional filters"""
    with get_db_connection() as conn:
        c = conn.cursor()
        query = "SELECT * FROM work_logs WHERE 1=1"
        params = []
        
        if emp_id:
            query += " AND emp_id = ?"
            params.append(emp_id)
        if start_date:
            query += " AND work_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND work_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY work_date DESC, start_time DESC"
        c.execute(query, params)
        return [dict(row) for row in c.fetchall()]


def add_work_log(emp_id: str, work_date: str, start_time: str, end_time: str,
                break_time: str, work_hours: float, work_description: str,
                work_type: str, created_by: str, is_manual: int = 1) -> int:
    """Add a single work log"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO work_logs 
            (emp_id, work_date, start_time, end_time, break_time, work_hours, 
             work_description, work_type, created_by, is_manual, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Approved')
        """, (emp_id, work_date, start_time, end_time, break_time, work_hours,
              work_description, work_type, created_by, is_manual))
        conn.commit()
        return c.lastrowid


def bulk_add_work_logs(logs: List[Dict]) -> int:
    """Bulk insert work logs"""
    with get_db_connection() as conn:
        c = conn.cursor()
        count = 0
        for log in logs:
            c.execute("""
                INSERT INTO work_logs 
                (emp_id, work_date, start_time, end_time, break_time, work_hours, 
                 work_description, work_type, created_by, is_manual, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Approved')
            """, (
                log['emp_id'], log['work_date'], log['start_time'], log['end_time'],
                log.get('break_time', '12:00-13:00'), log['work_hours'],
                log['work_description'], log.get('work_type', '재택근무'),
                log['created_by'], log.get('is_manual', 1)
            ))
            count += 1
        conn.commit()
        return count


def update_work_log(log_id: int, updates: Dict, modified_by: str) -> bool:
    """Update a work log"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            query = f"UPDATE work_logs SET {set_clause}, modified_at = ?, modified_by = ? WHERE id = ?"
            params = list(updates.values()) + [datetime.now().isoformat(), modified_by, log_id]
            c.execute(query, params)
            conn.commit()
        return True
    except Exception as e:
        print(f"Update error: {e}")
        return False


def delete_work_log(log_id: int) -> bool:
    """Delete a work log"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM work_logs WHERE id = ?", (log_id,))
            conn.commit()
        return True
    except Exception as e:
        print(f"Delete error: {e}")
        return False


# Company Settings
def get_company_setting(key: str) -> Optional[str]:
    """Get company setting by key"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT setting_value FROM company_settings WHERE setting_key = ?", (key,))
        row = c.fetchone()
        return row['setting_value'] if row else None


def update_company_setting(key: str, value: str) -> bool:
    """Update company setting"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO company_settings (setting_key, setting_value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(setting_key) DO UPDATE SET 
                    setting_value = excluded.setting_value,
                    updated_at = excluded.updated_at
            """, (key, value, datetime.now().isoformat()))
            conn.commit()
        return True
    except Exception as e:
        print(f"Setting update error: {e}")
        return False


# System Logs
def add_system_log(username: str, action: str, details: str = "", ip_address: str = ""):
    """Add system log entry"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO system_logs (username, action, details, ip_address)
            VALUES (?, ?, ?, ?)
        """, (username, action, details, ip_address))
        conn.commit()


def get_system_logs(limit: int = 100) -> List[Dict]:
    """Get recent system logs"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT * FROM system_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in c.fetchall()]


# Statistics
def get_work_stats(emp_id: str, start_date: str, end_date: str) -> Dict:
    """Get work statistics for an employee in a date range"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT 
                COUNT(*) as total_days,
                SUM(work_hours) as total_hours,
                AVG(work_hours) as avg_hours,
                MIN(work_date) as first_date,
                MAX(work_date) as last_date
            FROM work_logs
            WHERE emp_id = ? AND work_date BETWEEN ? AND ?
        """, (emp_id, start_date, end_date))
        row = c.fetchone()
        return dict(row) if row else {}
