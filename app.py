import streamlit as st
import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# Simple, readable connection handling with safe foreign key pragmas.
# -----------------------------------------------------------------------------
def get_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect("foodpanda.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def run_select_query(query, params=()):
    """Runs a SELECT query and returns the results as a Pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def execute_insert(query, params=()):
    """Executes INSERT operations safely and commits changes."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

# -----------------------------------------------------------------------------
# APP CONFIGURATION & SIDEBAR
# -----------------------------------------------------------------------------
st.set_page_config(page_title="CS160 Foodpanda Logistics", layout="wide")

st.title("🍔 Foodpanda: Cloud Kitchen & Rider Logistics")
st.subheader("CS160 Database Systems Project")
st.write("---")

# Simple beginner-friendly sidebar controls
st.sidebar.header("Navigation")
menu = st.sidebar.radio(
    "Choose an Option:",
    ["View Raw Tables", "Run Rubric Queries", "Add Customer", "Place Order"]
)

# -----------------------------------------------------------------------------
# VIEW 1: INSPECT RAW DATABASE TABLES
# -----------------------------------------------------------------------------
if menu == "View Raw Tables":
    st.header("🗂️ Inspect Database Tables")
    
    table_choice = st.selectbox(
        "Select Table to View:",
        ["Customer", "Customer_Contact", "Rider", "Rider_Contact", 
         "Saved_Address", "Restaurant", "Menu_Item", "Order_Record", 
         "Live_Tracking", "Order_Details"]
    )
    
    # Executing direct query matching the selected table name
    query = f"SELECT * FROM {table_choice}"
    df_table = run_select_query(query)
    
    st.dataframe(df_table, use_container_width=True)
    st.caption(f"Showing raw records straight from the '{table_choice}' table.")

# -----------------------------------------------------------------------------
# VIEW 2: REQUIRED RUBRIC QUERIES
# -----------------------------------------------------------------------------
elif menu == "Run Rubric Queries":
    st.header("📊 Required Course Rubric Queries")
    
    # Query A: Basic SELECT
    st.subheader("A. Basic SELECT: Active Riders")
    query_a = """
        SELECT Rider_ID, Full_Name, Vehicle_Reg, Shift_Status 
        FROM Rider 
        WHERE Shift_Status = 'active';
    """
    df_a = run_select_query(query_a)
    st.code(query_a, language="sql")
    st.dataframe(df_a)
    
    st.write("---")
    
    # Query B: JOIN Query
    st.subheader("B. JOIN Query: Complete Order Receipt")
    order_ids_df = run_select_query("SELECT Order_ID FROM Order_Record")
    
    if not order_ids_df.empty:
        selected_order = st.selectbox("Select Order ID to inspect receipt:", order_ids_df['Order_ID'])
        
        query_b = """
            SELECT 
                o.Order_ID,
                c.Full_Name AS Customer_Name,
                r.Full_Name AS Rider_Name,
                o.Order_Status,
                o.Total_Amount,
                o.Order_Time
            FROM Order_Record o
            JOIN Customer c ON o.Customer_ID = c.Customer_ID
            JOIN Rider r ON o.Rider_ID = r.Rider_ID
            WHERE o.Order_ID = ?;
        """
        df_b = run_select_query(query_b, (selected_order,))
        st.code(query_b, language="sql")
        st.table(df_b)
    
    st.write("---")
    
    # Query C: AGGREGATE Query
    st.subheader("C. AGGREGATE Query: Total Restaurant Revenue")
    query_c = """
        SELECT 
            r.Restaurant_ID,
            r.Rest_Name,
            SUM(od.Quantity * m.Price) AS Total_Revenue
        FROM Restaurant r
        JOIN Menu_Item m ON r.Restaurant_ID = m.Restaurant_ID
        JOIN Order_Details od ON m.Item_ID = od.Item_ID
        GROUP BY r.Restaurant_ID, r.Rest_Name
        ORDER BY Total_Revenue DESC;
    """
    df_c = run_select_query(query_c)
    st.code(query_c, language="sql")
    st.dataframe(df_c)

# -----------------------------------------------------------------------------
# VIEW 3: SIMPLE FORM - ADD CUSTOMER
# Demonstrates inserting data and maintaining 3NF separation.
# -----------------------------------------------------------------------------
elif menu == "Add Customer":
    st.header("👤 Register New Customer")
    st.write("Inserts a customer and their primary contact number into separate tables (3NF).")
    
    with st.form("new_customer_form", clear_on_submit=True):
        name = st.text_input("Full Name*")
        email = st.text_input("Email Address*")
        phone = st.text_input("Primary Phone Number* (e.g. 0300-1234567)")
        balance = st.number_input("Starting Wallet Balance (PKR)", min_value=0.0, value=500.0, step=100.0)
        
        submitted = st.form_submit_button("Save Customer")
        
        if submitted:
            if name and email and phone:
                try:
                    # Insert into independent Customer table
                    cust_query = "INSERT INTO Customer (Full_Name, Email, Wallet_Balance) VALUES (?, ?, ?)"
                    new_cust_id = execute_insert(cust_query, (name, email, balance))
                    
                    # Insert into dependent Contact table to satisfy 3NF
                    contact_query = "INSERT INTO Customer_Contact (Customer_ID, Phone_Number, Contact_Type) VALUES (?, ?, 'primary')"
                    execute_insert(contact_query, (new_cust_id, phone))
                    
                    st.success(f"Customer registered successfully! Assigned Customer ID: {new_cust_id}")
                except sqlite3.IntegrityError:
                    st.error("Error: This email address is already registered.")
            else:
                st.warning("Please fill out all required fields marked with an asterisk (*).")

# -----------------------------------------------------------------------------
# VIEW 4: SIMPLE FORM - PLACE BASIC ORDER
# Demonstrates basic FK selection and single table insertion.
# -----------------------------------------------------------------------------
elif menu == "Place Order":
    st.header("🛵 Place a Basic Order")
    
    # Fetch lists for clean dropdown selections
    customers = run_select_query("SELECT Customer_ID, Full_Name FROM Customer")
    riders = run_select_query("SELECT Rider_ID, Full_Name FROM Rider WHERE Shift_Status = 'active'")
    
    if customers.empty or riders.empty:
        st.error("Cannot place orders without customers and active riders in the database.")
    else:
        with st.form("new_order_form", clear_on_submit=True):
            # Create readable options mapping ID -> Name
            cust_options = dict(zip(customers['Customer_ID'], customers['Full_Name']))
            rider_options = dict(zip(riders['Rider_ID'], riders['Full_Name']))
            
            selected_cust = st.selectbox("Select Customer:", customers['Customer_ID'], format_func=lambda x: f"{x} - {cust_options[x]}")
            selected_rider = st.selectbox("Assign Active Rider:", riders['Rider_ID'], format_func=lambda x: f"{x} - {rider_options[x]}")
            total = st.number_input("Total Amount (PKR)", min_value=50.0, max_value=20000.0, value=850.0, step=50.0)
            
            submitted = st.form_submit_button("Confirm Order")
            
            if submitted:
                order_query = "INSERT INTO Order_Record (Customer_ID, Rider_ID, Total_Amount, Order_Status) VALUES (?, ?, ?, 'pending')"
                new_ord_id = execute_insert(order_query, (selected_cust, selected_rider, total))
                
                # Auto-generate a dummy live tracking session to respect the 1:1 constraint
                track_query = "INSERT INTO Live_Tracking (Order_ID, Estimated_Arrival, Ping_Status) VALUES (?, datetime('now', '+45 minutes'), 'active')"
                execute_insert(track_query, (new_ord_id,))
                
                st.success(f"Order #{new_ord_id} successfully created and linked to tracking!")