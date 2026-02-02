"""
통합 인증 모듈
Authentication Module for HR Automation System

사용자 인증, 세션 관리, 권한 관리
"""

import hashlib
import secrets
from typing import Optional, Dict
from datetime import datetime
from .database import get_db, add_system_log


def hash_password(password: str, salt: Optional[str] = None) -> tuple:
    """
    비밀번호 해싱
    
    Args:
        password: 평문 비밀번호
        salt: 솔트 (없으면 자동 생성)
    
    Returns:
        (해시된 비밀번호, 솔트) 튜플
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    # SHA256 해싱
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return pwd_hash, salt


def verify_password(password: str, stored_hash: str) -> bool:
    """
    비밀번호 검증
    
    Args:
        password: 입력된 평문 비밀번호
        stored_hash: 저장된 해시 (format: hash:salt)
    
    Returns:
        검증 성공 여부
    """
    try:
        if ':' in stored_hash:
            pwd_hash, salt = stored_hash.split(':', 1)
        else:
            # 구버전 호환 (salt 없는 경우)
            pwd_hash = stored_hash
            salt = ""
        
        new_hash, _ = hash_password(password, salt)
        return new_hash == pwd_hash
    except Exception:
        return False


def create_user(username: str, password: str, emp_id: str = None, 
                role: str = 'employee', full_name: str = None) -> bool:
    """
    사용자 생성
    
    Args:
        username: 사용자명
        password: 비밀번호
        emp_id: 직원 ID
        role: 역할 (admin, hr, manager, employee)
        full_name: 전체 이름
    
    Returns:
        생성 성공 여부
    """
    try:
        pwd_hash, salt = hash_password(password)
        password_hash = f"{pwd_hash}:{salt}"
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO users (username, password_hash, emp_id, role)
            VALUES (?, ?, ?, ?)
            """, (username, password_hash, emp_id, role))
            conn.commit()
        
        add_system_log("system", f"사용자 생성: {username}", "auth", f"역할: {role}")
        return True
    
    except Exception as e:
        print(f"사용자 생성 실패: {e}")
        return False


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    사용자 인증
    
    Args:
        username: 사용자명
        password: 비밀번호
    
    Returns:
        인증 성공 시 사용자 정보 딕셔너리, 실패 시 None
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT u.*, e.name as emp_name, e.department, e.position
        FROM users u
        LEFT JOIN employees e ON u.emp_id = e.emp_id
        WHERE u.username = ? AND u.is_active = 1
        """, (username,))
        
        user = cursor.fetchone()
        
        if user and verify_password(password, user['password_hash']):
            # 마지막 로그인 시간 업데이트
            cursor.execute("""
            UPDATE users SET last_login = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (user['id'],))
            conn.commit()
            
            add_system_log(username, "로그인", "auth")
            
            # 비밀번호 해시 제외하고 반환
            user_dict = dict(user)
            user_dict.pop('password_hash', None)
            return user_dict
        
        return None


def check_permission(user: Dict, required_role: str) -> bool:
    """
    권한 확인
    
    Args:
        user: 사용자 정보 딕셔너리
        required_role: 요구되는 역할
    
    Returns:
        권한 보유 여부
    """
    role_hierarchy = {
        'admin': 4,
        'hr': 3,
        'manager': 2,
        'employee': 1
    }
    
    user_level = role_hierarchy.get(user.get('role'), 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    return user_level >= required_level


def get_user_by_username(username: str) -> Optional[Dict]:
    """
    사용자명으로 사용자 정보 조회
    
    Args:
        username: 사용자명
    
    Returns:
        사용자 정보 딕셔너리 또는 None
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT u.*, e.name as emp_name, e.department, e.position
        FROM users u
        LEFT JOIN employees e ON u.emp_id = e.emp_id
        WHERE u.username = ?
        """, (username,))
        
        user = cursor.fetchone()
        if user:
            user_dict = dict(user)
            user_dict.pop('password_hash', None)
            return user_dict
        
        return None


def change_password(username: str, old_password: str, new_password: str) -> bool:
    """
    비밀번호 변경
    
    Args:
        username: 사용자명
        old_password: 기존 비밀번호
        new_password: 새 비밀번호
    
    Returns:
        변경 성공 여부
    """
    # 기존 비밀번호 확인
    user = authenticate_user(username, old_password)
    if not user:
        return False
    
    try:
        pwd_hash, salt = hash_password(new_password)
        password_hash = f"{pwd_hash}:{salt}"
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE users SET password_hash = ?
            WHERE username = ?
            """, (password_hash, username))
            conn.commit()
        
        add_system_log(username, "비밀번호 변경", "auth")
        return True
    
    except Exception as e:
        print(f"비밀번호 변경 실패: {e}")
        return False


def init_default_users():
    """
    기본 사용자 생성 (admin, 테스트 사용자)
    """
    # admin 사용자 생성
    admin_exists = get_user_by_username('admin')
    if not admin_exists:
        create_user('admin', 'admin1234', role='admin')
        print("✅ 관리자 계정 생성 완료 (ID: admin, PW: admin1234)")
    
    # 테스트 사용자 생성
    test_exists = get_user_by_username('test')
    if not test_exists:
        create_user('test', 'test1234', role='employee')
        print("✅ 테스트 계정 생성 완료 (ID: test, PW: test1234)")


if __name__ == "__main__":
    # 테스트
    from .database import init_master_database
    
    init_master_database()
    init_default_users()
    
    # 인증 테스트
    user = authenticate_user('admin', 'admin1234')
    if user:
        print(f"\n✅ 인증 성공: {user['username']} ({user['role']})")
    else:
        print("\n❌ 인증 실패")
