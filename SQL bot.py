import streamlit as st
import pymysql
import groq  # Correct import for Groq API

# Set up the Groq API Key directly (Replace with your actual API key)
groq_api_key = "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"  # Replace with your actual key

# Function to connect to the database
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

# Function to execute SQL query
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

# Sidebar for input and results
with st.sidebar:
    st.header("⚙️ Database Configuration")
    database_name = st.text_input("📂 Enter Database Name:", "practice")
    st.markdown("---")
    st.header("📊 Query Execution Results")

# Main content area
query = st.text_area("📝 Enter SQL Query:")
prompt = st.text_area("🤖 Describe SQL Query (AI-Generated):")

if st.button("🚀 Connect to Database"):
    db = connect_to_db(database_name)
    if db:
        st.sidebar.success(f"✅ Connected to database: `{database_name}`")

if st.button("🔎 Execute Query"):
    if database_name and query:
        db = connect_to_db(database_name)
        if db:
            columns, result = execute_query(db, query)
            if columns:
                # Display result in main content
                st.write("### 🟢 Query Results")
                st.dataframe(result, columns=columns)

                # Display result in sidebar
                st.sidebar.write("### 📊 Query Results")
                st.sidebar.dataframe(result, columns=columns)
            else:
                st.success(result)
                st.sidebar.success(result)
    else:
        st.warning("⚠️ Please enter a database name and query.")

if st.button("🤖 Generate SQL Query using AI"):
    if database_name and prompt:
        generated_sql = generate_sql_from_prompt(database_name, prompt)
        st.text_area("📜 Generated SQL Query:", generated_sql, height=100)
    else:
        st.warning("⚠️ Please enter a database name and a description.")
