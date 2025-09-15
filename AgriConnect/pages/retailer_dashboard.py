import streamlit as st
from database import execute_query, fetch_one
from utils import create_payment_card
from components.charts import create_sales_chart, create_metric_cards
from datetime import date, datetime, timedelta
import pandas as pd

def render():
    """Render retailer dashboard"""
    page = st.session_state.get('retailer_page', 'overview')
    
    if page == 'overview':
        render_overview()
    elif page == 'deliveries':
        render_deliveries()
    elif page == 'stock':
        render_stock()
    elif page == 'sales':
        render_sales()
    elif page == 'payments':
        render_payments()

def render_overview():
    """Render retailer overview"""
    st.markdown("## 🛒 Retailer Dashboard Overview")
    
    retailer_id = st.session_state.user_id
    
    # Get retailer statistics
    pending_deliveries = fetch_one("""
        SELECT COUNT(*) as count FROM deliveries 
        WHERE retailer_id = %s AND status IN ('pending', 'in_transit')
    """, (retailer_id,))
    
    total_stock = fetch_one("""
        SELECT COUNT(*) as count FROM deliveries 
        WHERE retailer_id = %s AND status = 'delivered'
    """, (retailer_id,))
    
    total_sales = fetch_one("""
        SELECT COALESCE(SUM(amount), 0) as total FROM payments 
        WHERE from_user_id = %s AND payment_status = 'completed'
    """, (retailer_id,))
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            color: white;
        ">
            <h3 style="margin: 0; font-size: 2rem;">{pending_deliveries['count'] if pending_deliveries else 0}</h3>
            <p style="margin: 0.5rem 0 0 0;">📦 Pending Deliveries</p>
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
            <h3 style="margin: 0; font-size: 2rem;">{total_stock['count'] if total_stock else 0}</h3>
            <p style="margin: 0.5rem 0 0 0;">🏪 Items in Stock</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            color: white;
        ">
            <h3 style="margin: 0; font-size: 2rem;">₹{total_sales['total'] if total_sales else 0:,.0f}</h3>
            <p style="margin: 0.5rem 0 0 0;">💰 Total Sales</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent activities
    st.markdown("### 📋 Recent Activities")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📦 Recent Deliveries")
        recent_deliveries = execute_query("""
            SELECT d.*, c.name as crop_name, u.name as distributor_name
            FROM deliveries d
            LEFT JOIN crops c ON d.crop_id = c.id
            LEFT JOIN users u ON d.distributor_id = u.id
            WHERE d.retailer_id = %s
            ORDER BY d.created_at DESC
            LIMIT 3
        """, (retailer_id,), fetch=True)
        
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
                    padding: 1rem;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    margin: 0.5rem 0;
                    border-left: 4px solid {status_color};
                ">
                    <h5 style="margin: 0; color: #1f2937;">{delivery['crop_name']}</h5>
                    <p style="margin: 0.25rem 0; color: #6b7280; font-size: 0.875rem;">
                        From: {delivery['distributor_name']}
                    </p>
                    <span style="
                        background: {status_color};
                        color: white;
                        padding: 0.125rem 0.5rem;
                        border-radius: 12px;
                        font-size: 0.75rem;
                    ">
                        {delivery['status'].title()}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent deliveries")
    
    with col2:
        st.markdown("#### 💰 Recent Payments")
        recent_payments = execute_query("""
            SELECT p.*, c.name as crop_name
            FROM payments p
            LEFT JOIN crops c ON p.crop_id = c.id
            WHERE p.from_user_id = %s
            ORDER BY p.created_at DESC
            LIMIT 3
        """, (retailer_id,), fetch=True)
        
        if recent_payments:
            for payment in recent_payments:
                status_color = {
                    'completed': '#22c55e',
                    'pending': '#f59e0b',
                    'failed': '#ef4444'
                }.get(payment['payment_status'], '#6b7280')
                
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 1rem;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    margin: 0.5rem 0;
                    border-left: 4px solid {status_color};
                ">
                    <h5 style="margin: 0; color: #1f2937;">₹{payment['amount']:,.0f}</h5>
                    <p style="margin: 0.25rem 0; color: #6b7280; font-size: 0.875rem;">
                        {payment.get('crop_name', 'N/A')}
                    </p>
                    <span style="
                        background: {status_color};
                        color: white;
                        padding: 0.125rem 0.5rem;
                        border-radius: 12px;
                        font-size: 0.75rem;
                    ">
                        {payment['payment_status'].title()}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent payments")

def render_deliveries():
    """Render deliveries management"""
    st.markdown("## 📦 Delivery Management")
    
    retailer_id = st.session_state.user_id
    
    # Filter options
    status_filter = st.selectbox("Filter by Status", ["All", "pending", "in_transit", "delivered"])
    
    query = """
        SELECT d.*, c.name as crop_name, c.quantity, c.price, c.batch_id,
               u1.name as farmer_name, u2.name as distributor_name
        FROM deliveries d
        LEFT JOIN crops c ON d.crop_id = c.id
        LEFT JOIN users u1 ON c.farmer_id = u1.id
        LEFT JOIN users u2 ON d.distributor_id = u2.id
        WHERE d.retailer_id = %s
    """
    params = [retailer_id]
    
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
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Farmer:</strong> {delivery['farmer_name']}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Distributor:</strong> {delivery['distributor_name']}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Quantity:</strong> {delivery['quantity']} kg</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Expected:</strong> {delivery['delivery_date']}</p>
                    {f"<p style='color: #6b7280; margin: 0.25rem 0;'><strong>Tracking:</strong> {delivery['tracking_info']}</p>" if delivery.get('tracking_info') else ""}
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
                
                if delivery['status'] == 'in_transit':
                    if st.button(f"✅ Accept Delivery", key=f"accept_{delivery['id']}"):
                        accept_delivery(delivery)
                
                elif delivery['status'] == 'delivered':
                    # Check if payment is made
                    payment_exists = fetch_one("""
                        SELECT id FROM payments 
                        WHERE from_user_id = %s AND crop_id = %s
                    """, (retailer_id, delivery['crop_id']))
                    
                    if not payment_exists:
                        if st.button(f"💰 Pay Distributor", key=f"pay_{delivery['id']}"):
                            make_payment_to_distributor(delivery)
                    else:
                        st.success("✅ Paid")
    else:
        st.info("No deliveries found.")

def accept_delivery(delivery):
    """Accept delivery from distributor"""
    delivery_id = delivery['id']
    crop_id = delivery['crop_id']
    
    # Update delivery status
    result = execute_query("UPDATE deliveries SET status = 'delivered' WHERE id = %s", (delivery_id,))
    
    if result:
        # Update crop status
        execute_query("UPDATE crops SET status = 'delivered' WHERE id = %s", (crop_id,))
        
        # Add traceability record
        retailer_id = st.session_state.user_id
        batch_id = delivery['batch_id']
        
        execute_query("""
            INSERT INTO traceability (batch_id, step_type, user_id, details)
            VALUES (%s, %s, %s, %s)
        """, (batch_id, "Retail", retailer_id, "Received by retailer"))
        
        st.success("✅ Delivery accepted successfully!")
        st.balloons()
        st.rerun()
    else:
        st.error("Failed to accept delivery.")

def make_payment_to_distributor(delivery):
    """Make payment to distributor"""
    retailer_id = st.session_state.user_id
    amount = delivery['price'] * delivery['quantity']
    
    with st.form(f"payment_form_{delivery['id']}"):
        st.markdown(f"### 💰 Pay ₹{amount:,.0f} to {delivery['distributor_name']}")
        
        payment_method = st.selectbox("Payment Method", ["UPI", "Bank Transfer", "Cash", "Cheque"])
        notes = st.text_area("Payment Notes", placeholder="Any additional notes...")
        
        submitted = st.form_submit_button("💰 Confirm Payment")
        
        if submitted:
            payment_result = execute_query("""
                INSERT INTO payments (amount, from_user_id, to_user_id, crop_id, payment_status, payment_method)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (amount, retailer_id, delivery['distributor_id'], delivery['crop_id'], 'completed', payment_method))
            
            if payment_result:
                st.success(f"✅ Payment of ₹{amount:,.0f} sent successfully!")
                st.rerun()
            else:
                st.error("Payment failed. Please try again.")

def render_stock():
    """Render stock management"""
    st.markdown("## 🏪 Stock Management")
    
    retailer_id = st.session_state.user_id
    
    # Get current stock
    stock_items = execute_query("""
        SELECT c.*, d.id as delivery_id, u.name as farmer_name
        FROM crops c
        LEFT JOIN deliveries d ON c.id = d.crop_id
        LEFT JOIN users u ON c.farmer_id = u.id
        WHERE d.retailer_id = %s AND d.status = 'delivered'
        ORDER BY d.created_at DESC
    """, (retailer_id,), fetch=True)
    
    if stock_items:
        # Stock summary
        total_items = len(stock_items)
        total_value = sum([item['price'] * item['quantity'] for item in stock_items])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📦 Total Items", total_items)
        with col2:
            st.metric("💰 Total Value", f"₹{total_value:,.0f}")
        
        st.markdown("---")
        
        # Stock items
        for item in stock_items:
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
                    <h3 style="color: #1f2937; margin: 0 0 0.5rem 0;">{item['name']}</h3>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Type:</strong> {item['type']}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Quantity:</strong> {item['quantity']} kg</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Purchase Price:</strong> ₹{item['price']}/kg</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Farmer:</strong> {item['farmer_name']}</p>
                    <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Batch ID:</strong> {item['batch_id']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                selling_price = st.number_input(f"Selling Price (₹/kg)", 
                                               min_value=float(item['price']), 
                                               value=float(item['price']) * 1.2,
                                               step=1.0,
                                               key=f"price_{item['id']}")
                
                if st.button(f"🏷️ Set Price", key=f"set_price_{item['id']}"):
                    # You can store selling prices in a separate table
                    st.success(f"Selling price set to ₹{selling_price}/kg")
    else:
        st.info("No stock available. Accept deliveries to build your inventory.")

def render_sales():
    """Render sales tracking"""
    st.markdown("## 📈 Sales Tracking")
    
    retailer_id = st.session_state.user_id
    
    # Sales summary for last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Simulate sales data (in a real app, you'd have a sales table)
    sales_data = execute_query("""
        SELECT DATE(p.created_at) as sale_date, SUM(p.amount) as daily_sales
        FROM payments p
        WHERE p.from_user_id = %s 
        AND p.created_at >= %s
        AND p.payment_status = 'completed'
        GROUP BY DATE(p.created_at)
        ORDER BY sale_date
    """, (retailer_id, start_date), fetch=True)
    
    if sales_data:
        # Convert to format for chart
        chart_data = [{'date': row['sale_date'].strftime('%Y-%m-%d'), 'amount': float(row['daily_sales'])} for row in sales_data]
        create_sales_chart(chart_data)
        
        # Sales metrics
        total_sales = sum([row['daily_sales'] for row in sales_data])
        avg_daily_sales = total_sales / len(sales_data) if sales_data else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Total Sales (30 days)", f"₹{total_sales:,.0f}")
        with col2:
            st.metric("📊 Average Daily Sales", f"₹{avg_daily_sales:,.0f}")
        with col3:
            st.metric("📈 Sales Days", len(sales_data))
    else:
        st.info("No sales data available for the last 30 days.")
    
    st.markdown("---")
    
    # Sales form (simulate making a sale)
    st.markdown("### 💰 Record New Sale")
    
    # Get available stock
    stock_items = execute_query("""
        SELECT c.id, c.name, c.quantity, c.batch_id
        FROM crops c
        LEFT JOIN deliveries d ON c.id = d.crop_id
        WHERE d.retailer_id = %s AND d.status = 'delivered'
    """, (retailer_id,), fetch=True)
    
    if stock_items:
        with st.form("sales_form"):
            selected_crop = st.selectbox("Select Crop", 
                                       options=[(item['id'], f"{item['name']} - {item['batch_id']}") for item in stock_items],
                                       format_func=lambda x: x[1])
            
            sale_quantity = st.number_input("Quantity Sold (kg)", min_value=1.0, value=10.0, step=1.0)
            sale_price = st.number_input("Sale Price per kg (₹)", min_value=1.0, value=100.0, step=1.0)
            customer_name = st.text_input("Customer Name (optional)", placeholder="Customer's name")
            
            submitted = st.form_submit_button("📝 Record Sale")
            
            if submitted and selected_crop:
                total_amount = sale_quantity * sale_price
                
                # Create a mock sale record (in real app, create sales table)
                st.success(f"✅ Sale recorded: {sale_quantity}kg × ₹{sale_price} = ₹{total_amount:,.0f}")
                
                # Add traceability record for sale
                crop_info = next(item for item in stock_items if item['id'] == selected_crop[0])
                execute_query("""
                    INSERT INTO traceability (batch_id, step_type, user_id, details)
                    VALUES (%s, %s, %s, %s)
                """, (crop_info['batch_id'], "Sale", retailer_id, f"Sold to customer: {customer_name or 'Anonymous'}"))
    else:
        st.info("No stock available for sale.")

def render_payments():
    """Render payments page"""
    st.markdown("## 💰 Payment Management")
    
    retailer_id = st.session_state.user_id
    
    # Payments made to distributors
    st.markdown("### 💸 Payments Made")
    made_payments = execute_query("""
        SELECT p.*, c.name as crop_name, u.name as to_user_name
        FROM payments p
        LEFT JOIN crops c ON p.crop_id = c.id
        LEFT JOIN users u ON p.to_user_id = u.id
        WHERE p.from_user_id = %s
        ORDER BY p.created_at DESC
    """, (retailer_id,), fetch=True)
    
    if made_payments:
        total_paid = sum([p['amount'] for p in made_payments if p['payment_status'] == 'completed'])
        st.metric("💰 Total Payments Made", f"₹{total_paid:,.0f}")
        
        for payment in made_payments:
            create_payment_card(payment)
    else:
        st.info("No payments made yet.")
    
    st.markdown("---")
    
    # Pending payments
    st.markdown("### ⏳ Pending Payments")
    
    pending_payments = execute_query("""
        SELECT d.*, c.name as crop_name, c.price, c.quantity, u.name as distributor_name
        FROM deliveries d
        LEFT JOIN crops c ON d.crop_id = c.id
        LEFT JOIN users u ON d.distributor_id = u.id
        WHERE d.retailer_id = %s AND d.status = 'delivered'
        AND NOT EXISTS (
            SELECT 1 FROM payments p 
            WHERE p.crop_id = d.crop_id AND p.from_user_id = %s
        )
    """, (retailer_id, retailer_id), fetch=True)
    
    if pending_payments:
        for payment in pending_payments:
            amount = payment['price'] * payment['quantity']
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div style="
                    background: #fef3c7;
                    padding: 1rem;
                    border-radius: 8px;
                    border-left: 4px solid #f59e0b;
                ">
                    <h4 style="margin: 0; color: #92400e;">{payment['crop_name']} - {payment['distributor_name']}</h4>
                    <p style="margin: 0.25rem 0; color: #92400e;">Amount: ₹{amount:,.0f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"💰 Pay Now", key=f"pay_pending_{payment['id']}"):
                    make_payment_to_distributor(payment)
    else:
        st.info("No pending payments.")
