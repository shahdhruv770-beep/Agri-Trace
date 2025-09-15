import streamlit as st
import os
from auth import init_auth, login_user, register_user, logout_user
from database import init_database
from components.navigation import render_navigation
from pages import farmer_dashboard, distributor_dashboard, retailer_dashboard, buyer_dashboard, admin_dashboard

# Initialize database
init_database()
init_auth()

# App configuration
st.set_page_config(
    page_title="AgriTrace - Farm to Table Traceability",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #22c55e 0%, #65a30d 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .stButton > button {
        background: linear-gradient(90deg, #22c55e 0%, #16a34a 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .role-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #22c55e;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None

    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🌾 AgriTrace - Farm to Table Traceability</h1>
        <p>Transparent agricultural supply chain tracking system</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.authenticated:
        render_auth_page()
    else:
        render_navigation()
        render_dashboard()

def render_auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            st.subheader("Login to AgriTrace")
            
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                if st.button("🔐 Login", use_container_width=True):
                    if email and password:
                        success, user_data = login_user(email, password)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.user_role = user_data['role']
                            st.session_state.user_id = user_data['id']
                            st.session_state.username = user_data['name']
                            st.success(f"Welcome back, {user_data['name']}!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Please try again.")
                    else:
                        st.warning("Please fill in all fields.")
        
        with tab2:
            st.subheader("Register for AgriTrace")
            
            name = st.text_input("Full Name", placeholder="Enter your full name")
            reg_email = st.text_input("Email Address", placeholder="Enter your email")
            phone = st.text_input("Phone Number", placeholder="Enter your phone number")
            role = st.selectbox("Select Your Role", 
                              ["Farmer", "Distributor", "Retailer", "Buyer", "Admin"])
            reg_password = st.text_input("Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                if st.button("📝 Register", use_container_width=True):
                    if all([name, reg_email, phone, role, reg_password, confirm_password]):
                        if reg_password == confirm_password:
                            success, message = register_user(name, reg_email, phone, role, reg_password)
                            if success:
                                st.success("Registration successful! Please login with your credentials.")
                            else:
                                st.error(message)
                        else:
                            st.error("Passwords do not match.")
                    else:
                        st.warning("Please fill in all fields.")

def render_dashboard():
    if st.session_state.user_role == "Farmer":
        farmer_dashboard.render()
    elif st.session_state.user_role == "Distributor":
        distributor_dashboard.render()
    elif st.session_state.user_role == "Retailer":
        retailer_dashboard.render()
    elif st.session_state.user_role == "Buyer":
        buyer_dashboard.render()
    elif st.session_state.user_role == "Admin":
        admin_dashboard.render()

if __name__ == "__main__":
    main()
