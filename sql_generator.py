import google.generativeai as genai
import os
import re
from dotenv import load_dotenv
from database import get_table_schema

# Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY is missing! Add it to your .env file.")

genai.configure(api_key=api_key)

def clean_sql_response(response_text: str) -> str:
    """Cleans the AI-generated SQL response."""
    if not response_text:
        return "Error: Empty response from AI"

    # Remove markdown/code formatting like ```sql and ```
    return re.sub(r"```sql\s*|\s*```", "", response_text, flags=re.MULTILINE).strip()

def generate_sql(question: str) -> str:
    """Generates a valid SQL query using Google Gemini AI."""
    schema = get_table_schema()

    schema_info = "\n".join(
        [f"Table `{table}`: Columns {', '.join(cols)}" for table, cols in schema.items()]
    )

    prompt = f"""
    Convert the following natural language question into a valid MySQL query.

    **Question:** {question}

    **Database Schema:**
    {schema_info}

    **Guidelines:**
    - Use correct table and column names.
    - Use `JOIN` when needed (avoid unnecessary joins).
    - Use `WHERE` for filtering, `COUNT()` for counting, and `SUM()` for totals.
    - If the question mentions "bar chart", "plot", or "graph", return at least one **numeric column** like `stock`, `price`, or `quantity` so it can be used to generate a chart.
    - Do NOT use string-based tricks like `REPEAT('*', stock)` when a bar chart or graph is requested.
    - Return **only the SQL query**, without Markdown or code block formatting.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        sql_query = response.text if hasattr(response, "text") else "Error: No valid response from AI"

        return clean_sql_response(sql_query)
    except Exception as e:
        return f"Error generating SQL: {str(e)}"
