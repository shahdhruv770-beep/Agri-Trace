import hashlib
import streamlit as st
from database import execute_query, fetch_one
import uuid

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_auth():
    """Initialize authentication system"""
    # Create default admin user if not exists
    admin_exists = fetch_one("SELECT id FROM users WHERE email = %s", ("admin@agritrace.com",))
    if not admin_exists:
        admin_password = hash_password("admin123")
        execute_query("""
            INSERT INTO users (name, email, phone, role, password_hash) 
            VALUES (%s, %s, %s, %s, %s)
        """, ("Admin User", "admin@agritrace.com", "1234567890", "Admin", admin_password))

def register_user(name, email, phone, role, password):
    """Register new user"""
    try:
        # Check if email already exists
        existing_user = fetch_one("SELECT id FROM users WHERE email = %s", (email,))
        if existing_user:
            return False, "Email already registered"
        
        password_hash = hash_password(password)
        result = execute_query("""
            INSERT INTO users (name, email, phone, role, password_hash) 
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, phone, role, password_hash))
        
        if result and result > 0:
            return True, "Registration successful"
        else:
            return False, "Registration failed"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def login_user(email, password):
    """Authenticate user login"""
    try:
        password_hash = hash_password(password)
        user = fetch_one("""
            SELECT id, name, email, role, status 
            FROM users 
            WHERE email = %s AND password_hash = %s AND status = 'active'
        """, (email, password_hash))
        
        if user:
            return True, dict(user)
        else:
            return False, None
            
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False, None

def logout_user():
    """Logout user and clear session"""
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_id = None
    st.session_state.username = None
    st.rerun()

def generate_batch_id():
    """Generate unique batch ID for crops"""
    return f"BATCH_{uuid.uuid4().hex[:8].upper()}"
