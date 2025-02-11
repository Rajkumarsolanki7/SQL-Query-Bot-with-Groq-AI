import streamlit as st
import pymysql
import pandas as pd
import groq  # Correct import for Groq API

# Set up the Groq API Key directly (Replace with your actual API key)
groq_api_key = "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"  # Replace with your actual key

# Function to connect to MySQL Server (without specifying a database)
def connect_to_server():
    try:
        db = pymysql.connect(
            host="localhost",
            user="root",
            password="ROOT"
        )
        return db
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

# Function to fetch all available databases
def get_databases():
    db = connect_to_server()
    if db:
        cursor = db.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        db.close()
        return databases
    return []

# Function to connect to a specific database
def connect_to_db(database_name):
    try:
        db = pymysql.connect(
            host="localhost",
            user="root",
            password="ROOT",
            database=database_name
        )
        return db
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

# Function to fetch tables from a selected database
def get_tables(database_name):
    db = connect_to_db(database_name)
    if db:
        cursor = db.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        db.close()
        return tables
    return []

# Function to execute SQL queries
def execute_query(db, query):
    try:
        cursor = db.cursor()
        cursor.execute(query)

        if query.strip().lower().startswith("select"):
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]  # Get column names
            return columns, data
        else:
            db.commit()
            return None, "✅ Query executed successfully"
    except Exception as e:
        return None, f"❌ Error: {e}"

# Function to generate SQL using Groq API
def generate_sql_from_prompt(database_name, prompt):
    client = groq.Client(api_key=groq_api_key)  # Initialize Groq Client
    response = client.chat.completions.create(
        model="llama3-70b-8192",  # Best Groq model for SQL queries
        messages=[
            {"role": "system", "content": f"You are an SQL expert. Generate an SQL query for a MySQL database named {database_name}."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# Streamlit UI
st.set_page_config(page_title="SQL Query Bot", layout="wide")
st.title("🔍 SQL Query Bot with Groq AI")

# Sidebar - Database Selection
with st.sidebar:
    st.header("⚙️ Database Configuration")
    
    # Fetch database list and show dropdown
    databases = get_databases()
    if databases:
        database_name = st.selectbox("📂 Select Database:", databases)
    else:
        database_name = None
        st.warning("⚠️ No databases found. Check your MySQL connection.")

    # Fetch table list based on the selected database
    if database_name:
        tables = get_tables(database_name)
        if tables:
            table_name = st.selectbox("🗂 Select Table:", tables)
        else:
            table_name = None
            st.warning("⚠️ No tables found in the selected database.")

    st.markdown("---")
    st.header("📊 Query Execution Results")

# Main content area
query = st.text_area("📝 Enter SQL Query:")
prompt = st.text_area("🤖 Describe SQL Query (AI-Generated):")

# Store query history in session state
if "query_history" not in st.session_state:
    st.session_state.query_history = []

if st.button("🔎 Execute Query"):
    if database_name and query:
        db = connect_to_db(database_name)
        if db:
            columns, result = execute_query(db, query)
            if columns:
                # Convert result to DataFrame before displaying
                df = pd.DataFrame(result, columns=columns)
                st.write("### 🟢 Query Results")
                st.dataframe(df)  # Corrected line

                # Store query in history
                st.session_state.query_history.append((query, df))
            else:
                st.success(result)
    else:
        st.warning("⚠️ Please select a database and enter a query.")


# Display query history
if st.session_state.query_history:
    st.write("### 📜 Query History")
    for i, (q, res) in enumerate(st.session_state.query_history):
        st.write(f"**Query {i+1}:** `{q}`")
        st.dataframe(res)

if st.button("🤖 Generate SQL Query using AI"):
    if database_name and prompt:
        generated_sql = generate_sql_from_prompt(database_name, prompt)
        st.text_area("📜 Generated SQL Query:", generated_sql, height=100)
    else:
        st.warning("⚠️ Please select a database and enter a description.")
