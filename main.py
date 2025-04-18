from fastapi import FastAPI
from database import get_db_connection
from sql_generator import generate_sql
import schemas

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI SQL chatbot with Graph support!"}

@app.post("/query", response_model=schemas.QueryResponse)
async def query_database(query: schemas.QueryRequest):
    sql_query = generate_sql(query.question)
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
        
        # Check if the result is plotable
        columns = cursor.column_names
        is_plotable = False
        if result and len(columns) >= 2:
            # Ensure first column is categorical, others numeric
            try:
                float(result[0][columns[1]])
                is_plotable = True
            except:
                pass
    except Exception as e:
        result = {"error": str(e)}
        columns = []
        is_plotable = False

    db.close()
    return {
        "sql_query": sql_query,
        "result": result,
        "columns": columns,
        "is_plotable": is_plotable
    }
