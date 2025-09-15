import streamlit as st
import qrcode
from PIL import Image
import io
import base64
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def generate_qr_code(batch_id):
    """Generate QR code for batch ID"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(batch_id)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def image_to_base64(image):
    """Convert PIL image to base64 string"""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def create_crop_card(crop):
    """Create styled crop card"""
    status_color = "#22c55e" if crop['status'] == 'available' else "#ef4444"
    
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
        <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Quantity:</strong> {crop['quantity']} kg</p>
        <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Price:</strong> ₹{crop['price']}/kg</p>
        <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Batch ID:</strong> {crop['batch_id']}</p>
        <span style="
            background: {status_color};
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
        ">{crop['status'].title()}</span>
    </div>
    """, unsafe_allow_html=True)

def create_user_card(user):
    """Create styled user card"""
    role_colors = {
        'Farmer': '#22c55e',
        'Distributor': '#3b82f6',
        'Retailer': '#f59e0b',
        'Buyer': '#8b5cf6',
        'Admin': '#ef4444'
    }
    
    color = role_colors.get(user['role'], '#6b7280')
    
    st.markdown(f"""
    <div style="
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid {color};
    ">
        <h3 style="color: #1f2937; margin: 0 0 0.5rem 0;">{user['name']}</h3>
        <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Email:</strong> {user['email']}</p>
        <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Phone:</strong> {user.get('phone', 'N/A')}</p>
        <span style="
            background: {color};
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
        ">{user['role']}</span>
    </div>
    """, unsafe_allow_html=True)

def create_payment_card(payment):
    """Create styled payment card"""
    status_colors = {
        'completed': '#22c55e',
        'pending': '#f59e0b',
        'failed': '#ef4444'
    }
    
    color = status_colors.get(payment['payment_status'], '#6b7280')
    
    st.markdown(f"""
    <div style="
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid {color};
    ">
        <h3 style="color: #1f2937; margin: 0 0 0.5rem 0;">₹{payment['amount']}</h3>
        <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Transaction ID:</strong> {payment.get('transaction_id', 'N/A')}</p>
        <p style="color: #6b7280; margin: 0.25rem 0;"><strong>Date:</strong> {payment['created_at'].strftime('%Y-%m-%d %H:%M')}</p>
        <span style="
            background: {color};
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
        ">{payment['payment_status'].title()}</span>
    </div>
    """, unsafe_allow_html=True)

def format_date(date_obj):
    """Format date object to string"""
    if isinstance(date_obj, datetime):
        return date_obj.strftime('%Y-%m-%d')
    elif isinstance(date_obj, date):
        return date_obj.strftime('%Y-%m-%d')
    return str(date_obj)

def create_timeline_step(step_data, icon, color):
    """Create timeline step for traceability"""
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 0.5rem 0;
        border-left: 4px solid {color};
    ">
        <div style="
            background: {color};
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
            font-size: 1.2rem;
        ">
            {icon}
        </div>
        <div>
            <h4 style="margin: 0; color: #1f2937;">{step_data['step_type']}</h4>
            <p style="margin: 0.25rem 0; color: #6b7280;">{step_data.get('details', '')}</p>
            <small style="color: #9ca3af;">{step_data['timestamp'].strftime('%Y-%m-%d %H:%M')}</small>
        </div>
    </div>
    """, unsafe_allow_html=True)
