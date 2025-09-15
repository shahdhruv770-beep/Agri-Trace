import streamlit as st
from auth import logout_user

def render_navigation():
    """Render navigation sidebar"""
    with st.sidebar:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            color: white;
            margin-bottom: 1rem;
        ">
            <h3 style="margin: 0;">Welcome!</h3>
            <p style="margin: 0.5rem 0 0 0;">{st.session_state.username}</p>
            <small>Role: {st.session_state.user_role}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Role-based navigation
        if st.session_state.user_role == "Farmer":
            render_farmer_menu()
        elif st.session_state.user_role == "Distributor":
            render_distributor_menu()
        elif st.session_state.user_role == "Retailer":
            render_retailer_menu()
        elif st.session_state.user_role == "Buyer":
            render_buyer_menu()
        elif st.session_state.user_role == "Admin":
            render_admin_menu()
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()

def render_farmer_menu():
    """Render farmer navigation menu"""
    st.markdown("### 🌾 Farmer Dashboard")
    
    if 'farmer_page' not in st.session_state:
        st.session_state.farmer_page = 'overview'
    
    if st.button("📊 Overview", use_container_width=True):
        st.session_state.farmer_page = 'overview'
        st.rerun()
    
    if st.button("🌱 Add Crop", use_container_width=True):
        st.session_state.farmer_page = 'add_crop'
        st.rerun()
    
    if st.button("📦 My Crops", use_container_width=True):
        st.session_state.farmer_page = 'my_crops'
        st.rerun()
    
    if st.button("💰 Payments", use_container_width=True):
        st.session_state.farmer_page = 'payments'
        st.rerun()
    
    if st.button("📱 QR Codes", use_container_width=True):
        st.session_state.farmer_page = 'qr_codes'
        st.rerun()

def render_distributor_menu():
    """Render distributor navigation menu"""
    st.markdown("### 🚚 Distributor Dashboard")
    
    if 'distributor_page' not in st.session_state:
        st.session_state.distributor_page = 'overview'
    
    if st.button("📊 Overview", use_container_width=True):
        st.session_state.distributor_page = 'overview'
        st.rerun()
    
    if st.button("🌾 Available Crops", use_container_width=True):
        st.session_state.distributor_page = 'available_crops'
        st.rerun()
    
    if st.button("🚛 My Deliveries", use_container_width=True):
        st.session_state.distributor_page = 'deliveries'
        st.rerun()
    
    if st.button("📋 Transport", use_container_width=True):
        st.session_state.distributor_page = 'transport'
        st.rerun()
    
    if st.button("💰 Payments", use_container_width=True):
        st.session_state.distributor_page = 'payments'
        st.rerun()

def render_retailer_menu():
    """Render retailer navigation menu"""
    st.markdown("### 🛒 Retailer Dashboard")
    
    if 'retailer_page' not in st.session_state:
        st.session_state.retailer_page = 'overview'
    
    if st.button("📊 Overview", use_container_width=True):
        st.session_state.retailer_page = 'overview'
        st.rerun()
    
    if st.button("📦 Deliveries", use_container_width=True):
        st.session_state.retailer_page = 'deliveries'
        st.rerun()
    
    if st.button("🏪 My Stock", use_container_width=True):
        st.session_state.retailer_page = 'stock'
        st.rerun()
    
    if st.button("📈 Sales", use_container_width=True):
        st.session_state.retailer_page = 'sales'
        st.rerun()
    
    if st.button("💰 Payments", use_container_width=True):
        st.session_state.retailer_page = 'payments'
        st.rerun()

def render_buyer_menu():
    """Render buyer navigation menu"""
    st.markdown("### 👥 Consumer Dashboard")
    
    if 'buyer_page' not in st.session_state:
        st.session_state.buyer_page = 'scan'
    
    if st.button("📱 Scan QR", use_container_width=True):
        st.session_state.buyer_page = 'scan'
        st.rerun()
    
    if st.button("🔍 Trace History", use_container_width=True):
        st.session_state.buyer_page = 'history'
        st.rerun()
    
    if st.button("⭐ Feedback", use_container_width=True):
        st.session_state.buyer_page = 'feedback'
        st.rerun()

def render_admin_menu():
    """Render admin navigation menu"""
    st.markdown("### 🛠️ Admin Dashboard")
    
    if 'admin_page' not in st.session_state:
        st.session_state.admin_page = 'analytics'
    
    if st.button("📊 Analytics", use_container_width=True):
        st.session_state.admin_page = 'analytics'
        st.rerun()
    
    if st.button("👥 Users", use_container_width=True):
        st.session_state.admin_page = 'users'
        st.rerun()
    
    if st.button("🌾 Crops", use_container_width=True):
        st.session_state.admin_page = 'crops'
        st.rerun()
    
    if st.button("💰 Payments", use_container_width=True):
        st.session_state.admin_page = 'payments'
        st.rerun()
    
    if st.button("📈 Reports", use_container_width=True):
        st.session_state.admin_page = 'reports'
        st.rerun()
