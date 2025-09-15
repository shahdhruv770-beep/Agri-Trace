import streamlit as st
from database import execute_query, fetch_one
from utils import create_user_card, create_crop_card, create_payment_card
from components.charts import create_analytics_overview, create_pie_chart, create_line_chart
import pandas as pd
from datetime import datetime, timedelta

def render():
    """Render admin dashboard"""
    page = st.session_state.get('admin_page', 'analytics')
    
    if page == 'analytics':
        render_analytics()
    elif page == 'users':
        render_users()
    elif page == 'crops':
        render_crops()
    elif page == 'payments':
        render_payments()
    elif page == 'reports':
        render_reports()

def render_analytics():
    """Render analytics overview"""
    st.markdown("## 📊 System Analytics")
    
    # Get system statistics
    total_users = fetch_one("SELECT COUNT(*) as count FROM users")
    total_crops = fetch_one("SELECT COUNT(*) as count FROM crops")
    total_payments_amount = fetch_one("SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE payment_status = 'completed'")
    pending_deliveries = fetch_one("SELECT COUNT(*) as count FROM deliveries WHERE status IN ('pending', 'in_transit')")
    
    # Display overview cards
    create_analytics_overview(
        total_users['count'] if total_users else 0,
        total_crops['count'] if total_crops else 0,
        total_payments_amount['total'] if total_payments_amount else 0,
        pending_deliveries['count'] if pending_deliveries else 0
    )
    
    st.markdown("---")
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        # User distribution pie chart
        st.markdown("### 👥 User Distribution by Role")
        user_roles = execute_query("""
            SELECT role, COUNT(*) as count 
            FROM users 
            GROUP BY role
        """, fetch=True)
        
        if user_roles:
            role_data = {row['role']: row['count'] for row in user_roles}
            create_pie_chart(role_data, "Users by Role")
        else:
            st.info("No user data available")
    
    with col2:
        # Crop distribution pie chart
        st.markdown("### 🌾 Crops by Type")
        crop_types = execute_query("""
            SELECT type, COUNT(*) as count 
            FROM crops 
            GROUP BY type
        """, fetch=True)
        
        if crop_types:
            crop_data = {row['type']: row['count'] for row in crop_types}
            create_pie_chart(crop_data, "Crops by Type")
        else:
            st.info("No crop data available")
    
    # Payment trends
    st.markdown("### 💰 Payment Trends (Last 30 Days)")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    payment_trends = execute_query("""
        SELECT DATE(created_at) as payment_date, SUM(amount) as daily_amount
        FROM payments 
        WHERE created_at >= %s AND payment_status = 'completed'
        GROUP BY DATE(created_at)
        ORDER BY payment_date
    """, (start_date,), fetch=True)
    
    if payment_trends:
        trend_data = [{'date': row['payment_date'].strftime('%Y-%m-%d'), 'amount': float(row['daily_amount'])} for row in payment_trends]
        create_line_chart(trend_data, 'date', 'amount', 'Daily Payment Volume')
    else:
        st.info("No payment trend data available")
    
    # Recent activity summary
    st.markdown("---")
    st.markdown("### 📈 Recent Activity Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        recent_users = fetch_one("SELECT COUNT(*) as count FROM users WHERE created_at >= %s", (start_date,))
        st.metric("👥 New Users (30d)", recent_users['count'] if recent_users else 0)
    
    with col2:
        recent_crops = fetch_one("SELECT COUNT(*) as count FROM crops WHERE created_at >= %s", (start_date,))
        st.metric("🌾 New Crops (30d)", recent_crops['count'] if recent_crops else 0)
    
    with col3:
        recent_transactions = fetch_one("SELECT COUNT(*) as count FROM transactions WHERE created_at >= %s", (start_date,))
        st.metric("🔄 Transactions (30d)", recent_transactions['count'] if recent_transactions else 0)
    
    with col4:
        active_deliveries = fetch_one("SELECT COUNT(*) as count FROM deliveries WHERE status = 'in_transit'")
        st.metric("🚛 Active Deliveries", active_deliveries['count'] if active_deliveries else 0)

def render_users():
    """Render user management"""
    st.markdown("## 👥 User Management")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        role_filter = st.selectbox("Filter by Role", ["All", "Farmer", "Distributor", "Retailer", "Buyer", "Admin"])
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "active", "inactive", "pending"])
    with col3:
        search_term = st.text_input("Search Users", placeholder="Search by name or email...")
    
    # Build query
    query = "SELECT * FROM users WHERE 1=1"
    params = []
    
    if role_filter != "All":
        query += " AND role = %s"
        params.append(role_filter)
    
    if status_filter != "All":
        query += " AND status = %s"
        params.append(status_filter)
    
    if search_term:
        query += " AND (LOWER(name) LIKE %s OR LOWER(email) LIKE %s)"
        params.extend([f"%{search_term.lower()}%", f"%{search_term.lower()}%"])
    
    query += " ORDER BY created_at DESC"
    
    users = execute_query(query, params, fetch=True)
    
    if users:
        # User statistics
        total_users = len(users)
        active_users = len([u for u in users if u['status'] == 'active'])
        pending_users = len([u for u in users if u['status'] == 'pending'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👥 Total Users", total_users)
        with col2:
            st.metric("✅ Active Users", active_users)
        with col3:
            st.metric("⏳ Pending Approval", pending_users)
        
        st.markdown("---")
        
        # User list
        for user in users:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                status_color = {
                    'active': '#22c55e',
                    'pending': '#f59e0b',
                    'inactive': '#ef4444'
                }.get(user['status'], '#6b7280')
                
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 1.5rem;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    margin: 1rem 0;
                    border-left: 4px solid {status_color};
                ">
                    <h3 style="color: #1f2937; margin: 0 0 0.5rem 0;">{user['name']}</h3>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Email:</strong> {user['email']}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Phone:</strong> {user.get('phone', 'N/A')}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Role:</strong> {user['role']}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Joined:</strong> {user['created_at'].strftime('%Y-%m-%d')}</p>
                    <span style="
                        background: {status_color};
                        color: white;
                        padding: 0.25rem 0.75rem;
                        border-radius: 20px;
                        font-size: 0.875rem;
                    ">
                        {user['status'].title()}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                
                if user['status'] == 'pending':
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"✅ Approve", key=f"approve_{user['id']}"):
                            approve_user(user['id'])
                    with col_b:
                        if st.button(f"❌ Reject", key=f"reject_{user['id']}"):
                            reject_user(user['id'])
                
                elif user['status'] == 'active':
                    if st.button(f"🔒 Deactivate", key=f"deactivate_{user['id']}"):
                        deactivate_user(user['id'])
                
                elif user['status'] == 'inactive':
                    if st.button(f"🔓 Activate", key=f"activate_{user['id']}"):
                        activate_user(user['id'])
                
                # View details button
                if st.button(f"👁️ View Details", key=f"view_{user['id']}"):
                    show_user_details(user)
    else:
        st.info("No users found matching your criteria.")

def approve_user(user_id):
    """Approve a pending user"""
    result = execute_query("UPDATE users SET status = 'active' WHERE id = %s", (user_id,))
    if result:
        st.success("✅ User approved successfully!")
        st.rerun()
    else:
        st.error("Failed to approve user.")

def reject_user(user_id):
    """Reject a pending user"""
    result = execute_query("UPDATE users SET status = 'inactive' WHERE id = %s", (user_id,))
    if result:
        st.success("❌ User rejected successfully!")
        st.rerun()
    else:
        st.error("Failed to reject user.")

def deactivate_user(user_id):
    """Deactivate an active user"""
    result = execute_query("UPDATE users SET status = 'inactive' WHERE id = %s", (user_id,))
    if result:
        st.success("🔒 User deactivated successfully!")
        st.rerun()
    else:
        st.error("Failed to deactivate user.")

def activate_user(user_id):
    """Activate an inactive user"""
    result = execute_query("UPDATE users SET status = 'active' WHERE id = %s", (user_id,))
    if result:
        st.success("🔓 User activated successfully!")
        st.rerun()
    else:
        st.error("Failed to activate user.")

def show_user_details(user):
    """Show detailed user information"""
    with st.expander(f"👁️ Details for {user['name']}", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Information:**")
            st.write(f"**ID:** {user['id']}")
            st.write(f"**Name:** {user['name']}")
            st.write(f"**Email:** {user['email']}")
            st.write(f"**Phone:** {user.get('phone', 'N/A')}")
            st.write(f"**Role:** {user['role']}")
            st.write(f"**Status:** {user['status']}")
            st.write(f"**Joined:** {user['created_at'].strftime('%Y-%m-%d %H:%M')}")
        
        with col2:
            st.markdown("**Activity Summary:**")
            
            if user['role'] == 'Farmer':
                crops_count = fetch_one("SELECT COUNT(*) as count FROM crops WHERE farmer_id = %s", (user['id'],))
                st.write(f"**Crops Added:** {crops_count['count'] if crops_count else 0}")
            
            elif user['role'] == 'Distributor':
                deliveries_count = fetch_one("SELECT COUNT(*) as count FROM deliveries WHERE distributor_id = %s", (user['id'],))
                st.write(f"**Deliveries:** {deliveries_count['count'] if deliveries_count else 0}")
            
            elif user['role'] == 'Retailer':
                received_deliveries = fetch_one("SELECT COUNT(*) as count FROM deliveries WHERE retailer_id = %s", (user['id'],))
                st.write(f"**Received Deliveries:** {received_deliveries['count'] if received_deliveries else 0}")
            
            # Payment summary
            payments_received = fetch_one("SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE to_user_id = %s AND payment_status = 'completed'", (user['id'],))
            payments_made = fetch_one("SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE from_user_id = %s AND payment_status = 'completed'", (user['id'],))
            
            st.write(f"**Payments Received:** ₹{payments_received['total'] if payments_received else 0:,.0f}")
            st.write(f"**Payments Made:** ₹{payments_made['total'] if payments_made else 0:,.0f}")

def render_crops():
    """Render crop management"""
    st.markdown("## 🌾 Crop Management")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.selectbox("Filter by Type", ["All", "Cereals", "Vegetables", "Fruits", "Pulses", "Spices", "Other"])
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "available", "in_transit", "delivered", "sold"])
    with col3:
        search_term = st.text_input("Search Crops", placeholder="Search by name or batch ID...")
    
    # Build query
    query = """
        SELECT c.*, u.name as farmer_name, u.email as farmer_email
        FROM crops c
        LEFT JOIN users u ON c.farmer_id = u.id
        WHERE 1=1
    """
    params = []
    
    if type_filter != "All":
        query += " AND c.type = %s"
        params.append(type_filter)
    
    if status_filter != "All":
        query += " AND c.status = %s"
        params.append(status_filter)
    
    if search_term:
        query += " AND (LOWER(c.name) LIKE %s OR LOWER(c.batch_id) LIKE %s)"
        params.extend([f"%{search_term.lower()}%", f"%{search_term.lower()}%"])
    
    query += " ORDER BY c.created_at DESC"
    
    crops = execute_query(query, params, fetch=True)
    
    if crops:
        # Crop statistics
        total_crops = len(crops)
        available_crops = len([c for c in crops if c['status'] == 'available'])
        total_value = sum([c['price'] * c['quantity'] for c in crops])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌾 Total Crops", total_crops)
        with col2:
            st.metric("📦 Available", available_crops)
        with col3:
            st.metric("💰 Total Value", f"₹{total_value:,.0f}")
        
        st.markdown("---")
        
        # Crop list
        for crop in crops:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                status_color = {
                    'available': '#22c55e',
                    'in_transit': '#3b82f6',
                    'delivered': '#f59e0b',
                    'sold': '#8b5cf6'
                }.get(crop['status'], '#6b7280')
                
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 1.5rem;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    margin: 1rem 0;
                    border-left: 4px solid {status_color};
                ">
                    <h3 style="color: #1f2937; margin: 0 0 0.5rem 0;">{crop['name']}</h3>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Type:</strong> {crop['type']}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Farmer:</strong> {crop['farmer_name']}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Quantity:</strong> {crop['quantity']} kg</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Price:</strong> ₹{crop['price']}/kg</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Value:</strong> ₹{crop['price'] * crop['quantity']:,.0f}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Batch ID:</strong> {crop['batch_id']}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Harvest Date:</strong> {crop['harvest_date']}</p>
                    <span style="
                        background: {status_color};
                        color: white;
                        padding: 0.25rem 0.75rem;
                        border-radius: 20px;
                        font-size: 0.875rem;
                    ">
                        {crop['status'].title()}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                
                if st.button(f"📍 Track", key=f"track_{crop['id']}"):
                    show_crop_traceability(crop)
                
                if st.button(f"📧 Contact Farmer", key=f"contact_{crop['id']}"):
                    st.info(f"Contact {crop['farmer_name']} at {crop['farmer_email']}")
    else:
        st.info("No crops found matching your criteria.")

def show_crop_traceability(crop):
    """Show crop traceability information"""
    with st.expander(f"📍 Traceability for {crop['name']} ({crop['batch_id']})", expanded=True):
        traceability = execute_query("""
            SELECT t.*, u.name as user_name, u.role
            FROM traceability t
            LEFT JOIN users u ON t.user_id = u.id
            WHERE t.batch_id = %s
            ORDER BY t.timestamp ASC
        """, (crop['batch_id'],), fetch=True)
        
        if traceability:
            for step in traceability:
                st.markdown(f"""
                **{step['step_type']}** - {step['user_name']} ({step['role']})  
                {step['details'] if step['details'] else 'No additional details'}  
                📅 {step['timestamp'].strftime('%Y-%m-%d %H:%M')}
                """)
                st.markdown("---")
        else:
            st.info("No traceability information available for this crop.")

def render_payments():
    """Render payment management"""
    st.markdown("## 💰 Payment Management")
    
    # Payment overview
    total_payments = fetch_one("SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE payment_status = 'completed'")
    pending_payments = fetch_one("SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE payment_status = 'pending'")
    failed_payments = fetch_one("SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE payment_status = 'failed'")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Completed Payments", f"₹{total_payments['total'] if total_payments else 0:,.0f}")
    with col2:
        st.metric("⏳ Pending Payments", f"₹{pending_payments['total'] if pending_payments else 0:,.0f}")
    with col3:
        st.metric("❌ Failed Payments", f"₹{failed_payments['total'] if failed_payments else 0:,.0f}")
    
    st.markdown("---")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "completed", "pending", "failed"])
    with col2:
        date_range = st.selectbox("Date Range", ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"])
    
    # Build query
    query = """
        SELECT p.*, 
               u1.name as from_user_name, u1.role as from_user_role,
               u2.name as to_user_name, u2.role as to_user_role,
               c.name as crop_name
        FROM payments p
        LEFT JOIN users u1 ON p.from_user_id = u1.id
        LEFT JOIN users u2 ON p.to_user_id = u2.id
        LEFT JOIN crops c ON p.crop_id = c.id
        WHERE 1=1
    """
    params = []
    
    if status_filter != "All":
        query += " AND p.payment_status = %s"
        params.append(status_filter)
    
    if date_range != "All Time":
        days = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}[date_range]
        cutoff_date = datetime.now() - timedelta(days=days)
        query += " AND p.created_at >= %s"
        params.append(cutoff_date)
    
    query += " ORDER BY p.created_at DESC LIMIT 50"
    
    payments = execute_query(query, params, fetch=True)
    
    if payments:
        for payment in payments:
            status_color = {
                'completed': '#22c55e',
                'pending': '#f59e0b',
                'failed': '#ef4444'
            }.get(payment['payment_status'], '#6b7280')
            
            st.markdown(f"""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin: 1rem 0;
                border-left: 4px solid {status_color};
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="margin: 0; color: #1f2937;">₹{payment['amount']:,.0f}</h3>
                        <p style="margin: 0.25rem 0; color: #6b7280;">
                            <strong>From:</strong> {payment['from_user_name']} ({payment['from_user_role']})
                        </p>
                        <p style="margin: 0.25rem 0; color: #6b7280;">
                            <strong>To:</strong> {payment['to_user_name']} ({payment['to_user_role']})
                        </p>
                        <p style="margin: 0.25rem 0; color: #6b7280;">
                            <strong>Crop:</strong> {payment.get('crop_name', 'N/A')}
                        </p>
                        <p style="margin: 0.25rem 0; color: #6b7280;">
                            <strong>Method:</strong> {payment.get('payment_method', 'N/A')}
                        </p>
                        <small style="color: #9ca3af;">
                            {payment['created_at'].strftime('%Y-%m-%d %H:%M')}
                        </small>
                    </div>
                    <span style="
                        background: {status_color};
                        color: white;
                        padding: 0.5rem 1rem;
                        border-radius: 20px;
                        font-size: 0.875rem;
                    ">
                        {payment['payment_status'].title()}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No payments found matching your criteria.")

def render_reports():
    """Render system reports"""
    st.markdown("## 📈 System Reports")
    
    # Report type selection
    report_type = st.selectbox("Select Report Type", [
        "Supply Chain Performance",
        "User Activity Summary",
        "Financial Overview",
        "Crop Production Analysis",
        "Quality Metrics"
    ])
    
    if report_type == "Supply Chain Performance":
        render_supply_chain_report()
    elif report_type == "User Activity Summary":
        render_user_activity_report()
    elif report_type == "Financial Overview":
        render_financial_report()
    elif report_type == "Crop Production Analysis":
        render_crop_production_report()
    elif report_type == "Quality Metrics":
        render_quality_metrics_report()

def render_supply_chain_report():
    """Render supply chain performance report"""
    st.markdown("### 🔗 Supply Chain Performance")
    
    # Get delivery statistics
    total_deliveries = fetch_one("SELECT COUNT(*) as count FROM deliveries")
    completed_deliveries = fetch_one("SELECT COUNT(*) as count FROM deliveries WHERE status = 'delivered'")
    average_delivery_time = fetch_one("""
        SELECT AVG(EXTRACT(EPOCH FROM (
            CASE 
                WHEN status = 'delivered' THEN 
                    COALESCE(
                        (SELECT MAX(timestamp) FROM traceability WHERE batch_id = (SELECT batch_id FROM crops WHERE id = deliveries.crop_id) AND step_type = 'Retail'),
                        deliveries.created_at
                    )
                ELSE deliveries.created_at
            END - deliveries.created_at
        )) / 86400) as avg_days
        FROM deliveries 
        WHERE status = 'delivered'
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📦 Total Deliveries", total_deliveries['count'] if total_deliveries else 0)
    with col2:
        completion_rate = (completed_deliveries['count'] / total_deliveries['count'] * 100) if total_deliveries and total_deliveries['count'] > 0 else 0
        st.metric("✅ Completion Rate", f"{completion_rate:.1f}%")
    with col3:
        avg_time = average_delivery_time['avg_days'] if average_delivery_time and average_delivery_time['avg_days'] else 0
        st.metric("⏱️ Avg Delivery Time", f"{avg_time:.1f} days")
    
    # Delivery status distribution
    delivery_status = execute_query("""
        SELECT status, COUNT(*) as count 
        FROM deliveries 
        GROUP BY status
    """, fetch=True)
    
    if delivery_status:
        status_data = {row['status'].replace('_', ' ').title(): row['count'] for row in delivery_status}
        create_pie_chart(status_data, "Delivery Status Distribution")

def render_user_activity_report():
    """Render user activity report"""
    st.markdown("### 👥 User Activity Summary")
    
    # Registration trends
    registration_trends = execute_query("""
        SELECT DATE(created_at) as reg_date, COUNT(*) as new_users
        FROM users 
        WHERE created_at >= %s
        GROUP BY DATE(created_at)
        ORDER BY reg_date
    """, (datetime.now() - timedelta(days=30),), fetch=True)
    
    if registration_trends:
        trend_data = [{'date': row['reg_date'].strftime('%Y-%m-%d'), 'users': row['new_users']} for row in registration_trends]
        create_line_chart(trend_data, 'date', 'users', 'New User Registrations (Last 30 Days)')
    
    # User role distribution
    role_distribution = execute_query("SELECT role, COUNT(*) as count FROM users GROUP BY role", fetch=True)
    if role_distribution:
        role_data = {row['role']: row['count'] for row in role_distribution}
        create_pie_chart(role_data, "User Distribution by Role")
    
    # Most active users
    st.markdown("#### 🏆 Most Active Users")
    active_users = execute_query("""
        SELECT u.name, u.role, 
               COALESCE(crop_count, 0) as crops,
               COALESCE(delivery_count, 0) as deliveries,
               COALESCE(payment_count, 0) as payments
        FROM users u
        LEFT JOIN (
            SELECT farmer_id, COUNT(*) as crop_count 
            FROM crops 
            GROUP BY farmer_id
        ) c ON u.id = c.farmer_id
        LEFT JOIN (
            SELECT distributor_id, COUNT(*) as delivery_count 
            FROM deliveries 
            GROUP BY distributor_id
        ) d ON u.id = d.distributor_id
        LEFT JOIN (
            SELECT from_user_id, COUNT(*) as payment_count 
            FROM payments 
            GROUP BY from_user_id
        ) p ON u.id = p.from_user_id
        WHERE u.status = 'active'
        ORDER BY (COALESCE(crop_count, 0) + COALESCE(delivery_count, 0) + COALESCE(payment_count, 0)) DESC
        LIMIT 10
    """, fetch=True)
    
    if active_users:
        for user in active_users:
            activity_score = user['crops'] + user['deliveries'] + user['payments']
            st.markdown(f"""
            **{user['name']}** ({user['role']}) - Activity Score: {activity_score}  
            Crops: {user['crops']} | Deliveries: {user['deliveries']} | Payments: {user['payments']}
            """)

def render_financial_report():
    """Render financial overview report"""
    st.markdown("### 💰 Financial Overview")
    
    # Payment statistics
    payment_stats = execute_query("""
        SELECT 
            payment_status,
            COUNT(*) as transaction_count,
            SUM(amount) as total_amount
        FROM payments 
        GROUP BY payment_status
    """, fetch=True)
    
    if payment_stats:
        for stat in payment_stats:
            st.markdown(f"""
            **{stat['payment_status'].title()} Payments:**  
            Count: {stat['transaction_count']} | Total: ₹{stat['total_amount']:,.0f}
            """)
    
    # Monthly payment trends
    monthly_payments = execute_query("""
        SELECT 
            DATE_TRUNC('month', created_at) as month,
            SUM(amount) as monthly_total
        FROM payments 
        WHERE payment_status = 'completed'
        AND created_at >= %s
        GROUP BY DATE_TRUNC('month', created_at)
        ORDER BY month
    """, (datetime.now() - timedelta(days=365),), fetch=True)
    
    if monthly_payments:
        monthly_data = [{'month': row['month'].strftime('%Y-%m'), 'amount': float(row['monthly_total'])} for row in monthly_payments]
        create_line_chart(monthly_data, 'month', 'amount', 'Monthly Payment Volume')

def render_crop_production_report():
    """Render crop production analysis"""
    st.markdown("### 🌾 Crop Production Analysis")
    
    # Crop type distribution
    crop_type_stats = execute_query("""
        SELECT 
            type,
            COUNT(*) as crop_count,
            SUM(quantity) as total_quantity,
            AVG(price) as avg_price
        FROM crops 
        GROUP BY type
        ORDER BY total_quantity DESC
    """, fetch=True)
    
    if crop_type_stats:
        st.markdown("#### 📊 Production by Crop Type")
        for stat in crop_type_stats:
            st.markdown(f"""
            **{stat['type']}:**  
            Batches: {stat['crop_count']} | Total Quantity: {stat['total_quantity']:,.0f} kg | Avg Price: ₹{stat['avg_price']:.2f}/kg
            """)
        
        # Create pie chart for crop distribution
        crop_quantity_data = {row['type']: float(row['total_quantity']) for row in crop_type_stats}
        create_pie_chart(crop_quantity_data, "Production Volume by Crop Type")
    
    # Top producing farmers
    st.markdown("#### 🏆 Top Producing Farmers")
    top_farmers = execute_query("""
        SELECT 
            u.name,
            COUNT(c.id) as crop_batches,
            SUM(c.quantity) as total_quantity,
            SUM(c.price * c.quantity) as total_value
        FROM users u
        JOIN crops c ON u.id = c.farmer_id
        WHERE u.role = 'Farmer'
        GROUP BY u.id, u.name
        ORDER BY total_quantity DESC
        LIMIT 10
    """, fetch=True)
    
    if top_farmers:
        for farmer in top_farmers:
            st.markdown(f"""
            **{farmer['name']}:**  
            Batches: {farmer['crop_batches']} | Quantity: {farmer['total_quantity']:,.0f} kg | Value: ₹{farmer['total_value']:,.0f}
            """)

def render_quality_metrics_report():
    """Render quality metrics report"""
    st.markdown("### ⭐ Quality Metrics")
    
    st.info("Quality metrics would be based on feedback data, delivery completion rates, and other quality indicators.")
    
    # Delivery success rate
    delivery_success = execute_query("""
        SELECT 
            COUNT(*) as total_deliveries,
            SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as successful_deliveries
        FROM deliveries
    """, fetch=True)
    
    if delivery_success and delivery_success[0]['total_deliveries'] > 0:
        success_rate = (delivery_success[0]['successful_deliveries'] / delivery_success[0]['total_deliveries']) * 100
        st.metric("📦 Delivery Success Rate", f"{success_rate:.1f}%")
    
    # Traceability completeness
    traceability_stats = execute_query("""
        SELECT 
            c.batch_id,
            COUNT(DISTINCT t.step_type) as trace_steps
        FROM crops c
        LEFT JOIN traceability t ON c.batch_id = t.batch_id
        GROUP BY c.batch_id
    """, fetch=True)
    
    if traceability_stats:
        complete_traces = len([t for t in traceability_stats if t['trace_steps'] >= 2])
        total_batches = len(traceability_stats)
        completeness_rate = (complete_traces / total_batches * 100) if total_batches > 0 else 0
        st.metric("🔍 Traceability Completeness", f"{completeness_rate:.1f}%")
    
    # Payment reliability
    payment_reliability = execute_query("""
        SELECT 
            COUNT(*) as total_payments,
            SUM(CASE WHEN payment_status = 'completed' THEN 1 ELSE 0 END) as completed_payments
        FROM payments
    """, fetch=True)
    
    if payment_reliability and payment_reliability[0]['total_payments'] > 0:
        reliability_rate = (payment_reliability[0]['completed_payments'] / payment_reliability[0]['total_payments']) * 100
        st.metric("💰 Payment Reliability", f"{reliability_rate:.1f}%")
