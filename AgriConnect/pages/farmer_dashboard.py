import streamlit as st
from database import execute_query, fetch_one
from auth import generate_batch_id
from utils import create_crop_card, create_payment_card, format_date
from components.qr_generator import generate_qr_display
from datetime import date
import uuid

def render():
    """Render farmer dashboard"""
    page = st.session_state.get('farmer_page', 'overview')
    
    if page == 'overview':
        render_overview()
    elif page == 'add_crop':
        render_add_crop()
    elif page == 'my_crops':
        render_my_crops()
    elif page == 'payments':
        render_payments()
    elif page == 'qr_codes':
        render_qr_codes()

def render_overview():
    """Render farmer overview"""
    st.markdown("## 🌾 Farmer Dashboard Overview")
    
    farmer_id = st.session_state.user_id
    
    # Get farmer statistics
    total_crops = fetch_one("SELECT COUNT(*) as count FROM crops WHERE farmer_id = %s", (farmer_id,))
    available_crops = fetch_one("SELECT COUNT(*) as count FROM crops WHERE farmer_id = %s AND status = 'available'", (farmer_id,))
    total_earnings = fetch_one("SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE to_user_id = %s AND payment_status = 'completed'", (farmer_id,))
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            color: white;
        ">
            <h3 style="margin: 0; font-size: 2rem;">{total_crops['count'] if total_crops else 0}</h3>
            <p style="margin: 0.5rem 0 0 0;">🌾 Total Crops</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            color: white;
        ">
            <h3 style="margin: 0; font-size: 2rem;">{available_crops['count'] if available_crops else 0}</h3>
            <p style="margin: 0.5rem 0 0 0;">📦 Available</p>
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
    
    # Recent crops
    st.markdown("### 📦 Recent Crops")
    recent_crops = execute_query("""
        SELECT * FROM crops 
        WHERE farmer_id = %s 
        ORDER BY created_at DESC 
        LIMIT 5
    """, (farmer_id,), fetch=True)
    
    if recent_crops:
        for crop in recent_crops:
            create_crop_card(crop)
    else:
        st.info("No crops added yet. Add your first crop to get started!")

def render_add_crop():
    """Render add crop form"""
    st.markdown("## 🌱 Add New Crop")
    
    with st.form("add_crop_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            crop_name = st.text_input("Crop Name", placeholder="e.g., Wheat, Rice, Tomato")
            crop_type = st.selectbox("Crop Type", [
                "Cereals", "Vegetables", "Fruits", "Pulses", "Spices", "Other"
            ])
            quantity = st.number_input("Quantity (kg)", min_value=1.0, value=100.0, step=1.0)
        
        with col2:
            price = st.number_input("Price per kg (₹)", min_value=1.0, value=50.0, step=1.0)
            harvest_date = st.date_input("Harvest Date", value=date.today())
            photo_url = st.text_input("Photo URL (optional)", placeholder="https://example.com/crop-image.jpg")
        
        submitted = st.form_submit_button("🌾 Add Crop", use_container_width=True)
        
        if submitted:
            if crop_name and crop_type and quantity and price:
                batch_id = generate_batch_id()
                farmer_id = st.session_state.user_id
                
                result = execute_query("""
                    INSERT INTO crops (farmer_id, name, type, quantity, price, harvest_date, batch_id, photo_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (farmer_id, crop_name, crop_type, quantity, price, harvest_date, batch_id, photo_url))
                
                if result and result > 0:
                    # Add traceability record
                    execute_query("""
                        INSERT INTO traceability (batch_id, step_type, user_id, details)
                        VALUES (%s, %s, %s, %s)
                    """, (batch_id, "Harvest", farmer_id, f"Crop harvested by farmer"))
                    
                    st.success(f"✅ Crop added successfully! Batch ID: {batch_id}")
                    st.balloons()
                else:
                    st.error("Failed to add crop. Please try again.")
            else:
                st.warning("Please fill in all required fields.")

def render_my_crops():
    """Render farmer's crops"""
    st.markdown("## 📦 My Crops")
    
    farmer_id = st.session_state.user_id
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "available", "sold", "in_transit"])
    with col2:
        type_filter = st.selectbox("Filter by Type", ["All", "Cereals", "Vegetables", "Fruits", "Pulses", "Spices", "Other"])
    with col3:
        search_term = st.text_input("Search Crops", placeholder="Search by name...")
    
    # Build query
    query = "SELECT * FROM crops WHERE farmer_id = %s"
    params = [farmer_id]
    
    if status_filter != "All":
        query += " AND status = %s"
        params.append(status_filter)
    
    if type_filter != "All":
        query += " AND type = %s"
        params.append(type_filter)
    
    if search_term:
        query += " AND LOWER(name) LIKE %s"
        params.append(f"%{search_term.lower()}%")
    
    query += " ORDER BY created_at DESC"
    
    crops = execute_query(query, params, fetch=True)
    
    if crops:
        for crop in crops:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                create_crop_card(crop)
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"📱 Generate QR", key=f"qr_{crop['id']}"):
                    st.session_state.selected_crop_qr = crop
                    st.session_state.farmer_page = 'qr_codes'
                    st.rerun()
                
                if crop['status'] == 'available':
                    if st.button(f"🔄 Update Status", key=f"update_{crop['id']}"):
                        new_status = st.selectbox(f"New status for {crop['name']}", 
                                                ["available", "sold", "in_transit"], 
                                                key=f"status_{crop['id']}")
                        if st.button(f"✅ Confirm", key=f"confirm_{crop['id']}"):
                            execute_query("UPDATE crops SET status = %s WHERE id = %s", 
                                        (new_status, crop['id']))
                            st.success("Status updated!")
                            st.rerun()
    else:
        st.info("No crops found matching your criteria.")

def render_payments():
    """Render payments page"""
    st.markdown("## 💰 Payment History")
    
    farmer_id = st.session_state.user_id
    
    payments = execute_query("""
        SELECT p.*, c.name as crop_name, u.name as from_user_name
        FROM payments p
        LEFT JOIN crops c ON p.crop_id = c.id
        LEFT JOIN users u ON p.from_user_id = u.id
        WHERE p.to_user_id = %s
        ORDER BY p.created_at DESC
    """, (farmer_id,), fetch=True)
    
    if payments:
        # Summary
        total_received = sum([p['amount'] for p in payments if p['payment_status'] == 'completed'])
        pending_amount = sum([p['amount'] for p in payments if p['payment_status'] == 'pending'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💰 Total Received", f"₹{total_received:,.0f}")
        with col2:
            st.metric("⏳ Pending Payments", f"₹{pending_amount:,.0f}")
        
        st.markdown("---")
        
        # Payment list
        for payment in payments:
            st.markdown(f"""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin: 1rem 0;
                border-left: 4px solid {'#22c55e' if payment['payment_status'] == 'completed' else '#f59e0b'};
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="margin: 0; color: #1f2937;">₹{payment['amount']:,.0f}</h3>
                        <p style="margin: 0.25rem 0; color: #6b7280;">
                            <strong>From:</strong> {payment.get('from_user_name', 'Unknown')}
                        </p>
                        <p style="margin: 0.25rem 0; color: #6b7280;">
                            <strong>Crop:</strong> {payment.get('crop_name', 'N/A')}
                        </p>
                        <small style="color: #9ca3af;">
                            {payment['created_at'].strftime('%Y-%m-%d %H:%M')}
                        </small>
                    </div>
                    <span style="
                        background: {'#22c55e' if payment['payment_status'] == 'completed' else '#f59e0b'};
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
        st.info("No payment history available.")

def render_qr_codes():
    """Render QR codes page"""
    st.markdown("## 📱 QR Code Generator")
    
    farmer_id = st.session_state.user_id
    
    # Check if a specific crop was selected
    if hasattr(st.session_state, 'selected_crop_qr'):
        crop = st.session_state.selected_crop_qr
        generate_qr_display(crop['batch_id'], crop['name'])
        
        if st.button("🔙 Back to Crops"):
            del st.session_state.selected_crop_qr
            st.session_state.farmer_page = 'my_crops'
            st.rerun()
    else:
        # Show all crops with QR generation option
        crops = execute_query("""
            SELECT * FROM crops 
            WHERE farmer_id = %s 
            ORDER BY created_at DESC
        """, (farmer_id,), fetch=True)
        
        if crops:
            st.markdown("### Select a crop to generate QR code:")
            
            for crop in crops:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="
                        background: white;
                        padding: 1rem;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                        border-left: 4px solid #22c55e;
                    ">
                        <h4 style="margin: 0; color: #1f2937;">{crop['name']}</h4>
                        <p style="margin: 0.25rem 0; color: #6b7280;">
                            Batch ID: {crop['batch_id']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"📱 Generate QR", key=f"gen_qr_{crop['id']}"):
                        generate_qr_display(crop['batch_id'], crop['name'])
        else:
            st.info("No crops available. Add crops first to generate QR codes.")
