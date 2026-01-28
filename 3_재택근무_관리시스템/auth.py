"""
auth.py
Remote Work Management System - Authentication Module
Using argon2-cffi for secure password hashing
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
import streamlit as st
from typing import Optional, Dict
from database import get_user_by_username, add_system_log

# Initialize Argon2 Password Hasher
ph = PasswordHasher(
    time_cost=2,  # Number of iterations
    memory_cost=65536,  # 64 MB
    parallelism=1,  # Number of parallel threads
    hash_len=32,  # Length of hash
    salt_len=16  # Length of salt
)


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2
    Returns: Hashed password string
    """
    return ph.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """
    Verify a password against its hash
    Returns: True if password matches, False otherwise
    """
    try:
        ph.verify(password_hash, password)
        return True
    except (VerifyMismatchError, InvalidHash):
        return False


def init_session_state():
    """Initialize Streamlit session state for authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'full_name' not in st.session_state:
        st.session_state.full_name = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None


def login(username: str, password: str) -> tuple[bool, str]:
    """
    Authenticate user with username and password
    Returns: (success: bool, message: str)
    """
    if not username or not password:
        return False, "사용자 ID와 비밀번호를 입력해주세요."
    
    user = get_user_by_username(username)
    
    if not user:
        add_system_log(username, "로그인 실패", "존재하지 않는 사용자")
        return False, "잘못된 사용자 ID 또는 비밀번호입니다."
    
    if not user['is_active']:
        add_system_log(username, "로그인 실패", "비활성 계정")
        return False, "비활성화된 계정입니다. 관리자에게 문의하세요."
    
    # Verify password
    if verify_password(user['password_hash'], password):
        # Set session state
        st.session_state.authenticated = True
        st.session_state.username = user['username']
        st.session_state.full_name = user['full_name']
        st.session_state.role = user['role']
        st.session_state.user_id = user['id']
        
        # Log successful login
        add_system_log(username, "로그인 성공", f"{user['full_name']} ({user['role']})")
        
        return True, f"환영합니다, {user['full_name']}님!"
    else:
        add_system_log(username, "로그인 실패", "잘못된 비밀번호")
        return False, "잘못된 사용자 ID 또는 비밀번호입니다."


def logout():
    """Logout current user"""
    username = st.session_state.get('username', 'Unknown')
    add_system_log(username, "로그아웃", "")
    
    # Clear session state
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.full_name = None
    st.session_state.role = None
    st.session_state.user_id = None


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)


def is_admin() -> bool:
    """Check if current user is admin"""
    return st.session_state.get('role') == 'admin'


def require_auth(func):
    """Decorator to require authentication"""
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            st.warning("⚠️ 로그인이 필요합니다.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper


def require_admin(func):
    """Decorator to require admin role"""
    def wrapper(*args, **kwargs):
        if not is_admin():
            st.error("🚫 관리자 권한이 필요합니다.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper


def get_current_user() -> Optional[Dict]:
    """Get current logged-in user info"""
    if not is_authenticated():
        return None
    
    return {
        'username': st.session_state.username,
        'full_name': st.session_state.full_name,
        'role': st.session_state.role,
        'user_id': st.session_state.user_id
    }


def login_page():
    """Render login page"""
    st.markdown("""
    <style>
    .login-container {
        max-width: 420px;
        margin: 80px auto;
        padding: 50px;
        background: linear-gradient(135deg, #7D9B76 0%, #6A8A63 100%);
        border-radius: 20px;
        box-shadow: 0 15px 50px rgba(74, 93, 68, 0.3);
    }
    .login-title {
        color: white;
        text-align: center;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .login-subtitle {
        color: #F5F5DC;
        text-align: center;
        font-size: 15px;
        margin-bottom: 30px;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">🏢 재택근무 관리 시스템</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Remote Work Management System v2.0</div>', unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 사용자 ID", placeholder="admin")
            password = st.text_input("🔒 비밀번호", type="password", placeholder="••••••••")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                login_button = st.form_submit_button("🚀 로그인", use_container_width=True)
            with col_btn2:
                if st.form_submit_button("❓ 도움말", use_container_width=True):
                    st.info("""
                    **🔑 기본 계정**
                    
                    **관리자:**
                    - ID: admin
                    - PW: admin1234
                    
                    **일반 직원 (송미):**
                    - ID: songmi
                    - PW: songmi1234
                    """)
            
            if login_button:
                success, message = login(username, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 12px; margin-top: 30px;'>
        Powered by Streamlit | Secured by Argon2
        </div>
        """, unsafe_allow_html=True)
