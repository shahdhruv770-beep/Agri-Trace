import psycopg2
import os
from psycopg2.extras import RealDictCursor
import streamlit as st

def get_connection():
    """Get database connection using environment variables"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("PGHOST"),
            database=os.getenv("PGDATABASE"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            port=os.getenv("PGPORT", 5432)
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        return None

def init_database():
    """Initialize database tables"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20),
                role VARCHAR(50) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crops table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crops (
                id SERIAL PRIMARY KEY,
                farmer_id INTEGER REFERENCES users(id),
                name VARCHAR(255) NOT NULL,
                type VARCHAR(100) NOT NULL,
                quantity DECIMAL(10,2) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                harvest_date DATE,
                batch_id VARCHAR(100) UNIQUE NOT NULL,
                status VARCHAR(50) DEFAULT 'available',
                photo_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                crop_id INTEGER REFERENCES crops(id),
                from_user_id INTEGER REFERENCES users(id),
                to_user_id INTEGER REFERENCES users(id),
                transaction_type VARCHAR(50) NOT NULL,
                amount DECIMAL(10,2),
                status VARCHAR(50) DEFAULT 'pending',
                transport_details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Payments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                amount DECIMAL(10,2) NOT NULL,
                from_user_id INTEGER REFERENCES users(id),
                to_user_id INTEGER REFERENCES users(id),
                crop_id INTEGER REFERENCES crops(id),
                payment_status VARCHAR(50) DEFAULT 'pending',
                payment_method VARCHAR(50),
                transaction_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Traceability table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traceability (
                id SERIAL PRIMARY KEY,
                batch_id VARCHAR(100) NOT NULL,
                step_type VARCHAR(50) NOT NULL,
                user_id INTEGER REFERENCES users(id),
                location VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT,
                status VARCHAR(50) DEFAULT 'active'
            )
        """)
        
        # Deliveries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deliveries (
                id SERIAL PRIMARY KEY,
                crop_id INTEGER REFERENCES crops(id),
                distributor_id INTEGER REFERENCES users(id),
                retailer_id INTEGER REFERENCES users(id),
                transport_details TEXT,
                delivery_date DATE,
                status VARCHAR(50) DEFAULT 'in_transit',
                tracking_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Database initialization failed: {str(e)}")
        return False

def execute_query(query, params=None, fetch=False):
    """Execute database query"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        
        if fetch:
            result = cursor.fetchall()
        else:
            result = cursor.rowcount
            
        conn.commit()
        cursor.close()
        conn.close()
        return result
        
    except Exception as e:
        st.error(f"Query execution failed: {str(e)}")
        return None

def fetch_one(query, params=None):
    """Fetch single record"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
        
    except Exception as e:
        st.error(f"Query execution failed: {str(e)}")
        return None
