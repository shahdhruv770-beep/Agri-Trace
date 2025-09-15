# AgriTrace - Farm to Table Traceability System

## Overview

AgriTrace is a comprehensive farm-to-table traceability platform built with Streamlit that enables tracking of agricultural products from farm to consumer. The system supports multiple stakeholder roles including farmers, distributors, retailers, buyers, and administrators, each with specialized dashboards and functionalities. The platform provides QR code-based product tracking, payment management, supply chain visibility, and comprehensive analytics for agricultural supply chain management.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application with custom CSS styling
- **UI Components**: Modular component-based architecture with reusable elements for navigation, charts, and QR code generation
- **Styling**: Custom CSS with gradient backgrounds, card-based layouts, and responsive design patterns
- **User Interface**: Role-based dashboards with sidebar navigation and dynamic page rendering

### Backend Architecture
- **Application Structure**: Monolithic Python application with modular page and component organization
- **Authentication**: Hash-based password authentication using SHA256 with session state management
- **Database Layer**: PostgreSQL integration with direct SQL queries using psycopg2 and connection pooling
- **API Design**: Function-based data access layer with execute_query and fetch_one utility functions

### Data Storage
- **Primary Database**: PostgreSQL with environment-based configuration
- **Schema Design**: Relational database with tables for users, crops, deliveries, and payments
- **Data Models**: User roles (Farmer, Distributor, Retailer, Buyer, Admin), crop lifecycle tracking, and payment transaction records

### Core Features
- **Traceability System**: QR code generation and scanning for batch tracking throughout the supply chain
- **Role-Based Access Control**: Distinct dashboard experiences based on user roles with appropriate feature access
- **Payment Management**: Transaction tracking between stakeholders with payment status monitoring
- **Supply Chain Visibility**: End-to-end tracking from farm production to consumer purchase
- **Analytics Dashboard**: Data visualization using Plotly for sales trends, user distribution, and system metrics

### Security Model
- **Authentication**: Session-based authentication with password hashing
- **Authorization**: Role-based access control limiting feature access based on user type
- **Data Protection**: Environment variable configuration for database credentials

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework for the user interface
- **psycopg2**: PostgreSQL database adapter for Python
- **Pillow (PIL)**: Image processing for QR code generation and manipulation
- **qrcode**: QR code generation library for product traceability
- **plotly**: Interactive data visualization and charting library
- **pandas**: Data manipulation and analysis for analytics features

### Database
- **PostgreSQL**: Primary relational database for all application data
- **Connection Management**: Environment-based configuration using PGHOST, PGDATABASE, PGUSER, PGPASSWORD, and PGPORT variables

### Utilities
- **hashlib**: SHA256 password hashing for user authentication
- **uuid**: Unique identifier generation for batch IDs and tracking
- **base64**: Image encoding for QR code downloads and display
- **datetime**: Date and time handling for crop harvesting, deliveries, and payment timestamps

### Development Environment
- **Python Runtime**: Core application runtime environment
- **Environment Variables**: Configuration management for database connections and application settings