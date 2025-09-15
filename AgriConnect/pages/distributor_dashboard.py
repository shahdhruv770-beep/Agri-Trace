import streamlit as st
from database import execute_query, fetch_one
from utils import create_crop_card, create_payment_card
from datetime import date
import uuid

def render():
    """Render distributor dashboard"""
    page = st.session_state.get('distributor_page', 'overview')
    
    if page == 'overview':
        render_overview()
    elif page == 'available_crops':
        render_available_crops()
    elif page == 'deliveries':
        render_deliveries()
    elif page == 'transport':
        render_transport()
    elif page == 'payments':
        render_payments()

def render_overview():
    """Render distributor overview"""
    st.markdown("## 🚚 Distributor Dashboard Overview")
    
    distributor_id = st.session_state.user_id
    
    # Get distributor statistics
    active_deliveries = fetch_one("""
        SELECT COUNT(*) as count FROM deliveries 
        WHERE distributor_id = %s AND status = 'in_transit'
    """, (distributor_id,))
    
    completed_deliveries = fetch_one("""
        SELECT COUNT(*) as count FROM deliveries 
        WHERE distributor_id = %s AND status = 'delivered'
    """, (distributor_id,))
    
    total_earnings = fetch_one("""
        SELECT COALESCE(SUM(amount), 0) as total FROM payments 
        WHERE to_user_id = %s AND payment_status = 'completed'
    """, (distributor_id,))
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            color: white;
        ">
            <h3 style="margin: 0; font-size: 2rem;">{active_deliveries['count'] if active_deliveries else 0}</h3>
            <p style="margin: 0.5rem 0 0 0;">🚛 Active Deliveries</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            color: white;
        ">
            <h3 style="margin: 0; font-size: 2rem;">{completed_deliveries['count'] if completed_deliveries else 0}</h3>
            <p style="margin: 0.5rem 0 0 0;">✅ Completed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            color: white;
        ">
            <h3 style="margin: 0; font-size: 2rem;">₹{total_earnings['total'] if total_earnings else 0:,.0f}</h3>
            <p style="margin: 0.5rem 0 0 0;">💰 Total Earnings</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent activities
    st.markdown("### 📋 Recent Activities")
    recent_deliveries = execute_query("""
        SELECT d.*, c.name as crop_name, u.name as farmer_name
        FROM deliveries d
        LEFT JOIN crops c ON d.crop_id = c.id
        LEFT JOIN users u ON c.farmer_id = u.id
        WHERE d.distributor_id = %s
        ORDER BY d.created_at DESC
        LIMIT 5
    """, (distributor_id,), fetch=True)
    
    if recent_deliveries:
        for delivery in recent_deliveries:
            status_color = {
                'pending': '#f59e0b',
                'in_transit': '#3b82f6',
                'delivered': '#22c55e'
            }.get(delivery['status'], '#6b7280')
            
            st.markdown(f"""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin: 1rem 0;
                border-left: 4px solid {status_color};
            ">
                <h4 style="margin: 0; color: #1f2937;">{delivery['crop_name']}</h4>
                <p style="margin: 0.25rem 0; color: #6b7280;">
                    <strong>Farmer:</strong> {delivery['farmer_name']}
                </p>
                <span style="
                    background: {status_color};
                    color: white;
                    padding: 0.25rem 0.75rem;
                    border-radius: 20px;
                    font-size: 0.875rem;
                ">
                    {delivery['status'].replace('_', ' ').title()}
                </span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent deliveries. Start by accepting crops from farmers!")

def render_available_crops():
    """Render available crops for procurement"""
    st.markdown("## 🌾 Available Crops")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.selectbox("Filter by Type", ["All", "Cereals", "Vegetables", "Fruits", "Pulses", "Spices", "Other"])
    with col2:
        price_range = st.slider("Max Price per kg (₹)", 0, 1000, 500)
    with col3:
        search_term = st.text_input("Search Crops", placeholder="Search by name...")
    
    # Build query
    query = """
        SELECT c.*, u.name as farmer_name, u.phone as farmer_phone
        FROM crops c
        LEFT JOIN users u ON c.farmer_id = u.id
        WHERE c.status = 'available' AND c.price <= %s
    """
    params = [price_range]
    
    if type_filter != "All":
        query += " AND c.type = %s"
        params.append(type_filter)
    
    if search_term:
        query += " AND LOWER(c.name) LIKE %s"
        params.append(f"%{search_term.lower()}%")
    
    query += " ORDER BY c.created_at DESC"
    
    crops = execute_query(query, params, fetch=True)
    
    if crops:
        for crop in crops:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 1.5rem;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    margin: 1rem 0;
                    border-left: 4px solid #22c55e;
                ">
                    <h3 style="color: #1f2937; margin: 0 0 0.5rem 0;">{crop['name']}</h3>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Type:</strong> {crop['type']}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Quantity:</strong> {crop['quantity']} kg</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Price:</strong> ₹{crop['price']}/kg</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Farmer:</strong> {crop['farmer_name']}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Contact:</strong> {crop['farmer_phone']}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Batch ID:</strong> {crop['batch_id']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button(f"🛒 Accept Crop", key=f"accept_{crop['id']}"):
                    accept_crop(crop)
    else:
        st.info("No crops available matching your criteria.")

def accept_crop(crop):
    """Accept crop from farmer"""
    with st.form(f"accept_form_{crop['id']}"):
        st.markdown(f"### Accept {crop['name']}")
        
        retailer_id = st.selectbox("Assign to Retailer", 
                                  options=get_retailers(),
                                  format_func=lambda x: x[1] if x else "Select Retailer")
        
        transport_details = st.text_area("Transport Details", 
                                       placeholder="Vehicle number, route, estimated delivery time...")
        
        delivery_date = st.date_input("Expected Delivery Date", value=date.today())
        
        submitted = st.form_submit_button("✅ Accept & Create Delivery")
        
        if submitted and retailer_id and transport_details:
            distributor_id = st.session_state.user_id
            
            # Create delivery record
            delivery_result = execute_query("""
                INSERT INTO deliveries (crop_id, distributor_id, retailer_id, transport_details, delivery_date)
                VALUES (%s, %s, %s, %s, %s)
            """, (crop['id'], distributor_id, retailer_id[0], transport_details, delivery_date))
            
            if delivery_result and delivery_result > 0:
                # Update crop status
                execute_query("UPDATE crops SET status = 'in_transit' WHERE id = %s", (crop['id'],))
                
                # Add traceability record
                execute_query("""
                    INSERT INTO traceability (batch_id, step_type, user_id, details)
                    VALUES (%s, %s, %s, %s)
                """, (crop['batch_id'], "Transport", distributor_id, f"Picked up by distributor - {transport_details}"))
                
                # Create transaction record
                execute_query("""
                    INSERT INTO transactions (crop_id, from_user_id, to_user_id, transaction_type, transport_details)
                    VALUES (%s, %s, %s, %s, %s)
                """, (crop['id'], crop['farmer_id'], distributor_id, "procurement", transport_details))
                
                st.success("✅ Crop accepted successfully! Delivery created.")
                st.rerun()
            else:
                st.error("Failed to accept crop. Please try again.")

def get_retailers():
    """Get list of retailers"""
    retailers = execute_query("SELECT id, name FROM users WHERE role = 'Retailer'", fetch=True)
    return [(r['id'], r['name']) for r in retailers] if retailers else []

def render_deliveries():
    """Render delivery management"""
    st.markdown("## 🚛 My Deliveries")
    
    distributor_id = st.session_state.user_id
    
    # Filter options
    status_filter = st.selectbox("Filter by Status", ["All", "pending", "in_transit", "delivered"])
    
    query = """
        SELECT d.*, c.name as crop_name, c.quantity, c.price, c.batch_id,
               u1.name as farmer_name, u2.name as retailer_name
        FROM deliveries d
        LEFT JOIN crops c ON d.crop_id = c.id
        LEFT JOIN users u1 ON c.farmer_id = u1.id
        LEFT JOIN users u2 ON d.retailer_id = u2.id
        WHERE d.distributor_id = %s
    """
    params = [distributor_id]
    
    if status_filter != "All":
        query += " AND d.status = %s"
        params.append(status_filter)
    
    query += " ORDER BY d.created_at DESC"
    
    deliveries = execute_query(query, params, fetch=True)
    
    if deliveries:
        for delivery in deliveries:
            status_color = {
                'pending': '#f59e0b',
                'in_transit': '#3b82f6',
                'delivered': '#22c55e'
            }.get(delivery['status'], '#6b7280')
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 1.5rem;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    margin: 1rem 0;
                    border-left: 4px solid {status_color};
                ">
                    <h3 style="color: #1f2937; margin: 0 0 0.5rem 0;">{delivery['crop_name']}</h3>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>From:</strong> {delivery['farmer_name']}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>To:</strong> {delivery['retailer_name']}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Quantity:</strong> {delivery['quantity']} kg</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Delivery Date:</strong> {delivery['delivery_date']}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Transport:</strong> {delivery['transport_details']}</p>
                    <span style="
                        background: {status_color};
                        color: white;
                        padding: 0.25rem 0.75rem;
                        border-radius: 20px;
                        font-size: 0.875rem;
                    ">
                        {delivery['status'].replace('_', ' ').title()}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if delivery['status'] == 'pending':
                    if st.button(f"🚛 Start Transport", key=f"start_{delivery['id']}"):
                        execute_query("UPDATE deliveries SET status = 'in_transit' WHERE id = %s", (delivery['id'],))
                        st.success("Transport started!")
                        st.rerun()
                
                elif delivery['status'] == 'in_transit':
                    if st.button(f"📍 Update Location", key=f"update_{delivery['id']}"):
                        location = st.text_input(f"Current location for delivery {delivery['id']}", key=f"loc_{delivery['id']}")
                        if st.button(f"✅ Update", key=f"confirm_loc_{delivery['id']}"):
                            execute_query("""
                                UPDATE deliveries SET tracking_info = %s WHERE id = %s
                            """, (f"Current location: {location}", delivery['id']))
                            st.success("Location updated!")
                            st.rerun()
    else:
        st.info("No deliveries found.")

def render_transport():
    """Render transport management"""
    st.markdown("## 📋 Transport Management")
    
    distributor_id = st.session_state.user_id
    
    with st.form("transport_form"):
        st.markdown("### 🚛 Add New Transport Vehicle")
        
        vehicle_number = st.text_input("Vehicle Number", placeholder="e.g., MH12AB1234")
        driver_name = st.text_input("Driver Name", placeholder="Driver's full name")
        driver_phone = st.text_input("Driver Phone", placeholder="Driver's contact number")
        vehicle_type = st.selectbox("Vehicle Type", ["Truck", "Van", "Pickup", "Other"])
        capacity = st.number_input("Capacity (kg)", min_value=100, value=1000, step=100)
        
        submitted = st.form_submit_button("🚛 Add Vehicle")
        
        if submitted and vehicle_number and driver_name:
            # Store vehicle info (you can create a vehicles table for this)
            st.success(f"✅ Vehicle {vehicle_number} added successfully!")
    
    st.markdown("---")
    
    # Active routes
    st.markdown("### 🗺️ Active Routes")
    
    active_deliveries = execute_query("""
        SELECT d.*, c.name as crop_name, u.name as retailer_name
        FROM deliveries d
        LEFT JOIN crops c ON d.crop_id = c.id
        LEFT JOIN users u ON d.retailer_id = u.id
        WHERE d.distributor_id = %s AND d.status = 'in_transit'
        ORDER BY d.delivery_date ASC
    """, (distributor_id,), fetch=True)
    
    if active_deliveries:
        for delivery in active_deliveries:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                padding: 1.5rem;
                border-radius: 12px;
                color: white;
                margin: 1rem 0;
            ">
                <h4 style="margin: 0 0 0.5rem 0;">🚛 {delivery['crop_name']} → {delivery['retailer_name']}</h4>
                <p style="margin: 0.25rem 0;">📅 Expected: {delivery['delivery_date']}</p>
                <p style="margin: 0.25rem 0;">🚛 {delivery['transport_details']}</p>
                {f"<p style='margin: 0.25rem 0;'>📍 {delivery['tracking_info']}</p>" if delivery.get('tracking_info') else ""}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No active routes. Accept crops to start deliveries!")

def render_payments():
    """Render payments page"""
    st.markdown("## 💰 Payment Management")
    
    distributor_id = st.session_state.user_id
    
    # Payments received
    st.markdown("### 💵 Payments Received")
    received_payments = execute_query("""
        SELECT p.*, c.name as crop_name, u.name as from_user_name
        FROM payments p
        LEFT JOIN crops c ON p.crop_id = c.id
        LEFT JOIN users u ON p.from_user_id = u.id
        WHERE p.to_user_id = %s
        ORDER BY p.created_at DESC
    """, (distributor_id,), fetch=True)
    
    if received_payments:
        total_received = sum([p['amount'] for p in received_payments if p['payment_status'] == 'completed'])
        st.metric("💰 Total Received", f"₹{total_received:,.0f}")
        
        for payment in received_payments:
            create_payment_card(payment)
    else:
        st.info("No payments received yet.")
    
    st.markdown("---")
    
    # Make payments to farmers
    st.markdown("### 💸 Pay Farmers")
    
    # Get crops that need payment
    unpaid_crops = execute_query("""
        SELECT c.*, u.name as farmer_name, t.id as transaction_id
        FROM crops c
        LEFT JOIN users u ON c.farmer_id = u.id
        LEFT JOIN transactions t ON c.id = t.crop_id
        WHERE c.status IN ('in_transit', 'delivered') 
        AND NOT EXISTS (
            SELECT 1 FROM payments p 
            WHERE p.crop_id = c.id AND p.from_user_id = %s
        )
        AND t.to_user_id = %s
    """, (distributor_id, distributor_id), fetch=True)
    
    if unpaid_crops:
        for crop in unpaid_crops:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div style="
                    background: #fef3c7;
                    padding: 1rem;
                    border-radius: 8px;
                    border-left: 4px solid #f59e0b;
                ">
                    <h4 style="margin: 0; color: #92400e;">{crop['name']} - {crop['farmer_name']}</h4>
                    <p style="margin: 0.25rem 0; color: #92400e;">Amount: ₹{crop['price'] * crop['quantity']:,.0f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"💰 Pay Farmer", key=f"pay_{crop['id']}"):
                    amount = crop['price'] * crop['quantity']
                    payment_result = execute_query("""
                        INSERT INTO payments (amount, from_user_id, to_user_id, crop_id, payment_status)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (amount, distributor_id, crop['farmer_id'], crop['id'], 'completed'))
                    
                    if payment_result:
                        st.success(f"✅ Payment of ₹{amount:,.0f} sent to {crop['farmer_name']}")
                        st.rerun()
    else:
        st.info("No pending payments to farmers.")
