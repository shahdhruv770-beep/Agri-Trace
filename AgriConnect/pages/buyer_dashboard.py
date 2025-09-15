import streamlit as st
from database import execute_query, fetch_one
from components.qr_generator import scan_qr_interface
from utils import create_timeline_step
from datetime import datetime

def render():
    """Render buyer/consumer dashboard"""
    page = st.session_state.get('buyer_page', 'scan')
    
    if page == 'scan':
        render_scan_qr()
    elif page == 'history':
        render_trace_history()
    elif page == 'feedback':
        render_feedback()

def render_scan_qr():
    """Render QR code scanning interface"""
    st.markdown("## 📱 Scan QR Code")
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin: 1rem 0;
    ">
        <h2 style="margin: 0 0 1rem 0;">🔍 Trace Your Food Journey</h2>
        <p style="margin: 0; font-size: 1.1rem;">
            Scan the QR code on your product to see its complete farm-to-table journey
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # QR scanning interface
    batch_id = scan_qr_interface()
    
    if batch_id:
        st.markdown("---")
        display_traceability(batch_id)

def display_traceability(batch_id):
    """Display complete traceability for a batch ID"""
    st.markdown(f"## 🔍 Traceability for Batch: {batch_id}")
    
    # Get crop information
    crop_info = fetch_one("""
        SELECT c.*, u.name as farmer_name, u.phone as farmer_phone
        FROM crops c
        LEFT JOIN users u ON c.farmer_id = u.id
        WHERE c.batch_id = %s
    """, (batch_id,))
    
    if not crop_info:
        st.error("❌ Invalid batch ID or crop not found.")
        return
    
    # Display crop information
    st.markdown("### 🌾 Product Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
        ">
            <h3 style="margin: 0 0 1rem 0;">🌾 {crop_info['name']}</h3>
            <p style="margin: 0.5rem 0;"><strong>Type:</strong> {crop_info['type']}</p>
            <p style="margin: 0.5rem 0;"><strong>Quantity:</strong> {crop_info['quantity']} kg</p>
            <p style="margin: 0.5rem 0;"><strong>Harvest Date:</strong> {crop_info['harvest_date']}</p>
            <p style="margin: 0.5rem 0;"><strong>Batch ID:</strong> {crop_info['batch_id']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #22c55e;
        ">
            <h3 style="color: #1f2937; margin: 0 0 1rem 0;">👨‍🌾 Farmer Information</h3>
            <p style="color: #6b7280; margin: 0.5rem 0;"><strong>Name:</strong> {crop_info['farmer_name']}</p>
            <p style="color: #6b7280; margin: 0.5rem 0;"><strong>Contact:</strong> {crop_info['farmer_phone']}</p>
            <p style="color: #6b7280; margin: 0.5rem 0;"><strong>Status:</strong> Verified Farmer ✅</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get traceability timeline
    timeline = execute_query("""
        SELECT t.*, u.name as user_name, u.role
        FROM traceability t
        LEFT JOIN users u ON t.user_id = u.id
        WHERE t.batch_id = %s
        ORDER BY t.timestamp ASC
    """, (batch_id,), fetch=True)
    
    if timeline:
        st.markdown("### 📍 Complete Journey Timeline")
        
        # Create timeline visualization
        for i, step in enumerate(timeline):
            # Determine icon and color based on step type
            step_config = {
                'Harvest': {'icon': '🌾', 'color': '#22c55e', 'title': 'Harvested by Farmer'},
                'Transport': {'icon': '🚛', 'color': '#3b82f6', 'title': 'Picked up by Distributor'},
                'Retail': {'icon': '🏪', 'color': '#f59e0b', 'title': 'Received by Retailer'},
                'Sale': {'icon': '🛒', 'color': '#8b5cf6', 'title': 'Sold to Customer'}
            }.get(step['step_type'], {'icon': '📍', 'color': '#6b7280', 'title': step['step_type']})
            
            # Timeline connector
            if i > 0:
                st.markdown("""
                <div style="
                    width: 2px;
                    height: 20px;
                    background: #e5e7eb;
                    margin: 0 auto;
                "></div>
                """, unsafe_allow_html=True)
            
            # Timeline step
            st.markdown(f"""
            <div style="
                display: flex;
                align-items: center;
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin: 1rem 0;
                border-left: 4px solid {step_config['color']};
            ">
                <div style="
                    background: {step_config['color']};
                    color: white;
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: 1.5rem;
                    font-size: 1.5rem;
                ">
                    {step_config['icon']}
                </div>
                <div style="flex: 1;">
                    <h4 style="margin: 0 0 0.5rem 0; color: #1f2937;">{step_config['title']}</h4>
                    <p style="margin: 0.25rem 0; color: #6b7280;">
                        <strong>By:</strong> {step['user_name']} ({step['role']})
                    </p>
                    {f"<p style='margin: 0.25rem 0; color: #6b7280;'><strong>Details:</strong> {step['details']}</p>" if step['details'] else ""}
                    {f"<p style='margin: 0.25rem 0; color: #6b7280;'><strong>Location:</strong> {step['location']}</p>" if step.get('location') else ""}
                    <small style="color: #9ca3af;">
                        📅 {step['timestamp'].strftime('%B %d, %Y at %I:%M %p')}
                    </small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Quality assurance info
    st.markdown("---")
    st.markdown("### ✅ Quality Assurance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: #dcfce7;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            border: 2px solid #22c55e;
        ">
            <h4 style="margin: 0; color: #16a34a;">🌱 Organic Certified</h4>
            <p style="margin: 0.5rem 0 0 0; color: #15803d; font-size: 0.875rem;">
                No harmful pesticides used
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: #dbeafe;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            border: 2px solid #3b82f6;
        ">
            <h4 style="margin: 0; color: #2563eb;">🚛 Fresh Transport</h4>
            <p style="margin: 0.5rem 0 0 0; color: #1d4ed8; font-size: 0.875rem;">
                Cold chain maintained
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: #fef3c7;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            border: 2px solid #f59e0b;
        ">
            <h4 style="margin: 0; color: #d97706;">✅ Quality Tested</h4>
            <p style="margin: 0.5rem 0 0 0; color: #b45309; font-size: 0.875rem;">
                Passed all quality checks
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_trace_history():
    """Render traceability history"""
    st.markdown("## 🔍 Trace History")
    
    buyer_id = st.session_state.user_id
    
    # Get recent traces (you can implement user trace history)
    st.markdown("### 📚 Your Recent Traces")
    
    # For demo, show some example traces
    st.info("Your traceability history will appear here. Scan QR codes to build your trace history!")
    
    # Sample data for demonstration
    sample_traces = [
        {
            'batch_id': 'BATCH_ABC123',
            'crop_name': 'Organic Tomatoes',
            'farmer': 'John Farmer',
            'date_traced': '2024-01-15',
            'status': 'Complete Journey'
        },
        {
            'batch_id': 'BATCH_XYZ789',
            'crop_name': 'Fresh Wheat',
            'farmer': 'Mary Agricultural',
            'date_traced': '2024-01-10',
            'status': 'Complete Journey'
        }
    ]
    
    for trace in sample_traces:
        st.markdown(f"""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
            border-left: 4px solid #22c55e;
        ">
            <h4 style="margin: 0 0 0.5rem 0; color: #1f2937;">{trace['crop_name']}</h4>
            <p style="margin: 0.25rem 0; color: #6b7280;"><strong>Batch ID:</strong> {trace['batch_id']}</p>
            <p style="margin: 0.25rem 0; color: #6b7280;"><strong>Farmer:</strong> {trace['farmer']}</p>
            <p style="margin: 0.25rem 0; color: #6b7280;"><strong>Traced on:</strong> {trace['date_traced']}</p>
            <span style="
                background: #22c55e;
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-size: 0.875rem;
            ">
                {trace['status']}
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Statistics
    st.markdown("### 📊 Your Traceability Stats")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🔍 Total Traces", "2")
    
    with col2:
        st.metric("🌾 Unique Farmers", "2")
    
    with col3:
        st.metric("✅ Verified Products", "2")

def render_feedback():
    """Render feedback form"""
    st.markdown("## ⭐ Product Feedback")
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin: 1rem 0;
    ">
        <h2 style="margin: 0 0 1rem 0;">💬 Share Your Experience</h2>
        <p style="margin: 0; font-size: 1.1rem;">
            Help farmers and the supply chain improve by sharing your feedback
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("feedback_form"):
        batch_id = st.text_input("Batch ID", placeholder="Enter the batch ID from your product")
        
        col1, col2 = st.columns(2)
        
        with col1:
            rating = st.selectbox("Overall Rating", [5, 4, 3, 2, 1], 
                                format_func=lambda x: "⭐" * x + f" ({x}/5)")
            
            quality_rating = st.selectbox("Product Quality", [5, 4, 3, 2, 1],
                                        format_func=lambda x: "⭐" * x + f" ({x}/5)")
        
        with col2:
            freshness_rating = st.selectbox("Freshness", [5, 4, 3, 2, 1],
                                          format_func=lambda x: "⭐" * x + f" ({x}/5)")
            
            packaging_rating = st.selectbox("Packaging", [5, 4, 3, 2, 1],
                                          format_func=lambda x: "⭐" * x + f" ({x}/5)")
        
        feedback_text = st.text_area("Detailed Feedback", 
                                   placeholder="Share your detailed experience with this product...")
        
        recommend = st.radio("Would you recommend this product?", ["Yes", "No", "Maybe"])
        
        submitted = st.form_submit_button("📝 Submit Feedback", use_container_width=True)
        
        if submitted:
            if batch_id and rating and feedback_text:
                buyer_id = st.session_state.user_id
                
                # Store feedback (create feedback table in real implementation)
                feedback_data = {
                    'batch_id': batch_id,
                    'buyer_id': buyer_id,
                    'overall_rating': rating,
                    'quality_rating': quality_rating,
                    'freshness_rating': freshness_rating,
                    'packaging_rating': packaging_rating,
                    'feedback_text': feedback_text,
                    'recommend': recommend,
                    'created_at': datetime.now()
                }
                
                st.success("✅ Thank you for your feedback! Your review helps improve the supply chain.")
                st.balloons()
                
                # Show confirmation
                st.markdown("### 📝 Your Feedback Summary")
                
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 1.5rem;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    border-left: 4px solid #22c55e;
                ">
                    <h4 style="margin: 0 0 1rem 0; color: #1f2937;">Feedback for Batch: {batch_id}</h4>
                    <p style="margin: 0.5rem 0; color: #6b7280;"><strong>Overall Rating:</strong> {"⭐" * rating}</p>
                    <p style="margin: 0.5rem 0; color: #6b7280;"><strong>Quality:</strong> {"⭐" * quality_rating}</p>
                    <p style="margin: 0.5rem 0; color: #6b7280;"><strong>Freshness:</strong> {"⭐" * freshness_rating}</p>
                    <p style="margin: 0.5rem 0; color: #6b7280;"><strong>Packaging:</strong> {"⭐" * packaging_rating}</p>
                    <p style="margin: 0.5rem 0; color: #6b7280;"><strong>Recommendation:</strong> {recommend}</p>
                    <p style="margin: 0.5rem 0; color: #6b7280;"><strong>Comments:</strong> {feedback_text}</p>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.warning("Please fill in all required fields.")
    
    st.markdown("---")
    
    # Recent feedback from others
    st.markdown("### 💬 Recent Community Feedback")
    
    # Sample feedback for demonstration
    sample_feedback = [
        {
            'batch_id': 'BATCH_ABC123',
            'crop_name': 'Organic Tomatoes',
            'rating': 5,
            'comment': 'Excellent quality tomatoes! Very fresh and organic.',
            'date': '2024-01-15'
        },
        {
            'batch_id': 'BATCH_XYZ789',
            'crop_name': 'Fresh Wheat',
            'rating': 4,
            'comment': 'Good quality wheat, well packaged.',
            'date': '2024-01-12'
        }
    ]
    
    for feedback in sample_feedback:
        st.markdown(f"""
        <div style="
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin: 0.5rem 0;
            border-left: 4px solid #8b5cf6;
        ">
            <h5 style="margin: 0; color: #1f2937;">{feedback['crop_name']} - {"⭐" * feedback['rating']}</h5>
            <p style="margin: 0.25rem 0; color: #6b7280; font-size: 0.875rem;">"{feedback['comment']}"</p>
            <small style="color: #9ca3af;">Batch: {feedback['batch_id']} • {feedback['date']}</small>
        </div>
        """, unsafe_allow_html=True)
