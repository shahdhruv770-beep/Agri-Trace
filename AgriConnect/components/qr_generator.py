import streamlit as st
import qrcode
from PIL import Image
import io
import base64

def generate_qr_display(batch_id, crop_name):
    """Generate and display QR code"""
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(batch_id)
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes for both display and download
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)  # Reset buffer position
    img_bytes = buffer.getvalue()
    img_str = base64.b64encode(img_bytes).decode()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(img_bytes, caption=f"QR Code for {crop_name}", width=300)
    
    with col2:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            text-align: center;
        ">
            <h3 style="margin: 0 0 1rem 0;">🌾 {crop_name}</h3>
            <p style="margin: 0.5rem 0;"><strong>Batch ID:</strong></p>
            <p style="font-family: monospace; font-size: 1.1rem; margin: 0;">{batch_id}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Download button
        st.download_button(
            label="📱 Download QR Code",
            data=base64.b64decode(img_str),
            file_name=f"qr_code_{batch_id}.png",
            mime="image/png",
            use_container_width=True
        )

def scan_qr_interface():
    """Interface for QR code scanning simulation"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin: 1rem 0;
    ">
        <h2 style="margin: 0 0 1rem 0;">📱 QR Code Scanner</h2>
        <p style="margin: 0;">Enter batch ID or use camera to scan QR code</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Manual input option
    batch_id = st.text_input("🔍 Enter Batch ID", placeholder="e.g., BATCH_ABC12345")
    
    # Simulated camera input
    st.markdown("### 📸 Or use camera to scan")
    
    # Camera input simulation
    uploaded_file = st.file_uploader("Upload QR Code Image", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded QR Code", width=300)
        
        # Simulate QR detection
        st.info("🔍 Analyzing QR code... (This is a simulation)")
        
        # For demo purposes, extract batch ID from filename or show input
        if batch_id:
            return batch_id
    
    return batch_id if batch_id else None
