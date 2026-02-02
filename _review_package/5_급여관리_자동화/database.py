"""
급여관리 자동화 - 데이터베이스 관리
급여 정보, 지급 이력, 공제 내역 저장
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from contextlib import contextmanager

# 데이터베이스 파일 경로
DB_PATH = Path(__file__).parent.parent / "hr_master.db"


@contextmanager
def get_db():
    """데이터베이스 연결 컨텍스트 관리자"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_payroll_tables():
    """급여 관련 테이블 초기화"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 급여 설정 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payroll_settings (
            emp_id TEXT PRIMARY KEY,
            base_salary INTEGER NOT NULL DEFAULT 0,
            allowances TEXT,  -- JSON: {'식대': 200000, '교통비': 150000, ...}
            tax_free_items TEXT,  -- JSON: {'식대': true, ...}
            dependents INTEGER DEFAULT 1,
            hourly_wage REAL DEFAULT 0,
            work_hours INTEGER DEFAULT 209,
            is_inclusive_wage INTEGER DEFAULT 0,
            fixed_ot_hours REAL DEFAULT 0,
            fixed_ot_amount INTEGER DEFAULT 0,
            work_type TEXT DEFAULT '사무실 출퇴근',
            apply_pension INTEGER DEFAULT 1,
            apply_health INTEGER DEFAULT 1,
            apply_longterm INTEGER DEFAULT 1,
            apply_employment INTEGER DEFAULT 1,
            dc_pension_rate REAL DEFAULT 8.33,
            dc_pension_amount INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        )
        """)
        
        # 기존 테이블에 새 컬럼 추가 (없는 경우에만)
        try:
            cursor.execute("ALTER TABLE payroll_settings ADD COLUMN fixed_ot_amount INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE payroll_settings ADD COLUMN work_type TEXT DEFAULT '사무실 출퇴근'")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE payroll_settings ADD COLUMN apply_pension INTEGER DEFAULT 1")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE payroll_settings ADD COLUMN apply_health INTEGER DEFAULT 1")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE payroll_settings ADD COLUMN apply_longterm INTEGER DEFAULT 1")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE payroll_settings ADD COLUMN apply_employment INTEGER DEFAULT 1")
        except sqlite3.OperationalError:
            pass
        
        # 급여 지급 이력 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payroll_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            year_month TEXT NOT NULL,
            pay_date TEXT NOT NULL,
            base_salary INTEGER NOT NULL,
            total_allowance INTEGER DEFAULT 0,
            taxable_amount INTEGER NOT NULL,
            national_pension INTEGER DEFAULT 0,
            health_insurance INTEGER DEFAULT 0,
            longterm_care INTEGER DEFAULT 0,
            employment_insurance INTEGER DEFAULT 0,
            income_tax INTEGER DEFAULT 0,
            local_tax INTEGER DEFAULT 0,
            total_deduction INTEGER NOT NULL,
            net_pay INTEGER NOT NULL,
            payslip_data TEXT,  -- JSON: 전체 급여명세서 데이터
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            paid_status TEXT DEFAULT '미지급',  -- 미지급, 지급완료
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
            UNIQUE(emp_id, year_month)
        )
        """)
        
        # 연차 관리 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS annual_leave (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            year INTEGER NOT NULL,
            total_days INTEGER NOT NULL,
            used_days INTEGER DEFAULT 0,
            remaining_days INTEGER NOT NULL,
            leave_allowance INTEGER DEFAULT 0,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
            UNIQUE(emp_id, year)
        )
        """)
        
        # 연차 사용 이력 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS annual_leave_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            leave_date TEXT NOT NULL,
            days REAL NOT NULL,
            leave_type TEXT DEFAULT '연차',
            reason TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        )
        """)
        
        # 시간외 근무 기록 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS overtime_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            work_date TEXT NOT NULL,
            overtime_type TEXT NOT NULL,  -- 연장, 야간, 휴일
            hours REAL NOT NULL,
            hourly_wage REAL NOT NULL,
            overtime_pay INTEGER NOT NULL,
            approved_by TEXT,
            approved_at TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        )
        """)
        
        # 퇴직금 계산 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS retirement_pay (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            retirement_date TEXT NOT NULL,
            total_work_days INTEGER NOT NULL,
            average_wage REAL NOT NULL,
            retirement_amount INTEGER NOT NULL,
            paid_status TEXT DEFAULT '미지급',
            paid_date TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        )
        """)
        
        conn.commit()


# ============================================================
# 급여 설정 CRUD
# ============================================================

def add_payroll_setting(emp_id: str, settings: Dict) -> bool:
    """급여 설정 추가"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO payroll_settings 
            (emp_id, base_salary, allowances, tax_free_items, dependents, hourly_wage, work_hours,
             is_inclusive_wage, fixed_ot_hours, fixed_ot_amount, work_type,
             apply_pension, apply_health, apply_longterm, apply_employment, dc_pension_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                emp_id,
                settings.get('base_salary', 0),
                json.dumps(settings.get('allowances', {}), ensure_ascii=False),
                json.dumps(settings.get('tax_free_items', {}), ensure_ascii=False),
                settings.get('dependents', 1),
                settings.get('hourly_wage', 0),
                settings.get('work_hours', 209),
                int(settings.get('is_inclusive_wage', False)),  # Boolean to Integer
                settings.get('fixed_ot_hours', 0),
                settings.get('fixed_ot_amount', 0),
                settings.get('work_type', '사무실 출퇴근'),
                int(settings.get('apply_pension', True)),  # Boolean to Integer
                int(settings.get('apply_health', True)),  # Boolean to Integer
                int(settings.get('apply_longterm', True)),  # Boolean to Integer
                int(settings.get('apply_employment', True)),  # Boolean to Integer
                settings.get('dc_pension_rate', 8.33)
            ))
            
            return True
    except Exception as e:
        print(f"급여 설정 추가 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_payroll_setting(emp_id: str) -> Optional[Dict]:
    """급여 설정 조회"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM payroll_settings WHERE emp_id = ?
            """, (emp_id,))
            
            row = cursor.fetchone()
            if row:
                # sqlite3.Row는 딕셔너리처럼 접근하되, 컬럼이 없으면 KeyError 발생
                # 안전하게 접근하기 위해 try-except 사용
                def safe_get(key, default=None):
                    try:
                        return row[key]
                    except (KeyError, IndexError):
                        return default
                
                return {
                    'emp_id': row['emp_id'],
                    'base_salary': row['base_salary'],
                    'allowances': json.loads(row['allowances']) if row['allowances'] else {},
                    'tax_free_items': json.loads(row['tax_free_items']) if row['tax_free_items'] else {},
                    'dependents': row['dependents'],
                    'hourly_wage': row['hourly_wage'],
                    'work_hours': row['work_hours'],
                    'is_inclusive_wage': bool(safe_get('is_inclusive_wage', 0)),  # Integer to Boolean
                    'fixed_ot_hours': safe_get('fixed_ot_hours', 0),
                    'fixed_ot_amount': safe_get('fixed_ot_amount', 0),
                    'work_type': safe_get('work_type', '사무실 출퇴근'),
                    'apply_pension': bool(safe_get('apply_pension', 1)),  # Integer to Boolean
                    'apply_health': bool(safe_get('apply_health', 1)),  # Integer to Boolean
                    'apply_longterm': bool(safe_get('apply_longterm', 1)),  # Integer to Boolean
                    'apply_employment': bool(safe_get('apply_employment', 1)),  # Integer to Boolean
                    'dc_pension_rate': safe_get('dc_pension_rate', 8.33),
                    'dc_pension_amount': safe_get('dc_pension_amount', 0),
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
    except Exception as e:
        print(f"급여 설정 조회 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def update_payroll_setting(emp_id: str, settings: Dict) -> bool:
    """급여 설정 수정"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            UPDATE payroll_settings
            SET base_salary = ?, allowances = ?, tax_free_items = ?,
                dependents = ?, hourly_wage = ?, work_hours = ?,
                is_inclusive_wage = ?, fixed_ot_hours = ?, fixed_ot_amount = ?,
                work_type = ?, apply_pension = ?, apply_health = ?, 
                apply_longterm = ?, apply_employment = ?, dc_pension_rate = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE emp_id = ?
            """, (
                settings.get('base_salary', 0),
                json.dumps(settings.get('allowances', {}), ensure_ascii=False),
                json.dumps(settings.get('tax_free_items', {}), ensure_ascii=False),
                settings.get('dependents', 1),
                settings.get('hourly_wage', 0),
                settings.get('work_hours', 209),
                int(settings.get('is_inclusive_wage', False)),  # Boolean to Integer
                settings.get('fixed_ot_hours', 0),
                settings.get('fixed_ot_amount', 0),
                settings.get('work_type', '사무실 출퇴근'),
                int(settings.get('apply_pension', True)),  # Boolean to Integer
                int(settings.get('apply_health', True)),  # Boolean to Integer
                int(settings.get('apply_longterm', True)),  # Boolean to Integer
                int(settings.get('apply_employment', True)),  # Boolean to Integer
                settings.get('dc_pension_rate', 8.33),
                emp_id
            ))
            
            return cursor.rowcount > 0
    except Exception as e:
        print(f"급여 설정 수정 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_all_payroll_settings() -> List[Dict]:
    """모든 급여 설정 조회"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT ps.*, e.name, e.department, e.position
            FROM payroll_settings ps
            JOIN employees e ON ps.emp_id = e.emp_id
            WHERE e.is_active = 1
            ORDER BY e.department, e.name
            """)
            
            results = []
            for row in cursor.fetchall():
                # sqlite3.Row는 딕셔너리처럼 접근하되, 컬럼이 없으면 KeyError 발생
                # 안전하게 접근하기 위해 try-except 사용
                def safe_get(key, default=None):
                    try:
                        return row[key]
                    except (KeyError, IndexError):
                        return default
                
                results.append({
                    'emp_id': row['emp_id'],
                    'name': row['name'],
                    'department': row['department'],
                    'position': row['position'],
                    'base_salary': row['base_salary'],
                    'allowances': json.loads(row['allowances']) if row['allowances'] else {},
                    'tax_free_items': json.loads(row['tax_free_items']) if row['tax_free_items'] else {},
                    'dependents': row['dependents'],
                    'hourly_wage': row['hourly_wage'],
                    'work_hours': row['work_hours'],
                    'is_inclusive_wage': bool(safe_get('is_inclusive_wage', 0)),
                    'fixed_ot_hours': safe_get('fixed_ot_hours', 0),
                    'fixed_ot_amount': safe_get('fixed_ot_amount', 0),
                    'work_type': safe_get('work_type', '사무실 출퇴근'),
                    'apply_pension': bool(safe_get('apply_pension', 1)),
                    'apply_health': bool(safe_get('apply_health', 1)),
                    'apply_longterm': bool(safe_get('apply_longterm', 1)),
                    'apply_employment': bool(safe_get('apply_employment', 1)),
                    'dc_pension_rate': safe_get('dc_pension_rate', 8.33)
                })
            
            return results
    except Exception as e:
        print(f"급여 설정 전체 조회 실패: {e}")
        return []


# ============================================================
# 급여 지급 이력 CRUD
# ============================================================

def add_payroll_history(emp_id: str, payroll_data: Dict, year_month: str) -> bool:
    """급여 지급 이력 추가"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            pay_date = f"{year_month}-21"  # 기본 급여일
            
            cursor.execute("""
            INSERT INTO payroll_history
            (emp_id, year_month, pay_date, base_salary, total_allowance, taxable_amount,
             national_pension, health_insurance, longterm_care, employment_insurance,
             income_tax, local_tax, total_deduction, net_pay, payslip_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                emp_id,
                year_month,
                pay_date,
                payroll_data['지급내역']['기본급'],
                payroll_data['지급내역']['수당합계'],
                payroll_data['지급내역']['과세대상액'],
                payroll_data['공제내역']['국민연금'],
                payroll_data['공제내역']['건강보험'],
                payroll_data['공제내역']['장기요양'],
                payroll_data['공제내역']['고용보험'],
                payroll_data['공제내역']['소득세'],
                payroll_data['공제내역']['지방소득세'],
                payroll_data['공제내역']['공제합계'],
                payroll_data['실수령액'],
                json.dumps(payroll_data, ensure_ascii=False)
            ))
            
            return True
    except sqlite3.IntegrityError:
        # 이미 해당 월 급여가 존재하면 업데이트
        return update_payroll_history(emp_id, year_month, payroll_data)
    except Exception as e:
        print(f"급여 이력 추가 실패: {e}")
        return False


def update_payroll_history(emp_id: str, year_month: str, payroll_data: Dict) -> bool:
    """급여 지급 이력 수정"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            UPDATE payroll_history
            SET base_salary = ?, total_allowance = ?, taxable_amount = ?,
                national_pension = ?, health_insurance = ?, longterm_care = ?,
                employment_insurance = ?, income_tax = ?, local_tax = ?,
                total_deduction = ?, net_pay = ?, payslip_data = ?
            WHERE emp_id = ? AND year_month = ?
            """, (
                payroll_data['지급내역']['기본급'],
                payroll_data['지급내역']['수당합계'],
                payroll_data['지급내역']['과세대상액'],
                payroll_data['공제내역']['국민연금'],
                payroll_data['공제내역']['건강보험'],
                payroll_data['공제내역']['장기요양'],
                payroll_data['공제내역']['고용보험'],
                payroll_data['공제내역']['소득세'],
                payroll_data['공제내역']['지방소득세'],
                payroll_data['공제내역']['공제합계'],
                payroll_data['실수령액'],
                json.dumps(payroll_data, ensure_ascii=False),
                emp_id,
                year_month
            ))
            
            return cursor.rowcount > 0
    except Exception as e:
        print(f"급여 이력 수정 실패: {e}")
        return False


def get_payroll_history(emp_id: str, year_month: str) -> Optional[Dict]:
    """특정 월 급여 이력 조회"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM payroll_history
            WHERE emp_id = ? AND year_month = ?
            """, (emp_id, year_month))
            
            row = cursor.fetchone()
            if row:
                # payslip_data에서 상세 정보 추출
                payslip_data = json.loads(row['payslip_data']) if row['payslip_data'] else {}
                
                return {
                    'emp_id': row['emp_id'],
                    'year_month': row['year_month'],
                    'pay_date': row['pay_date'],
                    'base_salary': row['base_salary'],
                    'total_allowance': row['total_allowance'],
                    'taxable_amount': row['taxable_amount'],
                    'national_pension': row['national_pension'],
                    'health_insurance': row['health_insurance'],
                    'longterm_care': row['longterm_care'],
                    'employment_insurance': row['employment_insurance'],
                    'income_tax': row['income_tax'],
                    'local_tax': row['local_tax'],
                    'total_deduction': row['total_deduction'],
                    'net_pay': row['net_pay'],
                    'payslip_data': payslip_data,
                    'paid_status': row['paid_status'],
                    'created_at': row['created_at'],
                    # 수당 상세 정보 추출
                    'allowances': payslip_data.get('수당상세', {})
                }
            return None
    except Exception as e:
        print(f"급여 이력 조회 실패: {e}")
        return None


def get_employee_payroll_history(emp_id: str, limit: int = 12) -> List[Dict]:
    """직원별 급여 이력 조회 (최근 N개월)"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM payroll_history
            WHERE emp_id = ?
            ORDER BY year_month DESC
            LIMIT ?
            """, (emp_id, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'year_month': row['year_month'],
                    'pay_date': row['pay_date'],
                    'base_salary': row['base_salary'],
                    'total_allowance': row['total_allowance'],
                    'total_deduction': row['total_deduction'],
                    'net_pay': row['net_pay'],
                    'paid_status': row['paid_status']
                })
            
            return results
    except Exception as e:
        print(f"직원 급여 이력 조회 실패: {e}")
        return []


def get_monthly_payroll_summary(year_month: str) -> List[Dict]:
    """월별 급여 요약 (전 직원)"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT ph.*, e.name, e.department, e.position
            FROM payroll_history ph
            JOIN employees e ON ph.emp_id = e.emp_id
            WHERE ph.year_month = ?
            ORDER BY e.department, e.name
            """, (year_month,))
            
            results = []
            for row in cursor.fetchall():
                # payslip_data JSON 파싱
                payslip_data = json.loads(row['payslip_data']) if row['payslip_data'] else {}
                
                results.append({
                    'emp_id': row['emp_id'],
                    'name': row['name'],
                    'department': row['department'],
                    'position': row['position'],
                    'base_salary': row['base_salary'],
                    'total_allowance': row['total_allowance'],
                    'taxable_amount': row['taxable_amount'],
                    'national_pension': row['national_pension'],
                    'health_insurance': row['health_insurance'],
                    'longterm_care': row['longterm_care'],
                    'employment_insurance': row['employment_insurance'],
                    'income_tax': row['income_tax'],
                    'local_tax': row['local_tax'],
                    'total_deduction': row['total_deduction'],
                    'net_pay': row['net_pay'],
                    'paid_status': row['paid_status'],
                    'allowances': payslip_data.get('수당상세', {}),  # 개별 수당 내역
                    'payslip_data': payslip_data
                })
            
            return results
    except Exception as e:
        print(f"월별 급여 요약 조회 실패: {e}")
        return []


def update_paid_status(emp_id: str, year_month: str, status: str = '지급완료') -> bool:
    """급여 지급 상태 변경"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            UPDATE payroll_history
            SET paid_status = ?
            WHERE emp_id = ? AND year_month = ?
            """, (status, emp_id, year_month))
            
            return cursor.rowcount > 0
    except Exception as e:
        print(f"지급 상태 변경 실패: {e}")
        return False


# ============================================================
# 연차 관리
# ============================================================

def add_annual_leave(emp_id: str, year: int, total_days: int) -> bool:
    """연차 추가"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO annual_leave (emp_id, year, total_days, remaining_days)
            VALUES (?, ?, ?, ?)
            """, (emp_id, year, total_days, total_days))
            
            return True
    except Exception as e:
        print(f"연차 추가 실패: {e}")
        return False


def use_annual_leave(emp_id: str, year: int, days: int) -> bool:
    """연차 사용"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            UPDATE annual_leave
            SET used_days = used_days + ?,
                remaining_days = remaining_days - ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE emp_id = ? AND year = ?
            """, (days, days, emp_id, year))
            
            return cursor.rowcount > 0
    except Exception as e:
        print(f"연차 사용 실패: {e}")
        return False


def get_annual_leave(emp_id: str, year: int) -> Optional[Dict]:
    """연차 조회"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM annual_leave
            WHERE emp_id = ? AND year = ?
            """, (emp_id, year))
            
            row = cursor.fetchone()
            if row:
                return {
                    'emp_id': row['emp_id'],
                    'year': row['year'],
                    'total_days': row['total_days'],
                    'used_days': row['used_days'],
                    'remaining_days': row['remaining_days'],
                    'leave_allowance': row['leave_allowance'],
                    'notes': row['notes']
                }
            return None
    except Exception as e:
        print(f"연차 조회 실패: {e}")
        return None


def add_annual_leave_usage(emp_id: str, leave_date: str, days: float, leave_type: str = '연차', reason: str = None) -> bool:
    """연차 사용 이력 추가"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 연차 사용 이력 추가
            cursor.execute("""
            INSERT INTO annual_leave_usage (emp_id, leave_date, days, leave_type, reason)
            VALUES (?, ?, ?, ?, ?)
            """, (emp_id, leave_date, days, leave_type, reason))
            
            # 연차 테이블 업데이트
            year = int(leave_date[:4])
            cursor.execute("""
            UPDATE annual_leave
            SET used_days = used_days + ?,
                remaining_days = remaining_days - ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE emp_id = ? AND year = ?
            """, (days, days, emp_id, year))
            
            return True
    except Exception as e:
        print(f"연차 사용 이력 추가 실패: {e}")
        return False


def get_annual_leave_usage(emp_id: str, year: int = None) -> List[Dict]:
    """연차 사용 이력 조회"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            if year:
                cursor.execute("""
                SELECT * FROM annual_leave_usage
                WHERE emp_id = ? AND strftime('%Y', leave_date) = ?
                ORDER BY leave_date DESC
                """, (emp_id, str(year)))
            else:
                cursor.execute("""
                SELECT * FROM annual_leave_usage
                WHERE emp_id = ?
                ORDER BY leave_date DESC
                """, (emp_id,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'leave_date': row['leave_date'],
                    'days': row['days'],
                    'leave_type': row['leave_type'],
                    'reason': row['reason'],
                    'created_at': row['created_at']
                })
            
            return results
    except Exception as e:
        print(f"연차 사용 이력 조회 실패: {e}")
        return []


def init_annual_leave_if_not_exists(emp_id: str, year: int, total_days: int) -> bool:
    """연차가 없으면 초기화"""
    try:
        existing = get_annual_leave(emp_id, year)
        if not existing:
            return add_annual_leave(emp_id, year, total_days)
        return True
    except Exception as e:
        print(f"연차 초기화 실패: {e}")
        return False


# ============================================================
# 시간외 근무
# ============================================================

def add_overtime_log(emp_id: str, work_date: str, overtime_type: str, hours: float, overtime_pay: int) -> bool:
    """시간외 근무 추가"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 시간급 조회
            setting = get_payroll_setting(emp_id)
            hourly_wage = setting['hourly_wage'] if setting else 0
            
            cursor.execute("""
            INSERT INTO overtime_logs 
            (emp_id, work_date, overtime_type, hours, hourly_wage, overtime_pay)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (emp_id, work_date, overtime_type, hours, hourly_wage, overtime_pay))
            
            return True
    except Exception as e:
        print(f"시간외 근무 추가 실패: {e}")
        return False


def get_monthly_overtime(emp_id: str, year_month: str) -> List[Dict]:
    """월별 시간외 근무 조회"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM overtime_logs
            WHERE emp_id = ? AND strftime('%Y-%m', work_date) = ?
            ORDER BY work_date
            """, (emp_id, year_month))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'work_date': row['work_date'],
                    'overtime_type': row['overtime_type'],
                    'hours': row['hours'],
                    'overtime_pay': row['overtime_pay']
                })
            
            return results
    except Exception as e:
        print(f"시간외 근무 조회 실패: {e}")
        return []


# ============================================================
# 초기화
# ============================================================

if __name__ == "__main__":
    print("급여 관리 데이터베이스 초기화 중...")
    init_payroll_tables()
    print("✅ 초기화 완료!")
