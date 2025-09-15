import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def create_sales_chart(data):
    """Create sales bar chart"""
    if not data:
        st.info("No sales data available")
        return
    
    df = pd.DataFrame(data)
    
    fig = px.bar(
        df, 
        x='date', 
        y='amount',
        title='Daily Sales Overview',
        color_discrete_sequence=['#22c55e']
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#1f2937',
        title_font_size=20
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_pie_chart(data, title, color_sequence=None):
    """Create pie chart for analytics"""
    if not data:
        st.info(f"No data available for {title}")
        return
    
    if color_sequence is None:
        color_sequence = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6']
    
    fig = px.pie(
        values=list(data.values()),
        names=list(data.keys()),
        title=title,
        color_discrete_sequence=color_sequence
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#1f2937',
        title_font_size=20
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_line_chart(data, x_col, y_col, title):
    """Create line chart"""
    if not data:
        st.info(f"No data available for {title}")
        return
    
    df = pd.DataFrame(data)
    
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        title=title,
        color_discrete_sequence=['#22c55e']
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#1f2937',
        title_font_size=20
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_metric_cards(metrics):
    """Create metric cards"""
    cols = st.columns(len(metrics))
    
    for i, (title, value, delta) in enumerate(metrics):
        with cols[i]:
            st.metric(
                label=title,
                value=value,
                delta=delta
            )

def create_analytics_overview(total_users, total_crops, total_payments, pending_deliveries):
    """Create analytics overview cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            color: white;
        ">
            <h3 style="margin: 0; font-size: 2rem;">{total_users}</h3>
            <p style="margin: 0.5rem 0 0 0;">👥 Total Users</p>
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
            <h3 style="margin: 0; font-size: 2rem;">{total_crops}</h3>
            <p style="margin: 0.5rem 0 0 0;">🌾 Total Crops</p>
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
            <h3 style="margin: 0; font-size: 2rem;">₹{total_payments:,.0f}</h3>
            <p style="margin: 0.5rem 0 0 0;">💰 Total Payments</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            color: white;
        ">
            <h3 style="margin: 0; font-size: 2rem;">{pending_deliveries}</h3>
            <p style="margin: 0.5rem 0 0 0;">🚚 Pending Deliveries</p>
        </div>
        """, unsafe_allow_html=True)
