import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),  # Ensure it's fetching the correct password
    'database': os.getenv('MYSQL_DATABASE', 'store_db')
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def get_table_schema():
    """Fetch table structures dynamically to ensure valid SQL queries."""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SHOW TABLES")
    tables = [table["Tables_in_" + DB_CONFIG["database"]] for table in cursor.fetchall()]
    
    schema = {}
    for table in tables:
        cursor.execute(f"DESC {table}")
        schema[table] = [col["Field"] for col in cursor.fetchall()]

    db.close()
    return schema
